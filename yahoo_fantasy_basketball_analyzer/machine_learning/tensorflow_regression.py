import numpy as np
import pandas as pd
import sys
import tensorflow  as tf

TRAIN_PROPORTION=0.8
TEST_PROPORTION=0.2
LEARNING_RATE = 0.001
EPOCHS = 40

table = pd.read_csv(sys.argv[1]).dropna()
train_length = int(len(table.index) * TRAIN_PROPORTION)

x_value = table.iloc[: , 0: len(table.columns) - 1].assign(C = 1).values
x_train = np.array(x_value[0: train_length, :], dtype=np.float32)
x_test = np.array(x_value[train_length + 1: , :], dtype=np.float32)

y_value = table.iloc[:, len(table.columns) - 1].values.reshape(-1, 1)
y_train = np.array(y_value[0: train_length, :], dtype=np.float32)
y_test = np.array(y_value[train_length + 1: , :], dtype=np.float32)

model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(10, input_dim=x_train.shape[1], activation='relu'),
  tf.keras.layers.Dense(3, input_dim=10, activation='relu'),
  tf.keras.layers.Dense(1, input_dim=3, activation='relu')
])

model.compile(loss=tf.keras.losses.MeanSquaredError(),
              optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE))

model.fit(x_train, y_train, epochs=EPOCHS)

predicted = model.predict(x_test)

RMSE = ((predicted - y_test) ** 2).mean() ** .5

print("RMSE: {}".format(RMSE))
