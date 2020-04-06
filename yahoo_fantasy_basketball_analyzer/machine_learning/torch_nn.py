import pandas as pd
import numpy as np
import sys
import utils

import torch
from torch.autograd import Variable
import torch.nn.functional as F

# class linearRegression(torch.nn.Module):
#   def __init__(self, inputSize, outputSize):
#     super(linearRegression, self).__init__()
#     self.linear = torch.nn.Linear(inputSize, outputSize, bias=True)
#
#   def forward(self, x):
#     out = self.linear(x)
#     return out
#
# class Net(torch.nn.Module):
#   def __init__(self, n_feature, n_hidden, n_output):
#     super(Net, self).__init__()
#     self.hidden = torch.nn.Linear(n_feature, n_hidden)   # hidden layer
#     self.predict = torch.nn.Linear(n_hidden, n_output, bias=True)   # output layer
#
#   def forward(self, x):
#     x = F.relu(self.hidden(x))      # activation function for hidden layer
#     x = self.predict(x)             # linear output
#     return x

TRAIN_PROPORTION=0.8
TEST_PROPORTION=0.2
TARGET="PTS"
REFERRED_STATS=["FGA", "PTS", "FG", "GmSc", "MP", "FT", "FTA", "TOV", "USG%"]
REFERRED_GAMES=4
PREDICTED_GAMES=4
LEARNING_RATE = 0.001
EPOCHS = 10000

utils.create_referred_data_table(sys.argv[1])
x_table, y_table = utils.db_to_df(sys.argv[1], ref=REFERRED_GAMES, pred=PREDICTED_GAMES, target=TARGET, ref_stats=REFERRED_STATS)
train_length = int(len(x_table.index) * TRAIN_PROPORTION)
x_value = x_table.assign(C = 1).values
y_value = y_table.values.reshape(-1, 1)

x_train = np.array(x_value[0: train_length, :], dtype=np.float32)
x_test = np.array(x_value[train_length + 1: , :], dtype=np.float32)
y_train = np.array(y_value[0: train_length, :], dtype=np.float32)
y_test = np.array(y_value[train_length + 1: , :], dtype=np.float32)

# model = linearRegression(input_dim, output_dim)
# model = Net(n_feature=input_dim, n_hidden=3, n_output=output_dim)
model = torch.nn.Sequential (
          torch.nn.Linear(x_train.shape[1], 10),
          torch.nn.LeakyReLU(),
          torch.nn.Linear(10, 3),
          torch.nn.LeakyReLU(),
          torch.nn.Linear(3, 1)
        )
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)

for epoch in range(EPOCHS):
  inputs = Variable(torch.from_numpy(x_train))
  labels = Variable(torch.from_numpy(y_train))

  optimizer.zero_grad()

  outputs = model(inputs)

  loss = criterion(outputs, labels)

  loss.backward()

  optimizer.step()

  if epoch % 1000 == 0:
    print('epoch {}, loss {}'.format(epoch, loss.item()))

with torch.no_grad(): # we don't need gradients in the testing phase
  predicted = model(Variable(torch.from_numpy(x_test))).data.numpy()
  RMSE = ((predicted - y_test) ** 2).mean() ** .5
  print("RMSE for predicted {}: {}".format(TARGET, RMSE))

