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
