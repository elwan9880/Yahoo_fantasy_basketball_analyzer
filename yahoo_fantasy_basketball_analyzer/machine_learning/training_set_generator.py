import pandas as pd
import csv
from os import listdir
import sys
import re

year = 2018
training_stats = "PTS"

predict_games =  int(sys.argv[1]) if len(sys.argv) > 1 else 4
referred_games = int(sys.argv[2]) if len(sys.argv) > 1 else 4
referred_player_stats_pool = {
  "PTS": ["AVG_S", "MP", "FGA", "FG", "3PA", "3P", "FTA", "FT", "USG%", "ORtg"],
  "TRB": ["AVG_S", "MP", "ORB", "DRB", "FG%", "FTA", "BLK", "PF"]
}
referred_team_stats_pool = {
  "PTS": [],
}
referred_opp_team_stats_pool = {
  "PTS": ["DRtg", "Pace"],
}
referred_player_stats = referred_player_stats_pool[training_stats]
# referred_team_stats = referred_team_stats_pool[training_stats]
referred_opp_team_stats = referred_opp_team_stats_pool[training_stats]

def find_csv_filenames(path_to_dir, suffix=".csv"):
  filenames = listdir(path_to_dir)
  return [filename for filename in filenames if filename.endswith( suffix )]

def mp_to_second(mp):
  (m, s) = mp.split(":")
  return int(m) * 60 + int(s)

csv_name = "{}_{}-{}_{}G_(".format(year, training_stats, predict_games, referred_games)
csv_name += "-".join(referred_player_stats).replace("+/-", "PN")
csv_name += ").csv"
with open(csv_name, "w", newline = "") as f:
  wr = csv.writer(f, quoting=csv.QUOTE_ALL)

  header = []
  for item in referred_player_stats:
    for i in range(referred_games, 0, -1):
      header.append("{}_{}".format(item, i))
  header.append("{}-{}G".format(training_stats, predict_games))
  wr.writerow(header)

  csv_names = find_csv_filenames("{}/player".format(year))

  for csv in csv_names:
    table = pd.read_csv("{}/player/{}".format(year, csv))
    table = table.fillna(0)
    for i in range(referred_games, len(table.index) - predict_games):
      row = [];
      for item in referred_player_stats:
        for j in range(referred_games, 0, -1):
          if item == "AVG_S":
            data = table.iloc[0: i - j + 1][training_stats].mean()
          else:
            data = table.iloc[i - j][item]
            if item == "MP":
              data = mp_to_second(data)
          row.append(data)
      row.append(sum([table.iloc[k][training_stats] for k in range(i, i + predict_games)]) / predict_games)
      wr.writerow(row)

f.close()
