import copy
from PyInquirer import prompt

from .fantasy_league_data import FantasyLeagueData
from .utilities import write_lines

class TradeAnalyzer(object):
  def __init__(self, fantasy_league_data):
    self.__dialog(fantasy_league_data)
    self.__swap_players()

  def print_result(self, fantasy_league_data, csv_name):
    stat_categories = fantasy_league_data.get_stat_categories()
    z_categories = list(map(lambda cat: "z" + cat, stat_categories))
    titles = ["Player"] + stat_categories + z_categories + ["zTotal"]

    f = open(csv_name, "w+")

    f.write("{} receives:\n".format(self.__team_1_before.get_name()))
    write_lines(f, titles)
    for item in self.__team_2_send_players:
      write_lines(f, [item] + self.__team_2_before.get_players()[item].get_stats_with_selected_category(stat_categories))
    f.write("\n")

    f.write("{} receives:\n".format(self.__team_2_before.get_name()))
    write_lines(f, titles)
    for item in self.__team_1_send_players:
      write_lines(f, [item] + self.__team_1_before.get_players()[item].get_stats_with_selected_category(stat_categories))
    f.write("\n")

    titles = ["Manager"] + stat_categories + z_categories + ["zTotal"]

    f.write("Before trade:\n")
    write_lines(f, titles)
    write_lines(f, [self.__team_1_before.get_name()] + self.__team_1_before.get_stats_with_selected_category(stat_categories))
    write_lines(f, [self.__team_2_before.get_name()] + self.__team_2_before.get_stats_with_selected_category(stat_categories))
    f.write("\n")

    f.write("After trade:\n")
    write_lines(f, titles)
    write_lines(f, [self.__team_1_after.get_name()] + self.__team_1_after.get_stats_with_selected_category(stat_categories))
    write_lines(f, [self.__team_2_after.get_name()] + self.__team_2_after.get_stats_with_selected_category(stat_categories))
    f.close()

  def __swap_players(self):
    self.__team_1_after = copy.deepcopy(self.__team_1_before)
    self.__team_2_after = copy.deepcopy(self.__team_2_before)

    for item in self.__team_1_send_players:
      self.__team_2_after.add_player(self.__team_1_after.get_players()[item])
      self.__team_1_after.remove_player(item)

    for item in self.__team_2_send_players:
      self.__team_1_after.add_player(self.__team_2_after.get_players()[item])
      self.__team_2_after.remove_player(item)

    self.__team_1_after.calculate_total_stats()
    self.__team_1_after.calculate_average_stats()
    self.__team_1_after.calculate_z_scores()
    self.__team_2_after.calculate_total_stats()
    self.__team_2_after.calculate_average_stats()
    self.__team_2_after.calculate_z_scores()

  def __dialog(self, fantasy_league_data):
    # team
    teams = fantasy_league_data.get_teams()
    team_names = list(teams.keys())
    questions = [
        {
            "type": "list",
            "name": "team_1",
            "message": "Please choose team 1 to trade:",
            "choices": team_names
        }
    ]
    answers = prompt(questions)
    self.__team_1_before = teams[answers["team_1"]]
    team_names.remove(answers["team_1"])
    questions = [
        {
            "type": "list",
            "name": "team_2",
            "message": "Please choose team 2 to trade:",
            "choices": team_names
        }
    ]
    answers = prompt(questions)
    self.__team_2_before = teams[answers["team_2"]]
    # team1 players
    players_for_questions = []
    for name in self.__team_1_before.get_players():
      players_for_questions.append({"name": name})
    questions = [
        {
            "type": "checkbox",
            "name": "team_1_send_players",
            "message": "Please choose players from {} to trade:".format(self.__team_1_before.get_name()),
            "choices": players_for_questions
        }
    ]
    answers = prompt(questions)
    self.__team_1_send_players = answers["team_1_send_players"]
    # team2 players
    players_for_questions = []
    for name in self.__team_2_before.get_players():
      players_for_questions.append({"name": name})
    questions = [
        {
            "type": "checkbox",
            "name": "team_2_send_players",
            "message": "Please choose players from {} to trade:".format(self.__team_2_before.get_name()),
            "choices": players_for_questions
        }
    ]
    answers = prompt(questions)
    self.__team_2_send_players = answers["team_2_send_players"]

  def get_team_1(self):
    return self.__team_1_after

  def get_team_2(self):
    return self.__team_2_after
