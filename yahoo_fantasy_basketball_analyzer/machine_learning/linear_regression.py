import pandas as pd
from numpy.linalg import inv
import sys
import utils

TRAIN_PROPORTION=0.8
TEST_PROPORTION=0.2
TARGET="PTS"

# Using CSV as input
# table = pd.read_csv(sys.argv[1]).dropna().sample(frac=1)
# train_length = int(len(table.index) * TRAIN_PROPORTION)
# x_value = table.iloc[:, 0: len(table.columns) - 1].assign(C = 1).values
# y_value = table.iloc[:, len(table.columns) - 1].values.reshape(-1, 1)

# Using db as input
utils.create_referred_data_table(sys.argv[1])
x_table, y_table = utils.db_to_df(sys.argv[1], target=TARGET)
train_length = int(len(x_table.index) * TRAIN_PROPORTION)
x_value = x_table.assign(C = 1).values
y_value = y_table.values.reshape(-1, 1)

x_train = x_value[0: train_length, :]
x_test = x_value[train_length + 1: , :]
y_train = y_value[0: train_length, :]
y_test = y_value[train_length + 1: , :]

print("y.mean: {}".format(y_value.mean()))
if (len(sys.argv) > 2) and (sys.argv[2] == "baseline"):
  y_avg = x_table.filter(regex=("x{}_*".format(TARGET))).mean(axis=1).values.reshape(-1, 1)
  print("RMSE for average: {}".format(((y_avg - y_value) ** 2).mean() ** .5))

theta = inv(x_train.T.dot(x_train)).dot(x_train.T).dot(y_train)

y_pred = x_test.dot(theta)

print("RMSE for prediction: {}".format(((y_pred - y_test) ** 2).mean() ** .5))
