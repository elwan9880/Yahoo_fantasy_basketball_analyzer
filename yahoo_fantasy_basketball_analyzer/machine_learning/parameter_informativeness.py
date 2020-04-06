import sqlite3
from numpy.linalg import inv
import sys
import utils

TARGET="PTS"

# For PTS, best parameters: ["FGA", "PTS", "FG", "GmSc", "MP", "FT", "FTA", "TOV", "USG%"]

def parameter_informativeness(db, target):

  utils.create_referred_data_table(sys.argv[1])

  score = {};
  for item in utils.REFERRED_CATEGORIES:
    x_table, y_table = utils.db_to_df(sys.argv[1], target=TARGET, stats_pool={TARGET: [item]})
    y = ((y_table - y_table.mean()) / y_table.std()).values.reshape(1, -1)
    x_table = x_table.mean(axis=1)
    x = ((x_table - x_table.mean()) / x_table.std()).values

    score[item] = ((y - x) ** 2).mean() ** .5

  score = sorted(score.items(), key=lambda x: x[1])
  print("Parameter Informative for {}, smaller is better".format(TARGET))
  for k, v in score:
    print("{}: {}".format(k, v))

if __name__ == "__main__":
  parameter_informativeness("players_2018.db", "PTS")
