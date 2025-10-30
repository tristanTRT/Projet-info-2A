import csv
import os
type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]
nombre_sample = int(input("Nombre de joueurs extraits"))
parsing = int(input("On prend un joueur tous les..."))


def extraction_users_leaderboard (nombre_sample, type_parties, parsing) :
    #Extraction des IDs pour les users du top X d'un type de parties Y 
    import requests
    nbusermax = parsing * nombre_sample
    url_Lichess_example = f"https://lichess.org/api/player/top/{nbusermax}/{type_parties}"
    req = requests.get(url_Lichess_example).json()
    users = req['users']
    subset = users[::parsing] 
    ids = [user['id'] for user in subset]
    return(ids)







# Export dans un CSV dans projet_info

# Vérifier si le dossier existe
if not os.path.exists("/home/onyxia/work/Projet-info-2A/Data"):
    os.makedirs(chemin_dossier)


for format_partie in type_parties :
    with open(f"/home/onyxia/work/Projet-info-2A/Data/{format_partie.capitalize()}_users.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for elem in extraction_users_leaderboard(nombre_sample,format_partie, parsing):
            writer.writerow([elem])