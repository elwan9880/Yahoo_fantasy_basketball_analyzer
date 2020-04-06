import sqlite3
import pandas

PREDICT_CATEGORIES = {"PTS", "3P", "FT%", "FG%", "AST", "TRB", "STL", "BLK", "TOV"}
REFERRED_CATEGORIES = {"GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "GmSc", "+/-", "TS%", "eFG%", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "ORtg", "DRtg"}
STATS_POOL = {
  "PTS": ["FGA", "PTS", "FG", "GmSc", "MP", "FT", "FTA", "TOV", "USG%"],
  "TRB": ["MP", "ORB", "DRB", "FG", "FGA", "FTA", "BLK", "PF"]
}

def mp_to_second(mp):
  (m, s) = mp.split(":")
  return int(m) * 60 + int(s)

def db_to_df(db, target, ref=4, pred=4, stats_pool=STATS_POOL):
  table_name = "_REF{}_PRED{}".format(ref, pred)
  con = sqlite3.connect(db)

  x_query = []
  for item in stats_pool[target]:
    for i in range(ref, 0, -1):
      x_query.append("x{}_{}".format(item, i))

  table = pandas.read_sql_query("SELECT * FROM {}".format(table_name), con).sample(frac=1)
  x_table = table[x_query]
  y_table = table[["y{}".format(target)]]

  con.close()

  return x_table, y_table

def create_referred_data_table(db, ref=4, pred=4, update=False):
  table_name = "_REF{}_PRED{}".format(ref, pred)
  con = sqlite3.connect(db)
  cur = con.cursor()
  cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}';".format(table_name))

  if cur.fetchone()[0] != 1 or update == True:
    header = []
    for item in REFERRED_CATEGORIES:
      for i in range(ref, 0, -1):
        header.append("x{}_{}".format(item, i))
    for item in PREDICT_CATEGORIES:
      header.append("y{}".format(item))

    table = pandas.DataFrame(columns=header)

    names = cur.execute('SELECT name FROM _PLAYER_INDEX').fetchall()
    count = 0;
    for name in names:
      player_table = pandas.read_sql_query("SELECT * FROM \"{}\"".format(name[0]), con)
      for i in range(ref, len(player_table.index) - pred):
        row = [];
        for item in REFERRED_CATEGORIES:
          for j in range(ref, 0, -1):
            data = player_table.iloc[i - j][item]
            if item == "MP":
              data = mp_to_second(data)
            row.append(data)
        for item in PREDICT_CATEGORIES:
          row.append(sum([player_table.iloc[k][item] for k in range(i, i + pred)]) / pred)
        table = table.append(pandas.Series(row, index=table.columns), ignore_index=True)
      count = count + 1
      if count % 50 == 0:
        print("Finished {} players".format(count))

    table.to_sql(table_name, con=con, index=False, if_exists="replace")

  con.close()

if __name__ == "__main__":
  create_referred_data_table("players_2018.db")
