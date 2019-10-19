from yahoo_fantasy_basketball_analyzer import client, nba_data, fantasy_league_data, trade_analyzer

def main():

  my_client = client.Client("oauth2.json")

  print("  Calculating player performace ...", end = " ", flush = True)
  my_nba_data = nba_data.NBAData(my_client.get_year())
  print("Done")

  csv_name = ""
  mode = my_client.get_mode()

  if mode == 0 or mode == 1:
    print("  Calculating Fantasy team performace ...", end = " ", flush = True)
    my_fantasy_league_data = fantasy_league_data.FantasyLeagueData(my_client.get_yahoo_fantasy_api_league(), my_nba_data)
    print("Done")

    if mode == 0:
      csv_name = "{}-{}_{}_teams.csv".format(my_client.get_year(), my_client.get_year() + 1, my_fantasy_league_data.get_name())
      my_fantasy_league_data.create_csv_file(csv_name)

    elif mode == 1:
      my_trade_analyzer = trade_analyzer.TradeAnalyzer(my_fantasy_league_data)
      csv_name = "{}-{}_{}_{}_{}.csv".format(my_client.get_year(), my_client.get_year() + 1, my_fantasy_league_data.get_name(), my_trade_analyzer.get_team_1().get_name(), my_trade_analyzer.get_team_2().get_name())
      my_trade_analyzer.create_csv_file(csv_name)

  elif mode == 2:
    csv_name = "{}-{}_players.csv".format(my_client.get_year(), my_client.get_year() + 1)
    my_nba_data.create_csv_file(csv_name, my_client.get_user_selected_categories())

  print("  Finished! Please import \"{}\" to excel as CSV format to see the results.".format(csv_name))

if __name__== "__main__":
  main()
