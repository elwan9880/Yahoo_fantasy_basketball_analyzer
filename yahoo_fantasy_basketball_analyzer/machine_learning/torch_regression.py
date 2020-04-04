import pandas as pd
import numpy as np
import sys

import torch
from torch.autograd import Variable
import torch.nn.functional as F
from matplotlib import pyplot as plt

class linearRegression(torch.nn.Module):
  def __init__(self, inputSize, outputSize):
    super(linearRegression, self).__init__()
    self.linear = torch.nn.Linear(inputSize, outputSize, bias=True)

  def forward(self, x):
    out = self.linear(x)
    return out

class Net(torch.nn.Module):
  def __init__(self, n_feature, n_hidden, n_output):
    super(Net, self).__init__()
    self.hidden = torch.nn.Linear(n_feature, n_hidden)   # hidden layer
    self.predict = torch.nn.Linear(n_hidden, n_output, bias=True)   # output layer

  def forward(self, x):
    x = F.relu(self.hidden(x))      # activation function for hidden layer
    x = self.predict(x)             # linear output
    return x

table = pd.read_csv(sys.argv[1]).dropna()
x_value = table.iloc[:, 0: len(table.columns) - 1].assign(C = 1).values
x_train = np.array(x_value, dtype=np.float32)

y_value = table.iloc[:, len(table.columns) - 1].values.reshape(-1, 1)
y_train = np.array(y_value, dtype=np.float32)

input_dim = x_train.shape[1]        # takes variable 'x'
output_dim = y_train.shape[1]       # takes variable 'y'
learning_rate = 0.001
epochs = 10000

# model = linearRegression(input_dim, output_dim)
# model = Net(n_feature=input_dim, n_hidden=3, n_output=output_dim)
model = torch.nn.Sequential (
          torch.nn.Linear(input_dim, 3),
          torch.nn.LeakyReLU(),
          torch.nn.Linear(3, 3),
          torch.nn.LeakyReLU(),
          torch.nn.Linear(3, output_dim),
        )
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=0.01)

for epoch in range(epochs):
  inputs = Variable(torch.from_numpy(x_train))
  labels = Variable(torch.from_numpy(y_train))

  # Clear gradient buffers because we don't want any gradient from previous epoch to carry forward, dont want to cummulate gradients
  optimizer.zero_grad()

  # get output from the model, given the inputs
  outputs = model(inputs)

  # get loss for the predicted output
  loss = criterion(outputs, labels)

  # get gradients w.r.t to parameters
  loss.backward()

  # update parameters
  optimizer.step()

  if epoch % 1000 == 0:
    print('epoch {}, loss {}'.format(epoch, loss.item()))

with torch.no_grad(): # we don't need gradients in the testing phase
  predicted = model(inputs).data.numpy()
  print(predicted)

RMSE = ((predicted - y_train) ** 2).mean() ** .5
print("RMSE: {}".format(RMSE))
