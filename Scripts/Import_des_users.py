# import_users.py
import csv
import os
import requests

type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]

def extraction_users_leaderboard(nombre_sample, format_partie, parsing):
    nbusermax = parsing * nombre_sample
    url = f"https://lichess.org/api/player/top/{nbusermax}/{format_partie}"
    req = requests.get(url).json()
    users = req["users"]
    subset = users[::parsing]
    return [user["id"] for user in subset]

def import_users(nombre_sample=10, parsing=5, data_dir="/home/onyxia/work/Projet-info-2A/Data"):
    """
    Fonction pour extraire les users Lichess et écrire les CSV dans data_dir.
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for format_partie in type_parties:
        filepath = os.path.join(data_dir, f"{format_partie.capitalize()}_users.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for elem in extraction_users_leaderboard(nombre_sample, format_partie, parsing):
                writer.writerow([elem])

    print("Import des utilisateurs terminé.")