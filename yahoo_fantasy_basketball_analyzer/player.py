from .utilities import formalize_name, divide, STAT_CATEGORIES

class Player(object):

  # name: str
  # total_stats: dict
  # average_stats: dict
  # z_scores: dict

  def __init__(self, player_stats, stats_pool):
    self.__name = player_stats.name
    self.__total_stats = {}
    self.__average_stats = {}
    self.__z_scores = {}
    self.__get_player(player_stats, stats_pool)

  def __get_player(self, player_stats, stats_pool):

    # player total stats
    for key, value in STAT_CATEGORIES.items():
      for stat in value:
        self.__total_stats[stat] = player_stats[stat]

    # player average stats
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        self.__average_stats[key] = divide(self.__total_stats[key], self.__total_stats["GP"])
      elif len(value) == 2:
        self.__average_stats[key] = divide(self.__total_stats[value[0]], self.__total_stats[value[1]])

    # player z-scores
    for key, value in STAT_CATEGORIES.items():
      if len(value) == 1:
        if key in {"GP", "GS"}:
          o = self.__total_stats[key]
        else:
          o = divide(self.__total_stats[key], self.__total_stats["GP"])
        m = stats_pool["average_stats"][key]
        s = stats_pool["standard_deviation"][key]
        if key in {"TO", "PF"}:
          self.__z_scores[key] = 0 - ((o - m) / s)
        else:
          self.__z_scores[key] = (o - m) / s
      elif len(value) == 2:
        league_average = divide(stats_pool["total_stats"][value[0]], stats_pool["total_stats"][value[1]])
        player_average = divide(self.__total_stats[value[0]], self.__total_stats[value[1]])
        o = divide((player_average - league_average) * self.__total_stats[value[1]], self.__total_stats["GP"])
        m = stats_pool["average_stats"][key]
        s = stats_pool["standard_deviation"][key]
        self.__z_scores[key] = (o - m) / s

  def get_name(self):
    return self.__name

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



