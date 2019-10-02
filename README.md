## z_score_generator

* Description
  TBD

* Requirements
  * python3
  * yahoo_fantasy_api (https://pypi.org/project/yahoo-fantasy-api/).  
    ```pip install yahoo_fantasy_api```
  * yahoo_oauth:  
    ```pip intall yahoo_oauth```

* How to use
  1. Create `Oauth.json`: https://yahoo-oauth.readthedocs.io/en/latest/.  
     Put it at the same directory with `z_score_generator.py`
  2. Run the script: `python z_score_generator.py`.  
     It will ask the `year` and the `league_id` you would like to reference.
  3. It will generate two CSV files: `<year>_<league_id>_teams.csv` and `<year>_<league_id>_players.csv`. 
     Import them to google sheet or excel as CSV files to see the results.

* Example:
  ```
  Chun-Tses-MacBook-Pro:Yahoo_fantasy_basketball_analyzer cshao$ python3 z_score_generator.py
  [2019-10-02 16:25:20,412 DEBUG] [yahoo_oauth.yahoo_oauth.__init__] Checking
  [2019-10-02 16:25:20,412 DEBUG] [yahoo_oauth.yahoo_oauth.token_is_valid] ELAPSED TIME : 820.547641992569
  [2019-10-02 16:25:20,412 DEBUG] [yahoo_oauth.yahoo_oauth.token_is_valid] TOKEN IS STILL VALID
  What year [default: 2018]: 2018
  Which league {0: 385.l.26762} {1: 385.l.4806} [default: 0]: 0
  Chun-Tses-MacBook-Pro:Yahoo_fantasy_basketball_analyzer cshao$ ls
  2018_385.l.26762_players.csv	2018_385.l.26762_teams.csv	README.md	 z_score_generator.py  oauth2.json
  ```

* TODO:
  * Check if z-score for FG% and FT% is right
