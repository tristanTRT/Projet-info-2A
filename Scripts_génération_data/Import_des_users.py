# import_users.py
import csv
import os
import requests

type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]

def extraction_users_leaderboard(nombre_sample, format_partie, parsing):
    nbusermax = parsing * nombre_sample
    url = f"https://lichess.org/api/player/top/{nbusermax}/{format_partie}"
    # Demande à l'API parsing x sample nb de users 
    req = requests.get(url).json()
    users = req["users"]
    subset = users[::parsing] 
    # garde dans le subset 1 user sur parsing 
    return [user["id"] for user in subset]
    #renvoie une liste des joueurs de longueur nombre_sample

def import_users(nombre_sample, parsing, data_dir="/home/onyxia/work/Projet-info-2A/Data"):
    """
    Fonction pour extraire les users Lichess et écrire les CSV dans data_dir.
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for format_partie in type_parties:
        filepath = os.path.join(data_dir, f"{format_partie.capitalize()}_users.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            #pour chaque élément dans la liste des joueurs on l'écrit dans le fichier games
            for elem in extraction_users_leaderboard(nombre_sample, format_partie, parsing):
                writer.writerow([elem])

    print("Import des utilisateurs terminé.")