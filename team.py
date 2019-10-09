from player import Player
from utilities import formalize_name, divide, STAT_CATEGORIES

class Team(object):

  # name: str
  # players - dict of class player
  # total_stats - dict
  # average_stats - dict
  # z_scores - dict

  __name = ""
  __players = {}
  __total_stats = {}
  __average_stats = {}
  __z_scores = {}

  def __init__(self, yahoo_fantasy_api_team, NBAData, week, name):
    self.__name = name
    self.__get_players(yahoo_fantasy_api_team, NBAData, week)
    print("{}".format(self.__players))
    self.__get_total_stats()
    self.__get_average_stats()
    self.__get_z_scores()

  def __get_players(self, yahoo_fantasy_api_team, NBAData, week):
    players = NBAData.get_players()
    for player in yahoo_fantasy_api_team.roster(week):
      player_name = formalize_name(player["name"])
      if players.get(player_name) is None:
        continue
      self.__players[player_name] = NBAData.get_players()[player_name]

  def __get_total_stats(self):
    for key, value in STAT_CATEGORIES.items():
      for stat in value:
        self.__total_stats[stat] = 0
    for player_name, player_object in self.__players.items():
      player_total_stats = player_object.get_total_stats()
      for stat_name, stat_value in player_total_stats.items():
        if len(STAT_CATEGORIES[stat_name]) == 1:
          self.__total_stats[stat_name] += stat_value

  def __get_average_stats(self):
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        self.__average_stats[key] = divide(self.__total_stats[key], self.__total_stats["GP"])
      elif len(value) == 2:
        self.__average_stats[key] = divide(self.__total_stats[value[0]], self.__total_stats[value[1]])

  def __get_z_scores(self):
    for key, value in STAT_CATEGORIES.items():
      self.__z_scores[key] = 0
    for player_name, player_object in self.__players.items():
      player_z_scores = player_object.get_z_scores()
      for stat_name, stat_value in player_z_scores.items():
        self.__z_scores[stat_name] += stat_value

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
