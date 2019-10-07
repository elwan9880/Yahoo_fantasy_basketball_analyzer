'''
client.py
'''

from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json

SUPPORTED_YEARS = [2018, 2017, 2016, 2015]

class Client(object):

  __league = None
  __league_id = ""
  __league_name = ""
  __year = 0

  def __init__(self, oauth2_file):
    sc = OAuth2(None, None, from_file = oauth2_file)
    game = yfa.Game(sc, "nba")

    self.__year = SUPPORTED_YEARS[self.__print_options_and_get_input("season", SUPPORTED_YEARS)]

    league_id_name_pair_list = []
    for item in game.league_ids(year=self.__year):
      league_id_name_pair_list.append((item, game.to_league(item).settings()["name"]))
    if not league_id_name_pair_list:
      print("No fantasy teams in {}-{} seasons...".format(self.__year, self.__year + 1))
      exit(0)
    input_id = self.__print_options_and_get_input("league", league_id_name_pair_list)

    self.__league_id = league_id_name_pair_list[int(input_id)][0]
    self.__league_name = league_id_name_pair_list[int(input_id)][1]
    self.__league = game.to_league(self.__league_id)

  def __print_options_and_get_input(self, name, my_list):
    message = "Choose a {} ".format(name)
    for index in range(len(my_list)):
      if name is "season":
        message += "{{{}: {}-{}}} ".format(index, my_list[index], my_list[index] + 1)
      elif name is "league":
        message += "{{{}: {}}} ".format(index, my_list[index][1])
    message += "[default: 0]: "
    input_id = input(message) or "0"
    while int(input_id) not in range(0, len(my_list)):
      input_id = input("Please enter an number between 0 to {}: ".format(len(my_list) - 1))

    return int(input_id)

  def get_league_id(self):
    return self.__league_id

  def get_league_name(self):
    return self.__league_name

  def get_yahoo_fantasy_api_league_struct(self):
    return self.__league

  def get_year(self):
    return self.__year
