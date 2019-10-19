## Yahoo Fantasy Basketball Analyzer

* Description
  * Average stats and Z-scores for teams in your Yahoo Fantasy Basketball league.
  * Average stats and Z-scores for NBA players.
  * Trade Analyzer for your Yahoo Fantasy Basketball league.

* Requires
  * python3.7

* Installation
  ```
  git clone https://github.com/elwan9880/Yahoo_fantasy_basketball_analyzer.git
  cd Yahoo_fantasy_basketball_analyzer
  python setup.py install
  ```

* How to use
  1. Create `oauth2.json` (https://yahoo-fantasy-api.readthedocs.io/en/latest/authentication.html).
     1. Apply Yahoo API key (https://developer.yahoo.com/apps/create/). Select all read/write permission. It will give you `consumer_key` and `consumer_secret`.
     2. Create `oauth.json` under the same directory with `yahoo_fantasy_basketball_analyzer.py` with your api key:
        ```
        {"consumer_key": <your consumer_key>, "consumer_secret": <your consumer_secret>}
        ```
  2. Run the script: `python yahoo_fantasy_basketball_analyzer.py`.
     1. It will pop a web browser window with your verifier. Enter the verifier in terminal.
     2. Enter the `year` and the `league_id` you would like to reference.
  3. Choose the mode for analysis:
     * `Fantasy Team Performance Analyzer`: Create `<season>_<league_name>_teams.csv`: Team performance with average stats and z-scores in your league
     * `Fantasy Trade Analyzer`: create `<season>_<league_name>_<team_A>_<team_B>.csv`: Trade Analysis
     * `NBA Players Performance Analyzer`: create `<season>_players.csv`: Players performance with average stats and z-scores
  4. Import CSV files to google sheet or excel as CSV format (comma separated) to see the results.

* Example:
  ```
  Chun-Tses-MacBook-Pro:Yahoo_fantasy_basketball_analyzer cshao$ python3 yahoo_fantasy_basketball_analyzer.py
  ? Please choose a mode:  NBA Players Performance Analyzer
  ? And a NBA season:  2018-2019
  ? Select categories for analysis (default 9CAT):  done (9 selections)
  Parsing Basketball Reference NBA players total stats ... Done
  Calculating player performace ... Done
  Finished! please import "2018-2019_players.csv" to excel as CSV format to see the results.
  ```
