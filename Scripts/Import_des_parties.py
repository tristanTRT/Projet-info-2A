import csv
import requests
import os
import json


#Paramétrage 
type_parties = "bullet" # A modifier dans la fonction, il faudra itérer son appel sur element in type_parties (et faire une lsite des types de parties dusponibles)
nb_parties_extraites = int(input("Quel est le nombre de parties à extraire par joueur ?"))


#Tentative Tristan
"""
def creation_csv_parties (partie_format): 
    with open(f"/home/onyxia/work/Projet-info-2A/Data/{partie_format.capitalize()}_games.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for user in partie_format.capitalize().csv:
            url_Lichess_example = f"https://lichess.org/api/games/user/{username}"
            req = requests.get(url_Lichess_example).json()
            writer.writerow([elem])
"""


def creation_csv_parties(partie_format, nb_parties_extraites):
    dossier_data = "/home/onyxia/work/Projet-info-2A/Data"
    os.makedirs(dossier_data, exist_ok=True)

    # Lecture des usernames depuis le CSV existant
    input_csv = os.path.join(dossier_data, f"{partie_format.capitalize()}_users.csv")
    usernames = []
    with open(input_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # éviter les lignes vides
                usernames.append(row[0])

    # Création du CSV de sortie
    output_csv = os.path.join(dossier_data, f"{partie_format.capitalize()}_games.csv")
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["username", "gameId", "victory"])  # header

        for username in usernames:
            url = f"https://lichess.org/api/games/user/{username}"
            headers = {"Accept": "application/x-ndjson"}
            params = {
                "max": nb_parties_extraites,
                "perfType": partie_format.lower(),
                "finished": True
            }
            r = requests.get(url, headers=headers, params=params, stream=True)
            for line in r.iter_lines():
                if not line:
                    continue  # ignore les lignes vides
                line = line.strip()
                if not line:
                    continue  # ignore les lignes avec juste espaces
                try:
                    game = json.loads(line)
                except json.JSONDecodeError:
                    continue  # ignore si la ligne n'est pas du JSON valide

                try:
                    if "user" not in game["players"]["white"] or "user" not in game["players"]["black"]:
                        continue
                    user_color = "white" if game["players"]["white"]["user"]["name"].lower() == username.lower() else "black"
                    result = game["players"][user_color].get("result")
                    if result is None:
                        continue
                    victoire = 1 if result == "win" else 0
                    writer.writerow([username, game["id"], victoire])
                except KeyError:
                    continue


print(creation_csv_parties(type_parties,nb_parties_extraites))

"""
# Exemple d'appel
creation_csv_parties("Blitz", nb_parties=10)



for partie_format in type_parties : 
    creation_csv_parties(partie_format)

"""