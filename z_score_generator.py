'''
z_score_generator
'''

from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import unidecode
from statistics import stdev, mean

N_PLAYERS_WITH_TOP_MPG = 300 # how many players want to retrieve based on minute per game
SUPPORTED_YEARS = [2018, 2017, 2016, 2015]
YFB_STAT_CATEGORIES = {"GP":   ["GP"],
                       "GS":   ["GS"],
                       "MIN":  ["MIN"],
                       "FGM":  ["FGM"],
                       "FGA":  ["FGA"],
                       "FG%":  ["FGM", "FGA"],
                       "FTM":  ["FTM"],
                       "FTA":  ["FTA"],
                       "FT%":  ["FTM", "FTA"],
                       "3PTM": ["3PTM"],
                       "3PTA": ["3PTA"],
                       "3PT%": ["3PTM", "3PTA"],
                       "PTS":  ["PTS"],
                       "DREB": ["DREB"],
                       "OREB": ["OREB"],
                       "REB":  ["REB"],
                       "AST":  ["AST"],
                       "ST":   ["ST"],
                       "BLK":  ["BLK"],
                       "TO":   ["TO"],
                       "A/T":  ["AST", "TO"],
                       "PF" :  ["PF"]}
BR_TO_YFB_STATS_NAME_MAP = {"G":   "GP",
                            "GS":  "GS",
                            "MP":  "MIN",
                            "FG":  "FGM",
                            "FGA": "FGA",
                            "FG%": "FG%",
                            "FT":  "FTM",
                            "FTA": "FTA",
                            "FT%": "FT%",
                            "3P":  "3PTM",
                            "3PA": "3PTA",
                            "3P%": "3PT%",
                            "PTS": "PTS",
                            "DRB": "DREB",
                            "ORB": "OREB",
                            "TRB": "REB",
                            "AST": "AST",
                            "STL": "ST",
                            "BLK": "BLK",
                            "TOV": "TO",
                            "PF":  "PF"}
def _formalize_name(name):
  name = unidecode.unidecode(name)
  name = name.replace(".", "").replace(" Jr", "").replace(" III", "")
  name = name.replace("Jakob Poltl", "Jakob Poeltl").replace("Taurean Waller-Prince", "Taurean Prince").replace("Moe Harkless", "Maurice Harkless")
  return name

def _create_csv_output_file(file_name, my_struct):
  f = open(file_name, "w+")
  print_header = True
  for key, item in my_struct.items():
    if print_header is True:
      f.write(",")
      for key2, item2 in item["average_stats"].items():
        f.write("{},".format(key2))
      for key2, item2 in item["z_scores"].items():
        f.write("z{},".format(key2))
      f.write("\n")
      print_header = False
    f.write("{},".format(key))
    for key2, item2 in item["average_stats"].items():
      f.write("{},".format(item2))
    for key2, item2 in item["z_scores"].items():
      f.write("{},".format(item2))
    f.write("\n")
  f.close()

def _divide(numerator, denominator):
  return float(numerator) / float(denominator) if float(denominator) != 0 else 0

def _create_player_stats_table(year):
  # URL page we will scraping (see image above)
  url = "https://www.basketball-reference.com/leagues/NBA_{}_totals.html".format(year + 1)
  # this is the HTML from the given URL
  html = urlopen(url)
  soup = BeautifulSoup(html, "lxml")
  # use findALL() to get the column headers
  soup.findAll('tr', limit=2)
  # use getText() to extract the text we need into a list
  headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
  # exclude the first column as we will not need the ranking order from Basketball Reference for the analysis
  headers = headers[1:]
  # avoid the first header row
  rows = soup.findAll('tr')[1:]
  player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

  br_stats_table = pd.DataFrame(player_stats, columns = headers)
  br_stats_table = br_stats_table.dropna()
  br_stats_table.drop_duplicates(subset = "Player", inplace = True)
  br_stats_table["Player"] = br_stats_table["Player"].apply(lambda x: _formalize_name(x))
  br_stats_table.set_index("Player", inplace=True)

  # rename table header with Yahoo fantasy basketball stats name
  for key, value in BR_TO_YFB_STATS_NAME_MAP.items():
    br_stats_table = br_stats_table.rename(columns={key: value})

  # filter players based on MPG
  br_stats_table["MPG"] = br_stats_table["MIN"].astype(float) / br_stats_table["GP"].astype(float)
  br_stats_table = br_stats_table.sort_values(by=['MPG'], ascending=False)
  br_stats_table = br_stats_table.head(N_PLAYERS_WITH_TOP_MPG)
  br_stats_table = br_stats_table.sort_index()

  return br_stats_table

