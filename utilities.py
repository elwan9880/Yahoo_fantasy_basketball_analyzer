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

BR_TO_YFB_STATS_NAME_MAP = {"G":   "GP",
                            "GS":  "GS",
                            "MP":  "MIN",
                            "FG":  "FGM",
                            "FGA": "FGA",
                            "FG%": "FG%",
                            "FT":  "FTM",
                            "FTA": "FTA",
                            "FT%": "FT%",
                            "3P":  "3PTM",
                            "3PA": "3PTA",
                            "3P%": "3PT%",
                            "PTS": "PTS",
                            "DRB": "DREB",
                            "ORB": "OREB",
                            "TRB": "REB",
                            "AST": "AST",
                            "STL": "ST",
                            "BLK": "BLK",
                            "TOV": "TO",
                            "PF":  "PF"}

def divide(numerator, denominator):
  return float(numerator) / float(denominator) if float(denominator) != 0 else 0

def formalize_name(name):
  name = unidecode.unidecode(name)
  name = name.replace(".", "").replace(" Jr", "").replace(" III", "")
  name = name.replace("Jakob Poltl", "Jakob Poeltl").replace("Taurean Waller-Prince", "Taurean Prince").replace("Moe Harkless", "Maurice Harkless")
  return name
