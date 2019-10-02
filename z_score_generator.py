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

DEFAULT_YEAR = 2018
N_PLAYERS_WITH_TOP_MPG = 300 # how many players want to retrieve based on minute per game
YFBR_STAT_NAME_MAP = {"FG%": ["FG", "FGA"], "FT%": ["FT", "FTA"], "3PTM": ["3P"], "3PT%": ["3P", "3PA"], "PTS": ["PTS"], "REB": ["TRB"], "OREB": ["ORB"], "AST": ["AST"], "ST": ["STL"], "BLK": ["BLK"], "TO": ["TOV"], "A/T": ["AST", "TOV"], "G": ["G"] }

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

''' Retrieve league data in Yahoo Fantasy Basketball '''

sc = OAuth2(None, None, from_file="oauth2.json")
game = yfa.Game(sc, "nba")
input_year = input("What year [default: {}]: ".format(DEFAULT_YEAR)) or DEFAULT_YEAR
year = int(input_year)
league_id_list = game.league_ids(year=year)
message = "Which league "
for i in range(len(league_id_list)):
  message += "{{{}: {}}} ".format(i, league_id_list[i])
message += "[default: 0]: "
input_id = input(message) or "0"
league_id = league_id_list[int(input_id)]
league = game.to_league(league_id)

''' Import basketball reference player total stats '''

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

br_stats = pd.DataFrame(player_stats, columns = headers)
br_stats = br_stats.dropna()
br_stats.drop_duplicates(subset = "Player", inplace = True)
br_stats["Player"] = br_stats["Player"].apply(lambda x: _formalize_name(x))
br_stats.set_index("Player", inplace=True)
br_stats["MP/G"] = br_stats["MP"].astype(float) / br_stats["G"].astype(float)
br_stats = br_stats.sort_values(by=['MP/G'], ascending=False)
br_stats = br_stats.head(N_PLAYERS_WITH_TOP_MPG)
br_stats = br_stats.sort_index()

''' Retrieve league stat categories and calculate league average and standard deviation using Basketball reference '''

league_total_games = 0;
league_total_stats = {}
league_average_stats = {}
league_standard_deviation = {}
league_stat_category_list = []

for stat_category in league.stat_categories():
  league_stat_category_list.append(stat_category["display_name"])
league_stat_category_list += ["G"]

# league total stats
player_average_stat_list = {}
for stat_category in league_stat_category_list:
  for br_stat_name in YFBR_STAT_NAME_MAP[stat_category]:
    player_average_stat_list[br_stat_name] = []
    league_total_stats[br_stat_name] = 0;
    for index, row in br_stats.iterrows():
      league_total_stats[br_stat_name] += float(row[br_stat_name])
      player_average_stat_list[br_stat_name].append(float(row[br_stat_name]) / float(row["G"]))
for index, row in br_stats.iterrows():
  league_total_games += float(row["G"])

# league average stats
league_average_stats = {k: v / league_total_games for k, v in league_total_stats.items()}

# league standard deviation
for stat_category in league_stat_category_list:
  br_stat_name_list = YFBR_STAT_NAME_MAP[stat_category]
  if len(br_stat_name_list) == 1:
    league_standard_deviation[br_stat_name_list[0]] = stdev(player_average_stat_list[br_stat_name_list[0]])
  elif len(br_stat_name_list) == 2:
    stdev_temp_list = []
    league_average = league_average_stats[br_stat_name_list[0]] / league_average_stats[br_stat_name_list[1]]
    for i in range(len(player_average_stat_list[br_stat_name_list[0]])):
      player_average = 0 if player_average_stat_list[br_stat_name_list[1]][i] == 0 else player_average_stat_list[br_stat_name_list[0]][i] / player_average_stat_list[br_stat_name_list[1]][i]
      d = player_average - league_average
      m = d * player_average_stat_list[br_stat_name_list[1]][i]
      stdev_temp_list.append(m)
    league_standard_deviation[stat_category] = stdev(stdev_temp_list)
    league_average_stats[stat_category] = mean(stdev_temp_list)

''' Create my_player_struct for player's total, average and z-score from Basketball reference '''

