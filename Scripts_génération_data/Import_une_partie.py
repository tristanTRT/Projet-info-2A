# Import_une_partie.py
import requests
import json
import time
import pandas as pd
from Scripts_génération_data.Import_des_users import type_parties
import pickle
import os

# Répertoire des données
DATA_DIR = os.path.join(os.path.dirname(__file__), "../Data")
os.makedirs(DATA_DIR, exist_ok=True)

# 🔹 Charger le DataFrame des ouvertures depuis openings.pkl dans Data/
openings_file = os.path.join(DATA_DIR, "openings.pkl")
with open(openings_file, "rb") as f:
    df_openings = pickle.load(f)

def identify_opening(moves_list, openings_df, max_moves=6):
    moves_to_check = moves_list[:max_moves]
    for _, row in openings_df.iterrows():
        opening_moves = row["moves"][:max_moves]
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
                "rated", "timestamp", "result", "eco", "opening_name", "nb_coups_joueur"
            ])
    else:
        print(f"Échec après {max_retries} retries pour {username}")
        return pd.DataFrame(columns=[
            "rated", "timestamp", "result", "eco", "opening_name", "nb_coups_joueur"
        ])

    rows = []
    for line in r.text.strip().split("\n"):
        if not line.strip():
            continue
        game_data = json.loads(line)
        rated = game_data.get("rated", None)
        timestamp = game_data.get("createdAt", None)
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
            "rated": rated,
            "timestamp": timestamp,
            "result": result,
            "eco": eco,
            "opening_name": opening_name,
            "nb_coups_joueur": nb_coups_joueur
        })

    return pd.DataFrame(rows)

def import_games_df(dfs_users, nb_parties_extraites, token):
    all_games = {}
    for format_partie in type_parties:
        all_games[format_partie] = {}
        users = dfs_users[format_partie]["user_id"].tolist()
        for username in users:
            df_games = extract_games_user(username, format_partie, nb_parties_extraites, token)
            all_games[format_partie][username] = df_games
            time.sleep(1)

    # 🔹 Sauvegarde dans Data/
    games_file = os.path.join(DATA_DIR, "dfs_games.pkl")
    with open(games_file, "wb") as f:
        pickle.dump(all_games, f)

    return all_games
