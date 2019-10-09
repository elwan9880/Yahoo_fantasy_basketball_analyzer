from player import Player
from utilities import divide, STAT_CATEGORIES
from statistics import stdev, mean

class NBAData(object):

  # stats_pool: dict - total_stats: dict
  #                  - average_stats: dict
  #                  - standard_deviation: dict
  # players: dict of class player

  def __init__(self, stats_table):
    self.__stats_pool = {}
    self.__players = {}
    self.__stats_pool["total_stats"] = {}
    self.__stats_pool["average_stats"] = {}
    self.__stats_pool["standard_deviation"] = {}
    self.__get_stats_pool(stats_table)
    self.__get_players(stats_table)

  def __get_stats_pool(self, stats_table):
    # league total stats
    for key, value in STAT_CATEGORIES.items():
      for stat in value:
        self.__stats_pool["total_stats"][stat] = stats_table[stat].sum()

    # league average stats
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        if key in {"GP", "GS"}:
          self.__stats_pool["average_stats"][key] = stats_table[key].sum() / len(stats_table.index)
        else:
          self.__stats_pool["average_stats"][key] = self.__stats_pool["total_stats"][key] / self.__stats_pool["total_stats"]["GP"]
      elif len(value) == 2:
        self.__stats_pool["average_stats"][key] = self.__stats_pool["total_stats"][value[0]] / self.__stats_pool["total_stats"][value[1]]

    # league standard deviation
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        if key in {"GP", "GS"}:
          self.__stats_pool["standard_deviation"][key] = stats_table[key].std()
        else:
          self.__stats_pool["standard_deviation"][key] = stats_table[[key, 'GP']].apply(lambda x: divide(*x), axis = 1).std()
      elif len(value) == 2:
        stdev_temp_list = []
        league_average = self.__stats_pool["average_stats"][key]
        for index, row in stats_table.iterrows():
          player_average = divide(row[value[0]], row[value[1]])
          d = player_average - league_average
          m = d * (row[value[1]] / row["GP"])
          stdev_temp_list.append(m)
        self.__stats_pool["standard_deviation"][key] = stdev(stdev_temp_list)
        # note: the average for percentage stats is average of "impact" ((player_avg - league_avg) / player_attempt)
        self.__stats_pool["average_stats"][key] = mean(stdev_temp_list)

  def __get_players(self, stats_table):
    for index, row in stats_table.iterrows():
      self.__players[index] = Player(row, self.__stats_pool)

  def get_stats_pool(self):
    return self.__stats_pool

  def get_players(self):
    return self.__players
