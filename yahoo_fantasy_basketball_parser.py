'''
yahoo-fantasy-api examples
pip install yahoo-fantasy-api
https://pypi.org/project/yahoo-fantasy-api/
'''

from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import unidecode
from statistics import stdev, mean

YEAR = 2018
N_PLAYERS_WITH_TOP_MPG = 300 # how many players want to retrieve based on minute per game
YFBR_STAT_NAME_MAP = {"FG%": ["FG", "FGA"], "FT%": ["FT", "FTA"], "3PTM": ["3P"], "PTS": ["PTS"], "REB": ["TRB"], "AST": ["AST"], "ST": ["STL"], "BLK": ["BLK"], "TO": ["TOV"], "G": ["G"] }

def _formalize_name(name):
  name = unidecode.unidecode(name)
  name = name.replace(".", "").replace(" Jr", "").replace(" III", "")
  name = name.replace("Jakob Poltl", "Jakob Poeltl").replace("Taurean Waller-Prince", "Taurean Prince").replace("Moe Harkless", "Maurice Harkless")
  return name

''' Import basketball reference player total stats '''

# URL page we will scraping (see image above)
url = "https://www.basketball-reference.com/leagues/NBA_{}_totals.html".format(YEAR + 1)
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

''' Retrieve league data in Yahoo Fantasy Basketball '''

sc = OAuth2(None, None, from_file="oauth2.json")
game = yfa.Game(sc, "nba")
league_ids = game.league_ids(year=YEAR)
league_id = input("Which league {} [0] : ".format(league_ids)) or "0"
league_id = int(league_id)
league = game.to_league(league_ids[league_id])

''' Retrieve league stat categories and calculate league average and standard deviation using Basketball reference '''

league_total_games = 0;
league_total_stats = {}
league_average_stats = {}
league_standard_deviation = {}
league_stat_categories = []

for stat_category in league.stat_categories():
  league_stat_categories.append(stat_category["display_name"])
league_stat_categories += ["G"]

# league total stats
player_average_stat_list = {}
for stat_category in league_stat_categories:
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
for stat_category in league_stat_categories:
  br_stat_names = YFBR_STAT_NAME_MAP[stat_category]
  if len(br_stat_names) == 1:
    league_standard_deviation[br_stat_names[0]] = stdev(player_average_stat_list[br_stat_names[0]])
  elif len(br_stat_names) == 2:
    stdev_temp_list = []
    league_average = league_average_stats[br_stat_names[0]] / league_average_stats[br_stat_names[1]]
    for i in range(len(player_average_stat_list[br_stat_names[0]])):
      d = (player_average_stat_list[br_stat_names[0]][i] / player_average_stat_list[br_stat_names[1]][i]) - league_average
      m = d * player_average_stat_list[br_stat_names[1]][i]
      stdev_temp_list.append(m)
    league_standard_deviation[stat_category] = stdev(stdev_temp_list)
    league_average_stats[stat_category] = mean(stdev_temp_list)

''' Create my_player_struct for player's total stats and z-score from Basketball reference '''

my_player_struct = {}
for index, row in br_stats.iterrows():
  player_name = _formalize_name(index)
  my_player_struct[player_name] = {}
  my_player_struct[player_name]["total_stats"] = {}
  my_player_struct[player_name]["z_scores"] = {}

  # player total stats
  for stat_category in league_stat_categories:
    br_stat_names = YFBR_STAT_NAME_MAP[stat_category]
    for br_stat_name in br_stat_names:
      my_player_struct[player_name]["total_stats"][br_stat_name] = float(row[br_stat_name])

  # player z-scores
  for stat_category in league_stat_categories:
      br_stat_names = YFBR_STAT_NAME_MAP[stat_category]
      if stat_category is "G":
        continue
      if len(br_stat_names) == 1:
        o = my_player_struct[player_name]["total_stats"][br_stat_names[0]] / my_player_struct[player_name]["total_stats"]["G"]
        m = league_average_stats[br_stat_names[0]]
        s = league_standard_deviation[br_stat_names[0]]
        if br_stat_names[0] is "TOV":
          my_player_struct[player_name]["z_scores"][br_stat_names[0]] = 0 - ((o - m) / s)
        else:
          my_player_struct[player_name]["z_scores"][br_stat_names[0]] = (o - m) / s
      elif len(br_stat_names) == 2:
        league_average = league_total_stats[br_stat_names[0]] / league_total_stats[br_stat_names[1]]
        o = ((my_player_struct[player_name]["total_stats"][br_stat_names[0]] / my_player_struct[player_name]["total_stats"][br_stat_names[1]]) - league_average) * (my_player_struct[player_name]["total_stats"][br_stat_names[1]] / my_player_struct[player_name]["total_stats"]["G"])
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
  for stat_category in league_stat_categories:
    for br_stat_name in YFBR_STAT_NAME_MAP[stat_category]:
      my_team_total_stats[br_stat_name] = 0
      for key2, player in my_team["players"].items():
        my_team_total_stats[br_stat_name] += player["total_stats"][br_stat_name]
  my_team["total_stats"] = my_team_total_stats
  # print("{}\n {}\n".format(key, my_team["total_stats"]))

# team average stats
for key, my_team in my_team_struct.items():
  my_team_average_stats = {}
  my_team_total_stats = my_team["total_stats"]
  for stat_category in league_stat_categories:
    br_stat_names = YFBR_STAT_NAME_MAP[stat_category]
    if len(br_stat_names) == 1:
      my_team_average_stats[stat_category] = my_team_total_stats[br_stat_names[0]] / my_team_total_stats["G"]
    elif len(br_stat_names) == 2:
      my_team_average_stats[stat_category] = my_team_total_stats[br_stat_names[0]] / my_team_total_stats[br_stat_names[1]]
  my_team["average_stats"] = my_team_average_stats
  # print("{}\n {}\n".format(key, my_team["average_stats"]))

# team z-scores
for key, my_team in my_team_struct.items():
  my_team_z_scores = {}
  for stat_category in league_stat_categories:
    if stat_category is "G":
      continue
    br_stat_names = YFBR_STAT_NAME_MAP[stat_category]
    if len(br_stat_names) == 1:
      index = br_stat_names[0];
    elif len(br_stat_names) == 2:
      index = stat_category
    my_team_z_scores[index] = 0
    for key2, player in my_team["players"].items():
      my_team_z_scores[index] += player["z_scores"][index]

  my_team["z_scores"] = my_team_z_scores
  print("{}\n {}\n".format(key, my_team["z_scores"]))