def _create_my_league_struct(league):
  my_league_struct = {}
  my_league_struct["name"] = league.settings()["name"]
  my_league_struct["total_games"] = 0;
  my_league_struct["total_stats"] = {}
  my_league_struct["average_stats"] = {}
  my_league_struct["standard_deviation"] = {}
  my_league_struct["stat_category_list"] = []

  for stat_category in league.stat_categories():
    if YFB_STAT_CATEGORIES.get(stat_category["display_name"]) is not None:
      my_league_struct["stat_category_list"].append(stat_category["display_name"])
    else:
      print("{} is not supported yet and will be skipped".format(stat_category["display_name"]))
  my_league_struct["stat_category_list"] += ["GP"]

  # league total stats
  player_average_stat_list = {}
  for stat_category in my_league_struct["stat_category_list"]:
    for stat_name in YFB_STAT_CATEGORIES[stat_category]:
      player_average_stat_list[stat_name] = []
      my_league_struct["total_stats"][stat_name] = 0;
      for index, row in stats_table.iterrows():
        my_league_struct["total_stats"][stat_name] += float(row[stat_name])
        player_average_stat_list[stat_name].append(_divide(float(row[stat_name]), float(row["GP"])))
  for index, row in stats_table.iterrows():
    my_league_struct["total_games"] += float(row["GP"])

  # league average stats
  my_league_struct["average_stats"] = {k: v / my_league_struct["total_games"] for k, v in my_league_struct["total_stats"].items()}

  # league standard deviation
  for stat_category in my_league_struct["stat_category_list"]:
    stat_name_list = YFB_STAT_CATEGORIES[stat_category]
    if len(stat_name_list) == 1:
      my_league_struct["standard_deviation"][stat_category] = stdev(player_average_stat_list[stat_category])
    elif len(stat_name_list) == 2:
      stdev_temp_list = []
      league_average = _divide(my_league_struct["average_stats"][stat_name_list[0]], my_league_struct["average_stats"][stat_name_list[1]])
      for i in range(len(player_average_stat_list[stat_name_list[0]])):
        player_average = _divide(player_average_stat_list[stat_name_list[0]][i], player_average_stat_list[stat_name_list[1]][i])
        d = player_average - league_average
        m = d * player_average_stat_list[stat_name_list[1]][i]
        stdev_temp_list.append(m)
      my_league_struct["standard_deviation"][stat_category] = stdev(stdev_temp_list)
      my_league_struct["average_stats"][stat_category] = mean(stdev_temp_list)

  return my_league_struct

def _create_my_player_struct(my_league_struct):
  my_player_struct = {}
  for index, row in stats_table.iterrows():
    player_name = _formalize_name(index)
    my_player_struct[player_name] = {}
    my_player_struct[player_name]["total_stats"] = {}
    my_player_struct[player_name]["average_stats"] = {}
    my_player_struct[player_name]["z_scores"] = {}

    # player total stats
    for stat_category in my_league_struct["stat_category_list"]:
      for stat_name in YFB_STAT_CATEGORIES[stat_category]:
        my_player_struct[player_name]["total_stats"][stat_name] = float(row[stat_name])

    # player average stats
    for stat_category in my_league_struct["stat_category_list"]:
        stat_name_list = YFB_STAT_CATEGORIES[stat_category]
        if stat_category is "GP":
          continue
        if len(stat_name_list) == 1:
          my_player_struct[player_name]["average_stats"][stat_category] = _divide(my_player_struct[player_name]["total_stats"][stat_category], my_player_struct[player_name]["total_stats"]["GP"])
        elif len(stat_name_list) == 2:
          my_player_struct[player_name]["average_stats"][stat_category] = _divide(my_player_struct[player_name]["total_stats"][stat_name_list[0]], my_player_struct[player_name]["total_stats"][stat_name_list[1]])

    # player z-scores
    for stat_category in my_league_struct["stat_category_list"]:
        stat_name_list = YFB_STAT_CATEGORIES[stat_category]
        if stat_category is "GP":
          continue
        if len(stat_name_list) == 1:
          o = my_player_struct[player_name]["total_stats"][stat_category] / my_player_struct[player_name]["total_stats"]["GP"]
          m = my_league_struct["average_stats"][stat_category]
          s = my_league_struct["standard_deviation"][stat_category]
          if stat_category in {"TO", "PF"}:
            my_player_struct[player_name]["z_scores"][stat_category] = 0 - ((o - m) / s)
          else:
            my_player_struct[player_name]["z_scores"][stat_category] = (o - m) / s
        elif len(stat_name_list) == 2:
          league_average = my_league_struct["total_stats"][stat_name_list[0]] / my_league_struct["total_stats"][stat_name_list[1]]
          player_average = _divide(my_player_struct[player_name]["total_stats"][stat_name_list[0]], my_player_struct[player_name]["total_stats"][stat_name_list[1]])
          o = _divide((player_average - league_average) * my_player_struct[player_name]["total_stats"][stat_name_list[1]], my_player_struct[player_name]["total_stats"]["GP"])
          m = my_league_struct["average_stats"][stat_category]
          s = my_league_struct["standard_deviation"][stat_category]
          my_player_struct[player_name]["z_scores"][stat_category] = (o - m) / s

  return my_player_struct

