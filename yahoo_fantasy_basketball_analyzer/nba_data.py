from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
import pandas as pd
from statistics import stdev, mean

from .player import Player
from .utilities import formalize_name, divide, STAT_CATEGORIES

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

    self.__stats_table = pd.DataFrame(player_stats, columns = headers)
    self.__stats_table = self.__stats_table.dropna()
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
