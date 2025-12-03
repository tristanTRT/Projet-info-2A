# Import_des_users.py
import requests
import pandas as pd
import time
import os

type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]

# Répertoire des données
DATA_DIR = os.path.join(os.path.dirname(__file__), "../Data")
os.makedirs(DATA_DIR, exist_ok=True)

def extraction_users_leaderboard(nombre_sample, format_partie, parsing, token, max_retries=5):
    nbusermax = parsing * nombre_sample
    url = f"https://lichess.org/api/player/top/{nbusermax}/{format_partie}"
    headers = {"Authorization": f"Bearer {token}"}

    retries = 0
    while retries < max_retries:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            break
        elif r.status_code == 429:
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
    dfs = {}
    for format_partie in type_parties:
        user_list = extraction_users_leaderboard(nombre_sample, format_partie, parsing, token)
        df = pd.DataFrame(user_list, columns=["user_id", "elo"])
        dfs[format_partie] = df.reset_index(drop=True)
        time.sleep(1)

    # 🔹 Sauvegarde dans Data/
    users_file = os.path.join(DATA_DIR, "dfs_users.pkl")
    with open(users_file, "wb") as f:
        pd.to_pickle(dfs, f)

    return dfs
