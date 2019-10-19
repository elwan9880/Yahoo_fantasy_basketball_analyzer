from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
from PyInquirer import prompt

class YahooFantasyApiClient(object):
  def __init__(self, year, oauth2_file):
    sc = OAuth2(None, None, from_file = oauth2_file)
    game = yfa.Game(sc, "nba")
    league_name_id_dict = {}
    for item in game.league_ids(year=year):
      league_name_id_dict[game.to_league(item).settings()["name"]] = item
    if not league_name_id_dict:
      print("No fantasy teams in {}-{} seasons...".format(year, year + 1))
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
    self.__league = game.to_league(league_name_id_dict[answers["league"]])

  def get_league(self):
    return self.__league
