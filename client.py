'''
client.py
'''

from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json

from utilities import STAT_CATEGORIES

SUPPORTED_YEARS = [2018, 2017, 2016, 2015]
MODE = ["Fantasy team score", "Player score"]

class Client(object):

  def __init__(self, oauth2_file):
    self.__league = None
    self.__league_id = ""
    self.__league_name = ""
    self.__user_selected_categories = []
    self.__mode = self.__print_options_and_get_input("mode", MODE)
    self.__year = SUPPORTED_YEARS[self.__print_options_and_get_input("season", SUPPORTED_YEARS)]
    if MODE[self.__mode] == "Fantasy team score":
      self.__get_yahoo_fantasy_api_client(oauth2_file)
      print("You select: Season: {}-{}, League: {}".format(self.__year, self.__year + 1, self.__league_name))
    elif MODE[self.__mode] == "Player score":
      self.__user_selected_categories = list(STAT_CATEGORIES.keys())
      print("You select: Season: {}-{}".format(self.__year, self.__year + 1))

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

  def get_league_id(self):
    return self.__league_id

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