my_player_struct = {}
for index, row in br_stats.iterrows():
  player_name = _formalize_name(index)
  my_player_struct[player_name] = {}
  my_player_struct[player_name]["total_stats"] = {}
  my_player_struct[player_name]["average_stats"] = {}
  my_player_struct[player_name]["z_scores"] = {}

  # player total stats
  for stat_category in league_stat_category_list:
    br_stat_name_list = YFBR_STAT_NAME_MAP[stat_category]
    for br_stat_name in br_stat_name_list:
      my_player_struct[player_name]["total_stats"][br_stat_name] = float(row[br_stat_name])

  # player average stats
  for stat_category in league_stat_category_list:
      br_stat_name_list = YFBR_STAT_NAME_MAP[stat_category]
      if stat_category is "G":
        continue
      if len(br_stat_name_list) == 1:
        my_player_struct[player_name]["average_stats"][br_stat_name_list[0]] = my_player_struct[player_name]["total_stats"][br_stat_name_list[0]] / my_player_struct[player_name]["total_stats"]["G"]
      elif len(br_stat_name_list) == 2:
        my_player_struct[player_name]["average_stats"][br_stat_name_list[0]] = my_player_struct[player_name]["total_stats"][br_stat_name_list[0]] / my_player_struct[player_name]["total_stats"][br_stat_name_list[1]]

  # player z-scores
  for stat_category in league_stat_category_list:
      br_stat_name_list = YFBR_STAT_NAME_MAP[stat_category]
      if stat_category is "G":
        continue
      if len(br_stat_name_list) == 1:
        o = my_player_struct[player_name]["total_stats"][br_stat_name_list[0]] / my_player_struct[player_name]["total_stats"]["G"]
        m = league_average_stats[br_stat_name_list[0]]
        s = league_standard_deviation[br_stat_name_list[0]]
        if br_stat_name_list[0] is "TOV":
          my_player_struct[player_name]["z_scores"][br_stat_name_list[0]] = 0 - ((o - m) / s)
        else:
          my_player_struct[player_name]["z_scores"][br_stat_name_list[0]] = (o - m) / s
      elif len(br_stat_name_list) == 2:
        league_average = league_total_stats[br_stat_name_list[0]] / league_total_stats[br_stat_name_list[1]]
        player_average = 0 if my_player_struct[player_name]["total_stats"][br_stat_name_list[1]] == 0 else my_player_struct[player_name]["total_stats"][br_stat_name_list[0]] / my_player_struct[player_name]["total_stats"][br_stat_name_list[1]]
        o = (player_average - league_average) * (my_player_struct[player_name]["total_stats"][br_stat_name_list[1]] / my_player_struct[player_name]["total_stats"]["G"])
        m = league_average_stats[stat_category]
        s = league_standard_deviation[stat_category]
        my_player_struct[player_name]["z_scores"][stat_category] = (o - m) / s

''' Create my_team_struct, parse roster from Yahoo Fantasy API and copy player data from my_player_struct '''

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
  for stat_category in league_stat_category_list:
    for br_stat_name in YFBR_STAT_NAME_MAP[stat_category]:
      my_team_total_stats[br_stat_name] = 0
      for key2, player in my_team["players"].items():
        my_team_total_stats[br_stat_name] += player["total_stats"][br_stat_name]
  my_team_struct[key]["total_stats"] = my_team_total_stats

# team average stats
for key, my_team in my_team_struct.items():
  my_team_average_stats = {}
  my_team_total_stats = my_team["total_stats"]
  for stat_category in league_stat_category_list:
    if stat_category is "G":
      continue
    br_stat_name_list = YFBR_STAT_NAME_MAP[stat_category]
    if len(br_stat_name_list) == 1:
      my_team_average_stats[stat_category] = my_team_total_stats[br_stat_name_list[0]] / my_team_total_stats["G"]
    elif len(br_stat_name_list) == 2:
      my_team_average_stats[stat_category] = my_team_total_stats[br_stat_name_list[0]] / my_team_total_stats[br_stat_name_list[1]]
  my_team_struct[key]["average_stats"] = my_team_average_stats

# team z-scores
for key, my_team in my_team_struct.items():
  my_team_z_scores = {}
  for stat_category in league_stat_category_list:
    if stat_category is "G":
      continue
    br_stat_name_list = YFBR_STAT_NAME_MAP[stat_category]
    index = br_stat_name_list[0] if len(br_stat_name_list) == 1 else stat_category if len(br_stat_name_list) == 2 else 0
    my_team_z_scores[index] = 0
    for key2, player in my_team["players"].items():
      my_team_z_scores[index] += player["z_scores"][index]

  my_team_struct[key]["z_scores"] = my_team_z_scores

''' Print result in CSV format '''

_create_csv_output_file("{}_{}_teams.csv".format(year, league_id), my_team_struct)
_create_csv_output_file("{}_{}_players.csv".format(year, league_id), my_player_struct)
