from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
import csv

year = 2018
br_url = "https://www.basketball-reference.com/"

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

  player_gamelog_url = "{}players/{}/{}/gamelog/{}".format(br_url, player_id[0], player_id, year + 1)

  player_html = urlopen(player_gamelog_url)
  player_soup = BeautifulSoup(player_html, "lxml")

  regular_season_table = player_soup.find_all("table", {"id": "pgl_basic"})[0]

  thead = regular_season_table.find_all("thead")[0]
  player_head = [th.get_text() for th in thead.find_all("th")]

  player_gamelog = []
  tbody = regular_season_table.find_all("tbody")[0]
  player_rows = tbody.find_all("tr")
  for row in player_rows:
    if not row.get("id"):
      continue
    player_gamelog.append([td.get_text() for td in row.find_all(["th", "td"])])

  with open("{}.csv".format(player_name), "w", newline = "") as f:
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    wr.writerow(player_head)
    for item in player_gamelog:
      wr.writerow(item)

  f.close()
