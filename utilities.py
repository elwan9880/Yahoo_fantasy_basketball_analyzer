import unidecode
from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
import pandas as pd

N_PLAYERS_WITH_TOP_MPG = 300 # how many players want to retrieve based on minute per game

STAT_CATEGORIES = {"GP":   ["GP"],
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

def divide(numerator, denominator):
  return float(numerator) / float(denominator) if float(denominator) != 0 else 0

def formalize_name(name):
  name = unidecode.unidecode(name)
  name = name.replace(".", "").replace(" Jr", "").replace(" III", "")
  name = name.replace("Jakob Poltl", "Jakob Poeltl").replace("Taurean Waller-Prince", "Taurean Prince").replace("Moe Harkless", "Maurice Harkless")
  return name

def create_csv_output_file(file_name, dictionary, stat_categories):
  f = open(file_name, "w+")
  f.write(",")
  for stat_name in stat_categories:
    f.write("{},".format(stat_name))
  for stat_name in stat_categories:
    f.write("z{},".format(stat_name))
  f.write("\n")

  for key, item in dictionary.items():
    f.write("{},".format(key))
    for stat_name in stat_categories:
      f.write("{0:.2f},".format(item.get_average_stats()[stat_name]))
    for stat_name in stat_categories:
      f.write("{0:.2f},".format(item.get_z_scores()[stat_name]))
    f.write("\n")
  f.close()

def create_player_stats_table(year):
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
  br_stats_table["Player"] = br_stats_table["Player"].apply(lambda x: formalize_name(x))
  br_stats_table.set_index("Player", inplace=True)

  # rename table header with Yahoo fantasy basketball stats name, type cast cells to float
  br_stats_table = br_stats_table.replace("", 0)
  for key, value in BR_TO_YFB_STATS_NAME_MAP.items():
    br_stats_table = br_stats_table.rename(columns={key: value})
    br_stats_table[value] = br_stats_table[value].apply(lambda x: float(x))

  # filter players based on MPG
  br_stats_table["MPG"] = br_stats_table["MIN"] / br_stats_table["GP"]
  br_stats_table = br_stats_table.sort_values(by=['MPG'], ascending=False)
  br_stats_table = br_stats_table.head(N_PLAYERS_WITH_TOP_MPG)
  br_stats_table = br_stats_table.sort_index()

  return br_stats_table

