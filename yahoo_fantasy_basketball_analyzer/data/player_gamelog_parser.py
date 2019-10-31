from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
import csv

year = 2018
br_url = "https://www.basketball-reference.com/"
duplicated_data_stats = {"ranker", "game_season", "date_game", "age", "team_id", "game_result", "game_location", "opp_id", "gs", "mp", "game_score"}

url = "{}leagues/NBA_{}_totals.html".format(br_url, year + 1)
html = urlopen(url)
soup = BeautifulSoup(html, "lxml")
headers = [th.get_text() for th in soup.find_all('tr', limit=2)[0].find_all('th')]
headers = headers[1:]
rows = soup.find_all('tr')[1:]

player_id_list = []

for i in range(len(rows)):
  data = rows[i].find_all("td")
  if not data:
    continue
  player_id = data[0]["data-append-csv"]
  if [player_id] == player_id_list[-1:]:
    continue

  player_id_list.append(player_id)
  player_name = data[0].get_text()

  basic_url = "{}players/{}/{}/gamelog/{}".format(br_url, player_id[0], player_id, year + 1)
  advanced_url = "{}players/{}/{}/gamelog-advanced/{}".format(br_url, player_id[0], player_id, year + 1)

  basic_soup = BeautifulSoup(urlopen(basic_url), "lxml")
  advanced_soup = BeautifulSoup(urlopen(advanced_url), "lxml")

  basic_table = basic_soup.find_all("table", {"id": "pgl_basic"})[0]
  advanced_table = advanced_soup.find_all("table", {"id": "pgl_advanced"})[0]

  basic_thead = basic_table.find_all("thead")[0]
  advanced_thead = advanced_table.find_all("thead")[0]
  basic_header = [th.get_text() for th in basic_thead.find_all("th")]
  advanced_header = [th.get_text() for th in advanced_thead.find_all("th") if th["data-stat"] not in duplicated_data_stats]
  header = basic_header + advanced_header

  basic_tbody = basic_table.find_all("tbody")[0]
  basic_rows = basic_tbody.find_all("tr")
  advanced_tbody = advanced_table.find_all("tbody")[0]
  advanced_rows = advanced_tbody.find_all("tr")
  if len(advanced_rows) != len(basic_rows):
    print("WARNING: {} has different number of rows for advanced ({}) and basic ({}) stats".format(len(advanced_rows, len(basic_rows))))
    continue

  gamelog = []
  for i in range(len(basic_rows)):
    if basic_rows[i].get("id") and advanced_rows[i].get("id"):
      gamelog.append([td.get_text() for td in basic_rows[i].find_all(["th", "td"])] +
                     [td.get_text() for td in advanced_rows[i].find_all(["th", "td"]) if td["data-stat"] not in duplicated_data_stats])

  with open("{}/{}.csv".format(year, player_name), "w", newline = "") as f:
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    wr.writerow(header)
    for item in gamelog:
      wr.writerow(item)

  f.close()
