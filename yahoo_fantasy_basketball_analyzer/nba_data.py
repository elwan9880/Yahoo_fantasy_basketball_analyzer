from urllib.request import urlopen
import json
import os
from bs4 import BeautifulSoup
import pandas as pd
from statistics import stdev, mean
from datetime import datetime

from .player import Player
from .utilities import formalize_name, divide, STAT_CATEGORIES, write_lines

N_PLAYERS_WITH_TOP_MPG = 300 # how many players want to retrieve based on minute per game

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

class NBAData(object):

  # stats_table - pandas object
  # stats_pool: dict - total_stats: dict
  #                  - average_stats: dict
  #                  - standard_deviation: dict
  # players: dict of class player

  def __init__(self, year):
    self.__stats_pool = {}
    self.__players = {}
    self.__stats_pool["total_stats"] = {}
    self.__stats_pool["average_stats"] = {}
    self.__stats_pool["standard_deviation"] = {}
    self.__get_player_stats_table(year)
    self.__get_stats_pool()
    self.__get_players()

  def __get_player_stats_table(self, year):
    date = datetime.now().strftime('%Y-%m-%d')
    filename = "tmp/player_stats_table_{}_{}.csv".format(year, date)
    if os.path.exists(filename):
      print("loaded from tmp")
      self.__stats_table = pd.read_csv(filename, index_col = 0)
      return
    url = "https://www.basketball-reference.com/leagues/NBA_{}_totals.html".format(year + 1)
    html = urlopen(url)
    soup = BeautifulSoup(html, "lxml")
    headers = [th.get_text() for th in soup.find_all('tr', limit=2)[0].find_all('th')]
    headers = headers[1:]
    rows = soup.find_all('tr')[1:]
    player_stats = [[td.get_text() for td in rows[i].find_all('td')] for i in range(len(rows))]

    self.__stats_table = pd.DataFrame(player_stats, columns = headers)
    self.__stats_table = self.__stats_table.dropna()

    # Replace player's team with the last team if the player played for more than a team in a season, then drop the duplicated data
    # Note on basketball reference for a player with multiple row , the first row is stats with team "TOT", and the last row is stats with current team
    for name in self.__stats_table[self.__stats_table["Player"].duplicated()]["Player"].drop_duplicates():
      num_teams = len(self.__stats_table[self.__stats_table["Player"] == name])
      current_team = self.__stats_table.loc[self.__stats_table["Player"] == name, "Tm"].iloc[num_teams - 1]
      self.__stats_table.loc[self.__stats_table["Player"] == name, "Tm"] = current_team
    self.__stats_table.drop_duplicates(subset = "Player", inplace = True)

    self.__stats_table["Player"] = self.__stats_table["Player"].apply(lambda x: formalize_name(x))
    self.__stats_table.set_index("Player", inplace=True)

    # rename table header with Yahoo fantasy basketball stats name, type cast cells to float
    self.__stats_table = self.__stats_table.replace("", 0)
    for key, value in BR_TO_YFB_STATS_NAME_MAP.items():
      self.__stats_table = self.__stats_table.rename(columns={key: value})
      self.__stats_table[value] = self.__stats_table[value].apply(lambda x: float(x))

    # filter players based on MPG
    self.__stats_table["MPG"] = self.__stats_table["MIN"] / self.__stats_table["GP"]
    self.__stats_table = self.__stats_table.sort_values(by=['MPG'], ascending=False)
    self.__stats_table = self.__stats_table.head(N_PLAYERS_WITH_TOP_MPG)
    self.__stats_table = self.__stats_table.sort_index()
    os.makedirs(os.path.dirname(filename), exist_ok = True)
    self.__stats_table.to_csv(filename)

  def __get_stats_pool(self):
    # league total stats
    for key, value in STAT_CATEGORIES.items():
      for stat in value:
        self.__stats_pool["total_stats"][stat] = self.__stats_table[stat].sum()

    # league average stats
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        if key in {"GP", "GS"}:
          self.__stats_pool["average_stats"][key] = self.__stats_table[key].sum() / len(self.__stats_table.index)
        else:
          self.__stats_pool["average_stats"][key] = self.__stats_pool["total_stats"][key] / self.__stats_pool["total_stats"]["GP"]
      elif len(value) == 2:
        self.__stats_pool["average_stats"][key] = self.__stats_pool["total_stats"][value[0]] / self.__stats_pool["total_stats"][value[1]]

    # league standard deviation
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        if key in {"GP", "GS"}:
          self.__stats_pool["standard_deviation"][key] = self.__stats_table[key].std()
        else:
          self.__stats_pool["standard_deviation"][key] = self.__stats_table[[key, 'GP']].apply(lambda x: divide(*x), axis = 1).std()
      elif len(value) == 2:
        stdev_temp_list = []
        league_average = self.__stats_pool["average_stats"][key]
        for index, row in self.__stats_table.iterrows():
          player_average = divide(row[value[0]], row[value[1]])
          d = player_average - league_average
          m = d * (row[value[1]] / row["GP"])
          stdev_temp_list.append(m)
        self.__stats_pool["standard_deviation"][key] = stdev(stdev_temp_list)
        # note: the average for percentage stats is average of "impact" ((player_avg - league_avg) / player_attempt)
        self.__stats_pool["average_stats"][key] = mean(stdev_temp_list)

  def __get_players(self):
    for index, row in self.__stats_table.iterrows():
      self.__players[index] = Player(row, self.__stats_pool)

  def get_stats_pool(self):
    return self.__stats_pool

  def get_players(self):
    return self.__players

  def create_csv_file(self, file_name, stat_categories, f = None):
    f = f or open(file_name, "w+")

    # Write titles
    z_categories = list(map(lambda cat: "z" + cat, stat_categories))
    titles = ["Player"] + stat_categories + z_categories + ["zTotal"]
    write_lines(f, titles)

    #write players
    for name, player in self.__players.items():
      f.write(name)
      write_lines(f, player.get_stats_with_selected_category(stat_categories), indents = 1)
    f.close()

