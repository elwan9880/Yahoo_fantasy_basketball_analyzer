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
  1. Create `oauth.json` (https://yahoo-fantasy-api.readthedocs.io/en/latest/authentication.html).  
     1. Apply Yahoo API key (https://developer.yahoo.com/apps/create/). It will give you `consumer_key` and `consumer_secret`.   
     2. Create `oauth.json` under the same directory with `z_score_generator.py` with your api key:  
        ```
        {"consumer_key": <your consumer_key>, "consumer_secret": <your consumer_secret>}
        ```
  2. Run the script: `python z_score_generator.py`.  
     1. It will pop a web browser window with your verifier. Enter the verifier in terminal.
     2. Enter the `year` and the `league_id` you would like to reference.
  3. Two CSV files will be created: 
     * `<year>_<league_id>_teams.csv`: Team with average stats and z-scores in your league
     * `<year>_<league_id>_players.csv`: Players with average stats and z-scores
  4. Import CSV files to google sheet or excel as CSV format (comma separated) to see the results.

* Example:
  ```
  Chun-Tses-MacBook-Pro:Yahoo_fantasy_basketball_analyzer cshao$ python3 z_score_generator.py
  [2019-10-02 17:34:52,990 DEBUG] [yahoo_oauth.yahoo_oauth.__init__] Checking
  [2019-10-02 17:34:52,990 DEBUG] [yahoo_oauth.yahoo_oauth.handler] AUTHORISATION URL :  https://api.login.yahoo.com/oauth2/request_auth?client_secret=a0394eb953210395e94f4ce940df7c2b27f8e27b&redirect_uri=oob&response_type=code&client_id=dj0yJmk9Y2t1Q0FzSUx5S2YxJmQ9WVdrOVZFdzJZbmgwTkhVbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PThj
  ```
  A window will be poped with your verifier.
  ```
  Enter verifier : f36qzrr
  What year [default: 2018]: 2018
  Which league {0: 385.l.26762} {1: 385.l.4806} [default: 0]: 0
  Chun-Tses-MacBook-Pro:Yahoo_fantasy_basketball_analyzer cshao$ ls -al
  ```

* TODO:
  * Check if z-score for FG% and FT% is right
