import csv
import os
nombre_sample = int(input("Nombre de joueurs extraits"))


def extraction_users_leaderboard (nombre_sample, type_parties) :
    #Extraction des IDs pour les users du top X d'un type de parties Y 
    import requests
    url_Lichess_example = f"https://lichess.org/api/player/top/{nombre_sample}/{type_parties}"
    req = requests.get(url_Lichess_example).json()
    ids = [user['id'] for user in req['users']]
    return(ids)



type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]
# Export dans un CSV dans projet_info

os.makedirs("/home/onyxia/work/Projet-info-2A/Data")


for format_partie in type_parties :
    with open(f"/home/onyxia/work/Projet-info-2A/Data/{format_partie.capitalize()}.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for elem in extraction_users_leaderboard(nombre_sample,format_partie):
            writer.writerow([elem])
