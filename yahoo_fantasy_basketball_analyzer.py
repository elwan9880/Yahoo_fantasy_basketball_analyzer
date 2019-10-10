'''
yahoo_fantasy_basketball_analyzer
'''

from client import Client
from utilities import create_csv_output_file, create_player_stats_table
from nba_data import NBAData
from fantasy_league_data import FantasyLeagueData
from player import Player
from team import Team

def main():

  ''' Retrieve league data in Yahoo Fantasy Basketball '''
  client = Client("oauth2.json")

  print("Parsing Basketball Reference NBA players total stats ...", end = " ", flush = True)
  stats_table = create_player_stats_table(client.get_year())
  print("Done")

  print("Calculating player performace...", end = " ", flush = True)
  nba_data = NBAData(stats_table)
  print("Done")

  csv_name = ""
  if client.get_mode() == 0:
    print("Calculating Fantasy team performace ...", end = " ", flush = True)
    fantasy_league_data = FantasyLeagueData(client.get_yahoo_fantasy_api_league(), nba_data)
    print("Done")

    ''' Print result in CSV format '''
    csv_name = "{}-{}_{}_teams.csv".format(client.get_year(), client.get_year() + 1, fantasy_league_data.get_name())
    create_csv_output_file(csv_name, fantasy_league_data.get_teams(), fantasy_league_data.get_stat_categories())
  elif client.get_mode() == 1:
    csv_name = "{}-{}_players.csv".format(client.get_year(), client.get_year() + 1)
    create_csv_output_file(csv_name, nba_data.get_players(), client.get_user_selected_categories())

  print("Finished! please import \"{}\" to excel as CSV format to see the results.".format(csv_name))

if __name__== "__main__":
  main()
