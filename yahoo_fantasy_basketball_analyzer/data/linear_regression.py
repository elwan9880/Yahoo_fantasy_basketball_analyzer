import pandas as pd
from numpy.linalg import inv
import sys

table = pd.read_csv(sys.argv[1]).dropna()

X = table.iloc[:, 0: len(table.columns) - 1].values
y = table.iloc[:, len(table.columns) - 1].values.reshape(-1, 1)
theta = inv(X.T.dot(X)).dot(X.T).dot(y)

y_pred = X.dot(theta)

RMSE = ((y_pred - y) ** 2).mean() ** .5

print("theta: {}".format(theta))
print("RMSE: {}".format(RMSE))
