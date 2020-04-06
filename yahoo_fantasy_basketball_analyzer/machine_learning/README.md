* Usage
  * `python db_generator.py` to create db for data processing (create `2018_player.db` by default)
  * `python parameter_informativeness.py` to identify which parameters are important
  * By default these model is using player's past 4 games stats to predict average "PTS" for next 4 games
  * `python linear_regression.py 2018_player.db` to run linear regression model, calculate theta by normal equation
  * `python torch_nn.py 2018_player.db` to run 10x3x1 Neural Network model by PyTorch
  * `python tensorflow_nn.py 2018_player.db` to run 10x3x1 Neural Network model by Tensorflow

