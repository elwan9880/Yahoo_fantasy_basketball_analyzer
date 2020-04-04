import pandas as pd
import csv
from os import listdir
import sys
import re

def find_csv_filenames(path_to_dir, suffix=".csv"):
  filenames = listdir(path_to_dir)
  return [filename for filename in filenames if filename.endswith( suffix )]

csv_names = find_csv_filenames(".")

for csv in csv_names:
  table = pd.read_csv(csv)
  table = table.ix[:, 0:5]
  export_csv = table.to_csv("{}_schedule.csv".format(csv.split(".")[0]), index=False)


