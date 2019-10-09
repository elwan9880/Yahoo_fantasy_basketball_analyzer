'''
z_score_generator
'''

import yahoo_fantasy_api as yfa
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import unidecode
from statistics import stdev, mean

from client import Client
from utilities import STAT_CATEGORIES, BR_TO_YFB_STATS_NAME_MAP, divide, formalize_name
from nba_data import NBAData
from fantasy_league_data import FantasyLeagueData
from player import Player
from team import Team

N_PLAYERS_WITH_TOP_MPG = 300 # how many players want to retrieve based on minute per game

def create_csv_output_file(file_name, dictionary, stat_categories):
  f = open(file_name, "w+")
  f.write(",")
  for stat_name in stat_categories:
    f.write("{},".format(stat_name))
  for stat_name in stat_categories:
    f.write("z{},".format(stat_name))
  f.write("\n")

  for key, item in dictionary.items():
    f.write("{},".format(key))
    for stat_name in stat_categories:
      f.write("{},".format(item.get_average_stats()[stat_name]))
    for stat_name in stat_categories:
      f.write("{},".format(item.get_z_scores()[stat_name]))
    f.write("\n")
  f.close()

def create_player_stats_table(year):
  # URL page we will scraping (see image above)
  url = "https://www.basketball-reference.com/leagues/NBA_{}_totals.html".format(year + 1)
  # this is the HTML from the given URL
  html = urlopen(url)
  soup = BeautifulSoup(html, "lxml")
  # use findALL() to get the column headers
  soup.findAll('tr', limit=2)
  # use getText() to extract the text we need into a list
  headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
  # exclude the first column as we will not need the ranking order from Basketball Reference for the analysis
  headers = headers[1:]
  # avoid the first header row
  rows = soup.findAll('tr')[1:]
  player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

  br_stats_table = pd.DataFrame(player_stats, columns = headers)
  br_stats_table = br_stats_table.dropna()
  br_stats_table.drop_duplicates(subset = "Player", inplace = True)
  br_stats_table["Player"] = br_stats_table["Player"].apply(lambda x: formalize_name(x))
  br_stats_table.set_index("Player", inplace=True)

  # rename table header with Yahoo fantasy basketball stats name, type cast cells to float
  br_stats_table = br_stats_table.replace("", 0)
  for key, value in BR_TO_YFB_STATS_NAME_MAP.items():
    br_stats_table = br_stats_table.rename(columns={key: value})
    br_stats_table[value] = br_stats_table[value].apply(lambda x: float(x))

  # filter players based on MPG
  br_stats_table["MPG"] = br_stats_table["MIN"] / br_stats_table["GP"]
  br_stats_table = br_stats_table.sort_values(by=['MPG'], ascending=False)
  br_stats_table = br_stats_table.head(N_PLAYERS_WITH_TOP_MPG)
  br_stats_table = br_stats_table.sort_index()

  return br_stats_table

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
  # create_csv_output_file(players_csv_name, my_player_struct)

  print("Finished! please import \"{}\" and \"{}\" to excel as CSV format to see the results.".format(teams_csv_name, players_csv_name))

if __name__== "__main__":
  main()
