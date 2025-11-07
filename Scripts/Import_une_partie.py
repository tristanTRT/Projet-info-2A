# import_games.py
import csv
import requests
import os
import json
import time

def import_games(nb_parties_extraites=10, data_dir="/home/onyxia/work/Projet-info-2A/Data"):
    """
    Extrait les parties Lichess pour tous les users présents dans les CSV
    et écrit un fichier CSV par type de partie.
    Chaque ligne correspond à un utilisateur avec tous ses résultats.
    """
    os.makedirs(data_dir, exist_ok=True)

    type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]
    headers = {"Accept": "application/x-ndjson"}

    for format_partie in type_parties:
        chemin_fichier = os.path.join(data_dir, f"{format_partie.capitalize()}_games.csv")
        users_file = os.path.join(data_dir, f"{format_partie.capitalize()}_users.csv")

        with open(chemin_fichier, "w", newline="", encoding="utf-8") as f_out, \
             open(users_file, newline="", encoding="utf-8") as f_users:

            writer = csv.writer(f_out)
            # En-tête : username + parties
            header = ["username"] + [f"partie_{i+1}" for i in range(nb_parties_extraites)]
            writer.writerow(header)

            reader = csv.reader(f_users)
            for ligne in reader:
                username = ligne[0]
                url = f"https://lichess.org/api/games/user/{username}"
                params = {
                    "max": nb_parties_extraites,
                    "rated": "true",
                    "perfType": format_partie,
                }

                r = requests.get(url, params=params, headers=headers)
                if r.status_code != 200:
                    print("Erreur", r.status_code, username)
                    continue

                results = []
                for line in r.text.strip().split("\n"):
                    if not line.strip():  # ignorer lignes vides
                        continue
                    game_data = json.loads(line)
                    player_color = "white" if game_data["players"]["white"]["user"]["id"].lower() == username.lower() else "black"
                    winner = game_data.get("winner")
                    result = "Win" if winner == player_color else "Loss"
                    results.append(result)

                writer.writerow([username] + results)
                time.sleep(1)  # éviter le 429 de l'API

    print("Import des parties terminé.")