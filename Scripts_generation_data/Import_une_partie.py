# Import_parties_parquet.py
import requests
import json
import time
import pandas as pd
import os

# Types de parties
type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]

# Répertoire des données
DATA_DIR = os.path.join(os.path.dirname(__file__), "../Data")
os.makedirs(DATA_DIR, exist_ok=True)

# Charger les ouvertures depuis un fichier parquet
openings_file = os.path.join(DATA_DIR, "openings.parquet")
df_openings = pd.read_parquet(openings_file)

def identify_opening(moves_list, openings_df, max_moves=6):
    moves_to_check = moves_list[:max_moves]
    for _, row in openings_df.iterrows():
        opening_moves = list(row["moves"][:max_moves])
        if moves_to_check[:len(opening_moves)] == opening_moves:
            return row["eco"], row["name"]
    return None, None

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
                "user_id", "rated", "timestamp", "result", "eco", "opening_name", "nb_coups_joueur"
            ])
    else:
        print(f"Échec après {max_retries} retries pour {username}")
        return pd.DataFrame(columns=[
            "user_id", "rated", "timestamp", "result", "eco", "opening_name", "nb_coups_joueur"
        ])

    rows = []
    for line in r.text.strip().split("\n"):
        if not line.strip():
            continue
        game_data = json.loads(line)
        rated = game_data.get("rated", None)
        timestamp = game_data.get("createdAt", None)

        # Déterminer la couleur du joueur
        try:
            white_user = game_data["players"]["white"]["user"]["id"].lower()
            player_color = "white" if white_user == username.lower() else "black"
        except Exception:
            continue

        winner = game_data.get("winner", None)
        result = "Win" if winner == player_color else "Loss"

        moves = game_data.get("moves", "").split()
        nb_coups_joueur = len(moves[::2]) if player_color == "white" else len(moves[1::2])
        moves_joueur = moves[::2] if player_color == "white" else moves[1::2]

        eco, opening_name = identify_opening(moves_joueur, df_openings)

        rows.append({
            "user_id": username,
            "rated": rated,
            "timestamp": timestamp,
            "result": result,
            "eco": eco,
            "opening_name": opening_name,
            "nb_coups_joueur": nb_coups_joueur
        })

    return pd.DataFrame(rows)

def import_games_df(nb_parties_extraites, token):
    """
    Importation des parties pour tous les utilisateurs et tous les formats.
    Sauvegarde un seul fichier Parquet par type de partie.
    """
    for format_partie in type_parties:
        print(f"Extraction des parties pour {format_partie}…")
        # Charger les joueurs pour ce format
        users_file = os.path.join(DATA_DIR, f"users_{format_partie}.parquet")
        df_users = pd.read_parquet(users_file)
        users = df_users["user_id"].tolist()

        dfs = []

        for username in users:
            df_games = extract_games_user(username, format_partie, nb_parties_extraites, token)
            dfs.append(df_games)
            time.sleep(1)

        # Concaténer toutes les parties pour ce format
        df_format = pd.concat(dfs, ignore_index=True)

        # Sauvegarder un seul fichier Parquet par format
        output_file = os.path.join(DATA_DIR, f"games_{format_partie}.parquet")
        df_format.to_parquet(output_file, index=False)
        print(f"Sauvegardé {len(df_format)} parties dans {output_file}\n")

# Pour tester 
# import_games_df(nb_parties_extraites=10, token="lip_EhmwZ2NVgfwE6kcZ4rWh")
