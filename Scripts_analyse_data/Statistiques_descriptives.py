import pandas as pd

# Chemin vers ton fichier CSV
chemin_fichier = "/home/onyxia/work/Projet-info-2A/Data/"


type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]
dfs = {}

for format_partie in type_parties:
    fichier = f"/home/onyxia/work/Projet-info-2A/Data/{format_partie.capitalize()}_games.csv"
    dfs[f"{format_partie}df"] = pd.read_csv(fichier)



print(dfs)