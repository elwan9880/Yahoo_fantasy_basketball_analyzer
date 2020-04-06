import csv, sqlite3
import pandas
from os import listdir

def find_csv_filenames(path_to_dir, suffix=".csv"):
  filenames = listdir(path_to_dir)
  return [filename for filename in filenames if filename.endswith( suffix )]

def create_db_from_csv(year=2018):
  csv_dir = "data/{}/player/".format(year)

  con = sqlite3.connect("players_{}.db".format(year))

  player_names = []
  csv_names = find_csv_filenames(csv_dir)
  for csv in csv_names:
    table = pandas.read_csv("{}/{}".format(csv_dir, csv))
    table = table.fillna(0)
    player_name = csv.replace(" ", "_").replace(".csv", "")
    table.to_sql(player_name, con=con, index=False)
    player_names.append(player_name)

  player_index_table = "_PLAYER_INDEX"
  con.cursor().execute("CREATE TABLE {} (id integer PRIMARY KEY, name text NOT NULL);".format(player_index_table))
  id = 0
  for name in player_names:
    con.cursor().execute("INSERT INTO {} (id, name) VALUES ({}, \"{}\");".format(player_index_table, id, name))
    id = id + 1

  con.commit();
  con.close()

if __name__ == "__main__":
  create_db_from_csv(2018)
