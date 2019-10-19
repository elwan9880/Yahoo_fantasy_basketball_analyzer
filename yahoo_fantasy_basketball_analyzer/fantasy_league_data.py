from .utilities import STAT_CATEGORIES, write_lines
from .nba_data import NBAData
from .team import Team

class FantasyLeagueData(object):

  # name: str
  # stat_category: list
  # teams - dict of class team

  def __init__(self, yahoo_fantasy_api_league, NBAData):
    self.__name = ""
    self.__stat_categories = []
    self.__teams = {}
    self.__name = yahoo_fantasy_api_league.settings()["name"]
    self.__get_stat_categories(yahoo_fantasy_api_league)
    self.__get_teams(yahoo_fantasy_api_league, NBAData)

  def __get_stat_categories(self, yahoo_fantasy_api_league):
    unsupprted_categories = []
    for stat_category in yahoo_fantasy_api_league.stat_categories():
      if STAT_CATEGORIES.get(stat_category["display_name"]) is not None:
        self.__stat_categories.append(stat_category["display_name"])
      else:
        unsupprted_categories.append(stat_category["display_name"])
    if unsupprted_categories:
        print(", ".join(unsupprted_categories) + " is(are) not supported and will be skipped ...", end = " ", flush = True)

  def __get_teams(self, yahoo_fantasy_api_league, NBAData):
    for item in yahoo_fantasy_api_league.teams():
      yahoo_fantasy_api_team = yahoo_fantasy_api_league.to_team(item["team_key"])
      self.__teams[item["name"]] = Team(yahoo_fantasy_api_team, NBAData, item["name"])

  def get_name(self):
    return self.__name

  def get_stat_categories(self):
    return self.__stat_categories

  def get_teams(self):
    return self.__teams

  def create_csv_file(self, file_name, f = None):
    f = f or open(file_name, "w+")

    z_categories = list(map(lambda cat: "z" + cat, self.__stat_categories))

    # Write team stats
    titles = ["Manager"] + self.__stat_categories + z_categories + ["zTotal"]
    write_lines(f, titles)
    for team_name, team in self.__teams.items():
      write_lines(f, [team_name] + team.get_stats_with_selected_category(self.__stat_categories))
    f.write("\n")

    # Write team player stats
    for team_name, team in self.__teams.items():
      titles = [team_name] + self.__stat_categories + z_categories + ["zTotal"]
      write_lines(f, titles)
      for player_name, player in team.get_players().items():
        write_lines(f, [player_name] + player.get_stats_with_selected_category(self.__stat_categories))
      f.write("\n")
    f.close()
