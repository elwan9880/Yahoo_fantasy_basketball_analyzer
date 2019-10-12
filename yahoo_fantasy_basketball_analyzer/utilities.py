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

def create_csv_output_file(file_name, dictionary, stat_categories):
  f = open(file_name, "w+")
  f.write(",")
  for stat_name in stat_categories:
    f.write("{},".format(stat_name))
  for stat_name in stat_categories:
    f.write("z{},".format(stat_name))
  f.write("zTotal,\n")

  for key, item in dictionary.items():
    total_z_score = 0;
    f.write("{},".format(key))
    for stat_name in stat_categories:
      f.write("{0:.2f},".format(item.get_average_stats()[stat_name]))
    for stat_name in stat_categories:
      f.write("{0:.2f},".format(item.get_z_scores()[stat_name]))
      total_z_score += item.get_z_scores()[stat_name]
    f.write("{0:.2f},\n".format(divide(total_z_score, len(stat_categories))))
  f.close()

