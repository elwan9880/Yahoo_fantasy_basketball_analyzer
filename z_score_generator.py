'''
z_score_generator
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
  year = client.get_year()
  league = client.get_yahoo_fantasy_api_league_struct()
  print("You select: Season: {}-{}, League: {} ".format(year, year + 1, client.get_league_name()))

  print("Parsing Basketball Reference {}-{} NBA players total stats ...".format(year, year + 1), end = " ", flush = True)
  stats_table = create_player_stats_table(year)
  print("Done")

  print("Retrieving NBA data and calculating player performace...", end = " ", flush = True)
  nba_data = NBAData(stats_table)
  print("Done")

  print("Calculating Fantasy team performace ...", end = " ", flush = True)
  fantasy_league_data = FantasyLeagueData(league, nba_data)
  print("Done")

  ''' Print result in CSV format '''
  teams_csv_name = "{}-{}_{}_teams.csv".format(year, year + 1, fantasy_league_data.get_name())
  players_csv_name = "{}-{}_{}_players.csv".format(year, year + 1, fantasy_league_data.get_name())
  create_csv_output_file(teams_csv_name, fantasy_league_data.get_teams(), fantasy_league_data.get_stat_categories())
  create_csv_output_file(players_csv_name, nba_data.get_players(), fantasy_league_data.get_stat_categories())

  print("Finished! please import \"{}\" and \"{}\" to excel as CSV format to see the results.".format(teams_csv_name, players_csv_name))

if __name__== "__main__":
  main()
