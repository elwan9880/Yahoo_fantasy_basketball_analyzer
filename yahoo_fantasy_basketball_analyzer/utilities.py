import unidecode

STAT_CATEGORIES = {"GP":   ["GP"],
                   "GS":   ["GS"],
                   "MIN":  ["MIN"],
                   "FGM":  ["FGM"],
                   "FGA":  ["FGA"],
                   "FG%":  ["FGM", "FGA"],
                   "FTM":  ["FTM"],
                   "FTA":  ["FTA"],
                   "FT%":  ["FTM", "FTA"],
                   "3PTM": ["3PTM"],
                   "3PTA": ["3PTA"],
                   "3PT%": ["3PTM", "3PTA"],
                   "PTS":  ["PTS"],
                   "DREB": ["DREB"],
                   "OREB": ["OREB"],
                   "REB":  ["REB"],
                   "AST":  ["AST"],
                   "ST":   ["ST"],
                   "BLK":  ["BLK"],
                   "TO":   ["TO"],
                   "A/T":  ["AST", "TO"],
                   "PF" :  ["PF"]}

def divide(numerator, denominator):
  return float(numerator) / float(denominator) if float(denominator) != 0 else 0

def formalize_name(name):
  name = unidecode.unidecode(name)
  name = name.replace(".", "").replace(" Jr", "").replace(" III", "")
  name = name.replace("Jakob Poltl", "Jakob Poeltl").replace("Taurean Waller-Prince", "Taurean Prince").replace("Moe Harkless", "Maurice Harkless")
  return name

def output_players_csv_file(file_name, players, stat_categories, f = None):
  f = f or open(file_name, "w+")

  # Write titles
  z_categories = list(map(lambda cat: "z" + cat, stat_categories))
  titles = ["Player"] + stat_categories + z_categories + ["zTotal"]
  write_lines(f, titles)

  #write players
  for name, player in players.items():
    f.write(name)
    write_lines(f, player.get_stats_with_selected_category(stat_categories), indents = 1)
  f.close()

def output_league_csv_file(file_name, teams, stat_categories, f = None):
  f = f or open(file_name, "w+")

  z_categories = list(map(lambda cat: "z" + cat, stat_categories))

  # Write team stats
  titles = ["Manager"] + stat_categories + z_categories + ["zTotal"]
  write_lines(f, titles)
  for team_name, team in teams.items():
    write_lines(f, [team_name] + team.get_stats_with_selected_category(stat_categories))
  f.write("\n")

  # Write team player stats
  for team_name, team in teams.items():
    titles = [team_name] + stat_categories + z_categories + ["zTotal"]
    write_lines(f, titles)
    for player_name, player in team.get_players().items():
      write_lines(f, [player_name] + player.get_stats_with_selected_category(stat_categories))
    f.write("\n")
  f.close()

def write_lines(f, list, indents = 0):
  if list == None or f == None:
    return
  for i in range(0, indents):
    f.write(",")
  for item in list:
    if isinstance(item, float):
      f.write("{0:.3f},".format(item))
    else:
      f.write("{},".format(item))
  f.write("\n")


