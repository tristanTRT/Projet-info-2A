# Import_des_users_parquet.py
import requests
import pandas as pd
import time
import os

type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]

# Répertoire des données
DATA_DIR = os.path.join(os.path.dirname(__file__), "../Data")
os.makedirs(DATA_DIR, exist_ok=True)

def extraction_users_leaderboard(nombre_sample, format_partie, parsing, token, max_retries=5):
    """
    Récupère les meilleurs joueurs pour un format donné depuis l'API Lichess
    """
    nbusermax = parsing * nombre_sample
    url = f"https://lichess.org/api/player/top/{nbusermax}/{format_partie}"
    headers = {"Authorization": f"Bearer {token}"}

    retries = 0
    while retries < max_retries:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            break
        elif r.status_code == 429:  # trop de requêtes
            wait_time = int(r.headers.get("Retry-After", 3))
            print(f"429 reçu pour leaderboard {format_partie}. Attente {wait_time}s ({retries+1}/{max_retries})")
            time.sleep(wait_time)
            retries += 1
        else:
            print("Erreur", r.status_code, format_partie)
            return []

    else:
        print(f"Échec après {max_retries} retries pour leaderboard {format_partie}")
        return []

    req = r.json()
    users = req.get("users", [])
    subset = users[::parsing]

    user_data = []
    for user in subset:
        user_id = user.get("id")
        perfs = user.get("perfs", {})
        elo = perfs.get(format_partie, {}).get("rating", None)
        user_data.append({"user_id": user_id, "elo": elo})

    return user_data

def import_users_df(nombre_sample, parsing, token):
    """
    Récupère les utilisateurs pour tous les formats et sauvegarde un Parquet par type de partie
    """
    dfs = {}
    for format_partie in type_parties:
        print(f"Extraction des joueurs pour {format_partie}…")
        user_list = extraction_users_leaderboard(nombre_sample, format_partie, parsing, token)
        df = pd.DataFrame(user_list, columns=["user_id", "elo"]).reset_index(drop=True)
        dfs[format_partie] = df

        # 🔹 Sauvegarde au format Parquet
        output_file = os.path.join(DATA_DIR, f"users_{format_partie}.parquet")
        df.to_parquet(output_file, index=False)
        print(f"Sauvegardé {len(df)} joueurs dans {output_file}\n")

        time.sleep(1)  # éviter d’être bloqué par l’API

    return dfs

# Pour tester 
# dfs_users = import_users_df(nombre_sample=50, parsing=2, token="lip_hdpFWKEs9ik0pf5mIg5T")
