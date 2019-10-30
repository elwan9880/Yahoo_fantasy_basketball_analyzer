import pandas as pd
import csv
from os import listdir
import sys
import re

year = 2018
training_stats = "PTS"
referred_games = int(sys.argv[1]) if len(sys.argv) > 1 else 5
referred_stats = [training_stats, "GS", "MP", "FG", "FGA", "3P", "3PA", "FT", "FTA", "+/-"]

def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith( suffix )]

csv_name = "{}_{}_{}G_(".format(year, training_stats, referred_games)
csv_name += "-".join(referred_stats).replace("+/-", "PN")
csv_name += ").csv"
with open(csv_name, "w", newline = "") as f:
  wr = csv.writer(f, quoting=csv.QUOTE_ALL)

  header = []
  for item in referred_stats:
    for i in range(referred_games, 0, -1):
      header.append("{}_{}".format(item, i))
  header.append(training_stats)
  wr.writerow(header)

  csv_names = find_csv_filenames("{}".format(year))

  for csv in csv_names:
    table = pd.read_csv("{}/{}".format(year, csv))
    for i in range(referred_games, len(table.index)):
      row = [];
      for item in referred_stats:
        for j in range(referred_games, 0, -1):
          data = table.iloc[i - j][item]
          if item == "MP":
            data = data.replace(":", ".")
          row.append(data)
      row.append(table.iloc[i][training_stats])
      wr.writerow(row)

f.close()
