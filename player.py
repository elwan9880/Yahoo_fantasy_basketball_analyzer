import pandas

class player(object):

  # name: str
  # total_stats: dict
  # average_stats: dict
  # z_scores: dict

  self.name = ""
  self.total_stats = {}
  self.average_stats = {}
  self.z_scores = {}

  def __init__(self, row_of_stats_table, stats_pool):
