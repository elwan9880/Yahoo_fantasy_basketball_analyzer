## yahoo_fantasy_basketball_analyzer

* Description  
  Generate average stats and z-scores from all teams in your Yahoo fantasy basketball league.  

* Requirements
  * python3
  * yahoo_fantasy_api (https://pypi.org/project/yahoo-fantasy-api/).  
    ```pip install yahoo_fantasy_api```
  * yahoo_oauth:  
    ```pip install yahoo_oauth```
  * lxml
  * bs4
  * pandas
  * unidecode

* How to use
  1. Create `oauth2.json` (https://yahoo-fantasy-api.readthedocs.io/en/latest/authentication.html).  
     1. Apply Yahoo API key (https://developer.yahoo.com/apps/create/). It will give you `consumer_key` and `consumer_secret`.   
     2. Create `oauth.json` under the same directory with `yahoo_fantasy_basketball_analyzer.py` with your api key:  
        ```
        {"consumer_key": <your consumer_key>, "consumer_secret": <your consumer_secret>}
        ```
  2. Run the script: `python yahoo_fantasy_basketball_analyzer.py`.  
     1. It will pop a web browser window with your verifier. Enter the verifier in terminal.
     2. Enter the `year` and the `league_id` you would like to reference.
  3. Two CSV files will be created: 
     * `<season>_<league_name>_teams.csv`: Team with average stats and z-scores in your league
     * `<season>_<league_name>_players.csv`: Players with average stats and z-scores
  4. Import CSV files to google sheet or excel as CSV format (comma separated) to see the results.

* Example:
  ```
  Chun-Tses-MacBook-Pro:Yahoo_fantasy_basketball_analyzer cshao$ python3 yahoo_fantasy_basketball_analyzer.py
  [2019-10-02 17:34:52,990 DEBUG] [yahoo_oauth.yahoo_oauth.__init__] Checking
  [2019-10-02 17:34:52,990 DEBUG] [yahoo_oauth.yahoo_oauth.handler] AUTHORISATION URL :  https://api.login.yahoo.com/oauth2/request_auth?client_secret=a0394eb953210395e94f4ce940df7c2b27f8e27b&redirect_uri=oob&response_type=code&client_id=dj0yJmk9Y2t1Q0FzSUx5S2YxJmQ9WVdrOVZFdzJZbmgwTkhVbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PThj
  ```
  A window will be poped with your verifier.
  ```
  Enter verifier : f36qzrr
  Choose a season {0: 2018-2019} {1: 2017-2018} {2: 2016-2017} {3: 2015-2016} [default: 0]:
  Choose a league {0: 5566 Forever} {1: Avalon} [default: 0]:
  You select: Season: 2018-2019, League: 5566 Forever
  Parsing Basketball Reference 2018-2019 NBA players total stats ... Done
  Retrieving NBA data and calculating player performace... Done
  Calculating Fantasy team performace ... Done
  Finished! please import "2018-2019_5566 Forever_teams.csv" and "2018-2019_5566 Forever_players.csv" to excel as CSV format to see the results.
  ```
