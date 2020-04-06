* Usage
  * `python db_generator.py` to create db for data processing (create `players_2018.db` by default)
  * `python parameter_informativeness.py` to identify which parameters are important
  * By default these model is using player's past 4 games stats to predict "PTS" for next game (for the following three regression model)
  * `python linear_regression.py players_2018.db` to run linear regression model, calculate theta by normal equation
  * `python torch_nn.py players_2018.db` to run 10x3x1 Neural Network model by PyTorch
  * `python tensorflow_nn.py players_2018.db` to run 10x3x1 Neural Network model by Tensorflow

