import numpy as np
import pandas as pd
import sys
import tensorflow  as tf
import utils

TRAIN_PROPORTION=0.8
TEST_PROPORTION=0.2
TARGET="PTS"
REFERRED_STATS=["FGA", "PTS", "FG", "GmSc", "MP", "FT", "FTA", "TOV", "USG%"]
REFERRED_GAMES=4
PREDICTED_GAMES=4
LEARNING_RATE = 0.01
EPOCHS = 40

x_table, y_table = utils.create_dataset(sys.argv[1], ref=REFERRED_GAMES, pred=PREDICTED_GAMES, target=TARGET, ref_stats=REFERRED_STATS)

train_length = int(len(x_table.index) * TRAIN_PROPORTION)
x_value = x_table.assign(C = 1).values
y_value = y_table.values.reshape(-1, 1)

x_train = np.array(x_value[0: train_length, :], dtype=np.float32)
x_test = np.array(x_value[train_length + 1: , :], dtype=np.float32)
y_train = np.array(y_value[0: train_length, :], dtype=np.float32)
y_test = np.array(y_value[train_length + 1: , :], dtype=np.float32)

model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(10, input_dim=x_train.shape[1], activation='relu'),
  tf.keras.layers.Dense(3, input_dim=10, activation='relu'),
  tf.keras.layers.Dense(1, input_dim=3)
])

model.compile(loss=tf.keras.losses.MeanSquaredError(),
              optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE))

model.fit(x_train, y_train, epochs=EPOCHS)

predicted = model.predict(x_test)

RMSE = ((predicted - y_test) ** 2).mean() ** .5

print("RMSE for predicted {}: {}".format(TARGET, RMSE))
