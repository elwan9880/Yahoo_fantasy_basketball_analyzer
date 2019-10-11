from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json
from PyInquirer import style_from_dict, Token, prompt, Separator

from .utilities import STAT_CATEGORIES

SUPPORTED_YEARS = {"2018-2019": 2018, "2017-2018": 2017, "2016-2017": 2016, "2015-2016": 2015}
MODE = {"Fantasy Team Performance Analyzer": 0, "NBA Players Performance Analyzer": 1}
DEFAULT_9_CATEGORIES = {"FG%", "FT%", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"}

class YahooFantasyApiClient(object):

  def __init__(self, oauth2_file):
    self.__league = None
    self.__league_name = ""
    self.__user_selected_categories = []
    self.__oauth2_file = oauth2_file
    self.__dialog()

  def __dialog(self):
    questions = [
        {
            "type": "rawlist",
            "name": "mode",
            "message": "Please choose a mode:",
            "choices": MODE.keys()
        },
        {
            'type': "rawlist",
            'name': "year",
            'message': "And a NBA season:",
            'choices': SUPPORTED_YEARS.keys()
        }
    ]
    answers = prompt(questions)
    self.__mode = MODE[answers["mode"]]
    self.__year = SUPPORTED_YEARS[answers["year"]]

    if self.__mode == 0:
      self.__get_yahoo_fantasy_api_client()
    elif self.__mode == 1:
      # self.__user_selected_categories = list(STAT_CATEGORIES.keys())
      stat_categories_for_questions = []
      for item in STAT_CATEGORIES.keys():
        if item in DEFAULT_9_CATEGORIES:
          stat_categories_for_questions.append({"name": item, "checked": True})
        else:
          stat_categories_for_questions.append({"name": item})
      questions = [
          {
              'type': 'checkbox',
              'message': 'Select categories for analysis (default 9CAT):',
              'name': 'user_selected_categories',
              'choices': stat_categories_for_questions,
              'validate': lambda answer: 'You must choose at least one category.' \
                  if len(answer) == 0 else True
          }
      ]
      answers = prompt(questions)

      self.__user_selected_categories = answers["user_selected_categories"]

  def __get_yahoo_fantasy_api_client(self):
      sc = OAuth2(None, None, from_file = self.__oauth2_file)
      game = yfa.Game(sc, "nba")
      league_name_id_dict = {}
      for item in game.league_ids(year=self.__year):
        league_name_id_dict[game.to_league(item).settings()["name"]] = item
      if not league_name_id_dict:
        print("No fantasy teams in {}-{} seasons...".format(self.__year, self.__year + 1))
        exit(0)

      questions = [
          {
              "type": "rawlist",
              "name": "league",
              "message": "And the Fantasy league:",
              "choices": league_name_id_dict.keys()
          }
      ]
      answers = prompt(questions)
      self.__league_name = answers["league"]
      self.__league = game.to_league(league_name_id_dict[self.__league_name])

  def get_league_name(self):
    return self.__league_name

  def get_yahoo_fantasy_api_league(self):
    return self.__league

  def get_year(self):
    return self.__year

  def get_mode(self):
    return self.__mode

  def get_user_selected_categories(self):
    return self.__user_selected_categories

'''
  def __get_yahoo_fantasy_api_client(self, oauth2_file):
    sc = OAuth2(None, None, from_file = oauth2_file)
    game = yfa.Game(sc, "nba")
    league_id_list = []
    league_name_list = []
    for item in game.league_ids(year=self.__year):
      league_id_list.append(item)
      league_name_list.append(game.to_league(item).settings()["name"])
    if not league_id_list:
      print("No fantasy teams in {}-{} seasons...".format(self.__year, self.__year + 1))
      exit(0)
    input_id = self.__print_options_and_get_input("league", league_name_list)

    self.__league_id = league_id_list[int(input_id)]
    self.__league_name = league_name_list[int(input_id)]
    self.__league = game.to_league(self.__league_id)

  def __print_options_and_get_input(self, name, my_list):
    message = "Choose a {} ".format(name)
    for index in range(len(my_list)):
      if name is "season":
        message += "{{{}: {}-{}}} ".format(index, my_list[index], my_list[index] + 1)
      else:
        message += "{{{}: {}}} ".format(index, my_list[index])
    message += "[default: 0]: "
    input_id = input(message) or "0"
    while int(input_id) not in range(0, len(my_list)):
      input_id = input("Please enter an number between 0 to {}: ".format(len(my_list) - 1))

    return int(input_id)
'''
