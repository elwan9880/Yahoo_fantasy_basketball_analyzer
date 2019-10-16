from datetime import date

from .player import Player
from .utilities import formalize_name, divide, STAT_CATEGORIES

class Team(object):

  # name: str
  # players - dict of class player
  # total_stats - dict
  # average_stats - dict
  # z_scores - dict

  def __init__(self, yahoo_fantasy_api_team, NBAData, name):
    self.__name = name
    self.__players = {}
    self.__total_stats = {}
    self.__average_stats = {}
    self.__z_scores = {}
    self.__stats = []
    self.__get_players(yahoo_fantasy_api_team, NBAData)
    self.calculate_total_stats()
    self.calculate_average_stats()
    self.calculate_z_scores()

  def __get_players(self, yahoo_fantasy_api_team, NBAData):
    players = NBAData.get_players()
    for player in yahoo_fantasy_api_team.roster(day=date.today()):
      player_name = formalize_name(player["name"])
      if players.get(player_name) is None:
        continue
      self.__players[player_name] = NBAData.get_players()[player_name]

  def remove_player(self, player_name):
    self.__players.pop(player_name)

  def add_player(self, player):
    self.__players[player.get_name()] = player

  def calculate_total_stats(self):
    for key, value in STAT_CATEGORIES.items():
      for stat in value:
        self.__total_stats[stat] = 0
    for player_name, player_object in self.__players.items():
      player_total_stats = player_object.get_total_stats()
      for stat_name, stat_value in player_total_stats.items():
        if len(STAT_CATEGORIES[stat_name]) == 1:
          self.__total_stats[stat_name] += stat_value

  def calculate_average_stats(self):
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        self.__average_stats[key] = divide(self.__total_stats[key], self.__total_stats["GP"])
      elif len(value) == 2:
        self.__average_stats[key] = divide(self.__total_stats[value[0]], self.__total_stats[value[1]])

  def calculate_z_scores(self):
    for key, value in STAT_CATEGORIES.items():
      self.__z_scores[key] = 0
    for player_name, player_object in self.__players.items():
      player_z_scores = player_object.get_z_scores()
      for stat_name, stat_value in player_z_scores.items():
        self.__z_scores[stat_name] += stat_value
    for key, value in STAT_CATEGORIES.items():
      self.__z_scores[key] /= len(self.__players)

  def get_name(self):
    return self.__name

  def get_players(self):
    return self.__players

  def get_total_stats(self):
    return self.__total_stats

  def get_average_stats(self):
    return self.__average_stats

  def get_z_scores(self):
    return self.__z_scores

  def get_stats_with_selected_category(self, category_list):
    stats = []
    length = len(category_list)
    total_z_score = 0
    for i, category in enumerate(category_list):
      z_score = self.__z_scores[category]
      total_z_score += z_score
      stats.insert(i, self.__average_stats[category])
      stats.insert(i + length, z_score)
    stats.append(total_z_score)
    return stats
