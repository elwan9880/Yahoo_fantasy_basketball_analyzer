from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
import csv

year = 2018
br_url = "https://www.basketball-reference.com/"
team_list = ["PHI", "TOR", "MIA", "BOS", "CLE", "ORL", "MIL", "CHO", "ATL", "DET", "WAS", "BRK", "IND", "CHI", "NYK", "UTA", "HOU", "DAL", "SAS", "MIN", "LAL", "LAC", "PHO", "POR", "DEN", "GSW", "MEM", "NOP", "OKC", "SAC"]
duplicated_data_stats = {"ranker", "game_season", "game_location", "date_game", "opp_id", "game_result", "pts", "opp_pts"}

for team in team_list:
  basic_url = "{}/teams/{}/{}/gamelog/".format(br_url, team, year + 1)
  advanced_url = "{}/teams/{}/{}/gamelog-advanced/".format(br_url, team, year + 1)

  basic_soup = BeautifulSoup(urlopen(basic_url), "lxml")
  advanced_soup = BeautifulSoup(urlopen(advanced_url), "lxml")

  basic_table = basic_soup.find_all("table", {"id": "tgl_basic"})[0]
  advanced_table = advanced_soup.find_all("table", {"id": "tgl_advanced"})[0]

  basic_thead = basic_table.find_all("thead")[0].find_all("tr")[1]
  advanced_thead = advanced_table.find_all("thead")[0].find_all("tr")[1]
  basic_header = ["opp" + th.get_text() if th.get("data-over-header") and th["data-over-header"] == "Opponent" and th.get_text() != "Opp" else th.get_text() for th in basic_thead.find_all("th")]
  advanced_header = [th["data-over-header"][0].lower() + th.get_text() if th.get("data-over-header") and (th["data-over-header"] == "Defensive Four Factors" or th["data-over-header"] == "Offensive Four Factors") else th.get_text()
                     for th in advanced_thead.find_all("th") if th["data-stat"] not in duplicated_data_stats]
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

  with open("{}/team/{}.csv".format(year, team), "w", newline = "") as f:
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    wr.writerow(header)
    for item in gamelog:
      wr.writerow(item)

  f.close()
