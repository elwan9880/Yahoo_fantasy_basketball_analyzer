'''
yahoo_fantasy_basketball_analyzer
'''

from yahoo_fantasy_basketball_analyzer import yahoo_fantasy_api_client, utilities, nba_data, fantasy_league_data, trade_analyzer

def main():

  ''' Retrieve league data in Yahoo Fantasy Basketball '''
  yfa_client = yahoo_fantasy_api_client.YahooFantasyApiClient("oauth2.json")

  print("  Calculating player performace ...", end = " ", flush = True)
  my_nba_data = nba_data.NBAData(yfa_client.get_year())
  print("Done")

  csv_name = ""
  mode = yfa_client.get_mode()
  if mode == 0 or mode == 1:
    print("  Calculating Fantasy team performace ...", end = " ", flush = True)
    my_fantasy_league_data = fantasy_league_data.FantasyLeagueData(yfa_client.get_yahoo_fantasy_api_league(), my_nba_data)
    print("Done")
    if mode == 0:
      csv_name = "{}-{}_{}_teams.csv".format(yfa_client.get_year(), yfa_client.get_year() + 1, my_fantasy_league_data.get_name())
      utilities.output_league_csv_file(csv_name, my_fantasy_league_data.get_teams(), my_fantasy_league_data.get_stat_categories())
    elif mode == 1:
      my_trade_analyzer = trade_analyzer.TradeAnalyzer(my_fantasy_league_data)
      csv_name = "{}-{}_{}_{}_{}.csv".format(yfa_client.get_year(), yfa_client.get_year() + 1, my_fantasy_league_data.get_name(), my_trade_analyzer.get_team_1().get_name(), my_trade_analyzer.get_team_2().get_name())
      my_trade_analyzer.print_result(my_fantasy_league_data, csv_name)

  elif mode == 2:
    csv_name = "{}-{}_players.csv".format(yfa_client.get_year(), yfa_client.get_year() + 1)
    utilities.output_players_csv_file(csv_name, my_nba_data.get_players(), yfa_client.get_user_selected_categories())

  print("  Finished! Please import \"{}\" to excel as CSV format to see the results.".format(csv_name))

if __name__== "__main__":
  main()
