import json
from PyInquirer import prompt

from .yahoo_fantasy_api_client import YahooFantasyApiClient
from .utilities import STAT_CATEGORIES

SUPPORTED_YEARS = {"2021-2022": 2021, "2020-2021": 2020, "2019-2020": 2019, "2018-2019": 2018, "2017-2018": 2017, "2016-2017": 2016, "2015-2016": 2015}
MODE = {"Fantasy Team Performance Analyzer": 0, "Fantasy Trade Analyzer": 1, "NBA Players Performance Analyzer": 2}
DEFAULT_9_CATEGORIES = {"FG%", "FT%", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"}

class Client(object):

  def __init__(self, oauth2_file):
    self.__yahoo_fantasy_api_league = None
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

    if self.__mode == 0 or self.__mode == 1:
      self.__yahoo_fantasy_api_client = YahooFantasyApiClient(self.__year, self.__oauth2_file)

    elif self.__mode == 2:
      stat_categories_for_questions = []
      for item in STAT_CATEGORIES.keys():
        if item in DEFAULT_9_CATEGORIES:
          stat_categories_for_questions.append({"name": item, "checked": True})
        else:
          stat_categories_for_questions.append({"name": item})
      questions = [
          {
              'type': 'checkbox',
              'message': 'Select categories for analysis (9CAT by default):',
              'name': 'user_selected_categories',
              'choices': stat_categories_for_questions,
              'validate': lambda answer: 'You must choose at least one category.' \
                  if len(answer) == 0 else True
          }
      ]
      answers = prompt(questions)

      self.__user_selected_categories = answers["user_selected_categories"]

  def get_yahoo_fantasy_api_league(self):
    return self.__yahoo_fantasy_api_client.get_league()

  def get_year(self):
    return self.__year

  def get_mode(self):
    return self.__mode

  def get_user_selected_categories(self):
    return self.__user_selected_categories