def _create_my_team_struct(my_league_struct, my_player_struct):
  my_team_struct = {}
  for item in league.teams():
    team = league.to_team(item["team_key"])
    my_team = {}
    my_team["players"] = {}

    for player in team.roster(league.current_week()):
      player_name = _formalize_name(player["name"])
      if my_player_struct.get(player_name) is None:
        continue
      my_team["players"][player_name] = my_player_struct[player_name]

    my_team_struct[item["name"]] = my_team

  # team total stats
  for key, my_team in my_team_struct.items():
    my_team_total_stats = {}
    for stat_category in my_league_struct["stat_category_list"]:
      for stat_name in YFB_STAT_CATEGORIES[stat_category]:
        my_team_total_stats[stat_name] = 0
        for key2, player in my_team["players"].items():
          my_team_total_stats[stat_name] += player["total_stats"][stat_name]
    my_team_struct[key]["total_stats"] = my_team_total_stats

  # team average stats
  for key, my_team in my_team_struct.items():
    my_team_average_stats = {}
    my_team_total_stats = my_team["total_stats"]
    for stat_category in my_league_struct["stat_category_list"]:
      if stat_category is "GP":
        continue
      stat_name_list = YFB_STAT_CATEGORIES[stat_category]
      if len(stat_name_list) == 1:
        my_team_average_stats[stat_category] = _divide(my_team_total_stats[stat_category], my_team_total_stats["GP"])
      elif len(stat_name_list) == 2:
        my_team_average_stats[stat_category] = _divide(my_team_total_stats[stat_name_list[0]], my_team_total_stats[stat_name_list[1]])
    my_team_struct[key]["average_stats"] = my_team_average_stats

  # team z-scores
  for key, my_team in my_team_struct.items():
    my_team_z_scores = {}
    for stat_category in my_league_struct["stat_category_list"]:
      if stat_category is "GP":
        continue
      my_team_z_scores[stat_category] = 0
      for key2, player in my_team["players"].items():
        my_team_z_scores[stat_category] += player["z_scores"][stat_category]
    my_team_struct[key]["z_scores"] = my_team_z_scores

  return my_team_struct

def _print_options_and_get_input(name, my_list):
  message = "Choose a {} ".format(name)
  for index in range(len(my_list)):
    if name is "season":
      message += "{{{}: {}-{}}} ".format(index, my_list[index], my_list[index] + 1)
    elif name is "league":
      message += "{{{}: {}}} ".format(index, my_list[index][1])
  message += "[default: 0]: "
  input_id = input(message) or "0"
  while int(input_id) not in range(0, len(my_list)):
    input_id = input("Please enter an number between 0 to {}: ".format(len(my_list) - 1))

  return int(input_id)

''' Retrieve league data in Yahoo Fantasy Basketball '''

sc = OAuth2(None, None, from_file="oauth2.json")
game = yfa.Game(sc, "nba")

year = SUPPORTED_YEARS[_print_options_and_get_input("season", SUPPORTED_YEARS)]

league_id_name_pair_list = []
for item in game.league_ids(year=year):
  league_id_name_pair_list.append((item, game.to_league(item).settings()["name"]))
if not league_id_name_pair_list:
  print("No fantasy teams in {}-{} seasons...".format(year, year + 1))
  exit(0)

input_id = _print_options_and_get_input("league", league_id_name_pair_list)
league_id = league_id_name_pair_list[int(input_id)][0]
league_name = league_id_name_pair_list[int(input_id)][1]
league = game.to_league(league_id)

print("You select: Season: {}-{}, League: {} ".format(year, year + 1, league_name))

''' Import basketball reference player total stats '''

print("Parsing Basketball Reference {}-{} NBA players total stats ...".format(year, year + 1), end = " ", flush = True)
stats_table = _create_player_stats_table(year)
print("Done")

''' Retrieve league stat categories and calculate league average and standard deviation using Basketball reference '''

print("Retrieving league data ...", end = " ", flush = True)
my_league_struct = _create_my_league_struct(league)
print("Done")

''' Create my_player_struct for player's total, average and z-score from Basketball Reference '''

print("Calculating player performance ...", end = " ", flush = True)
my_player_struct = _create_my_player_struct(my_league_struct)
print("Done")

''' Create my_team_struct, parse roster from Yahoo Fantasy API and copy player data from my_player_struct '''

print("Calculating team performace ...", end = " ", flush = True)
my_team_struct = _create_my_team_struct(my_league_struct, my_player_struct)
print("Done")

''' Print result in CSV format '''

teams_csv_name = "{}-{}_{}_teams.csv".format(year, year + 1, my_league_struct["name"])
players_csv_name = "{}-{}_{}_players.csv".format(year, year + 1, my_league_struct["name"])
_create_csv_output_file(teams_csv_name, my_team_struct)
_create_csv_output_file(players_csv_name, my_player_struct)

print("Finished! please import \"{}\" and \"{}\" to excel as CSV format to see the results.".format(teams_csv_name, players_csv_name))
