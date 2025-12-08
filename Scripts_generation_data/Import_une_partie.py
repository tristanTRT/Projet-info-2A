import requests
import json
import time
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "../Data")
os.makedirs(DATA_DIR, exist_ok=True)

# Charger les ouvertures depuis un fichier parquet
openings_file = os.path.join(DATA_DIR, "openings.parquet")
df_openings = pd.read_parquet(openings_file)

# Construire un dictionnaire pour identifier rapidement les ouvertures
MAX_MOVES = 6
openings_dict = {}
for _, row in df_openings.iterrows():
    key = tuple(row["moves"][:MAX_MOVES])
    openings_dict[key] = (row["eco"], row["name"])

def identify_opening_fast(moves_list):
    moves_slice = tuple(moves_list[:MAX_MOVES])
    return openings_dict.get(moves_slice, (None, None))

def extract_games_user(username, format_partie, nb_parties, token, max_retries=5):
    url = f"https://lichess.org/api/games/user/{username}"
    params = {"max": nb_parties, "rated": "true", "perfType": format_partie}
    headers = {"Accept": "application/x-ndjson", "Authorization": f"Bearer {token}"}

    retries = 0
    while retries < max_retries:
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 200:
            break
        elif r.status_code == 429:
            wait_time = int(r.headers.get("Retry-After", 3))
            print(f"429 reçu pour {username}. Attente {wait_time}s ({retries+1}/{max_retries})")
            time.sleep(wait_time)
            retries += 1
        else:
            print("Erreur", r.status_code, username)
            return pd.DataFrame(columns=[
                "user_id", "rated", "timestamp", "result",
                "eco", "opening_name", "nb_coups_joueur",
                "rating", "rating_diff"
            ])
    else:
        print(f"Échec après {max_retries} retries pour {username}")
        return pd.DataFrame(columns=[
            "user_id", "rated", "timestamp", "result",
            "eco", "opening_name", "nb_coups_joueur",
            "rating", "rating_diff"
        ])

    rows = []
    for line in r.text.strip().split("\n"):
        if not line.strip():
            continue
        game_data = json.loads(line)
        rated = game_data.get("rated")
        timestamp = game_data.get("createdAt")

        try:
            white_user = game_data["players"]["white"]["user"]["id"].lower()
            player_color = "white" if white_user == username.lower() else "black"
        except Exception:
            continue

        rating = game_data["players"][player_color].get("rating")
        rating_diff = game_data["players"][player_color].get("ratingDiff")
        winner = game_data.get("winner")
        result = "Win" if winner == player_color else "Loss"

        moves = game_data.get("moves", "").split()
        nb_coups_joueur = len(moves[::2]) if player_color == "white" else len(moves[1::2])
        moves_joueur = moves[::2] if player_color == "white" else moves[1::2]

        eco, opening_name = identify_opening_fast(moves_joueur)

        rows.append({
            "user_id": username,
            "rated": rated,
            "timestamp": timestamp,
            "result": result,
            "eco": eco,
            "opening_name": opening_name,
            "nb_coups_joueur": nb_coups_joueur,
            "rating": rating,
            "rating_diff": rating_diff
        })

    return pd.DataFrame(rows)


def import_games_df(nb_parties_extraites, token, max_workers=10):
    """
    Importation des parties pour tous les utilisateurs et tous les formats.
    Sauvegarde un fichier Parquet par type de partie.
    Retourne un DataFrame global.
    """
    all_dfs = []

    for format_partie in type_parties:
        print(f"Extraction des parties pour {format_partie}…")
        users_file = os.path.join(DATA_DIR, f"users_{format_partie}.parquet")
        df_users = pd.read_parquet(users_file)
        users = df_users["user_id"].tolist()

        dfs = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_user = {executor.submit(extract_games_user, user, format_partie, nb_parties_extraites, token): user for user in users}
            for future in as_completed(future_to_user):
                user_df = future.result()
                dfs.append(user_df)

        df_format = pd.concat(dfs, ignore_index=True)
        output_file = os.path.join(DATA_DIR, f"games_{format_partie}.parquet")
        df_format.to_parquet(output_file, index=False)
        print(f"Sauvegardé {len(df_format)} parties dans {output_file}\n")
        all_dfs.append(df_format)

    df_all = pd.concat(all_dfs, ignore_index=True)
    return df_all