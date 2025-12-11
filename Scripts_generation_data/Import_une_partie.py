import requests
import json
import time
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# --- CONFIGURATION ---
type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]
MAX_MOVES = 12  # Augmenté à 12 pour attraper les variantes profondes, mais le système marche avec n'importe quel nombre
DATA_DIR = os.path.join(os.path.dirname(__file__), "../Data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- CHARGEMENT DES OUVERTURES ---
openings_file = os.path.join(DATA_DIR, "openings.parquet")
openings_dict = {}

if os.path.exists(openings_file):
    try:
        print("Chargement des ouvertures...")
        df_openings = pd.read_parquet(openings_file)
        
        # Vérification du type de données
        if not df_openings.empty:
            sample_moves = df_openings.iloc[0]["moves"]
            if isinstance(sample_moves, str):
                print("⚠️ ATTENTION: La colonne 'moves' est chargée comme des chaînes de caractères au lieu de listes.")
                # Si nécessaire, décommenter la ligne suivante pour convertir :
                # import ast; df_openings["moves"] = df_openings["moves"].apply(ast.literal_eval)

        for _, row in df_openings.iterrows():
            # On stocke les coups sous forme de tuple pour qu'ils soient "hashable"
            # On ne coupe PAS ici avec [:MAX_MOVES], on garde toute la définition de l'ouverture
            key = tuple(row["moves"])
            openings_dict[key] = (row["eco"], row["name"])
            
        print(f"✅ Chargé {len(openings_dict)} ouvertures en mémoire.")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des ouvertures : {e}")
else:
    print("⚠️ Fichier openings.parquet non trouvé.")

def identify_opening_fast(moves_list):
    """
    Identifie l'ouverture en cherchant le préfixe le plus long connu.
    """
    if not moves_list:
        return (None, None)
    
    # On teste jusqu'à 20 coups max pour éviter les boucles infinies sur des parties géantes
    limit = min(len(moves_list), 20)
    
    # On cherche la séquence la plus longue possible
    # Ex: Si la partie est e4 e5 Nf3 Nc6
    # On teste (e4, e5, Nf3, Nc6) -> Non trouvé
    # On teste (e4, e5, Nf3) -> Trouvé ! (King's Knight)
    for length in range(limit, 0, -1):
        moves_slice = tuple(moves_list[:length])
        if moves_slice in openings_dict:
            return openings_dict[moves_slice]
            
    return (None, None)

def extract_games_user(username, format_partie, nb_parties, token, max_retries=5):
    # Pause aléatoire pour ne pas bloquer l'API
    time.sleep(random.uniform(0.5, 1.5)) 
    
    url = f"https://lichess.org/api/games/user/{username}"
    params = {"max": nb_parties, "rated": "true", "perfType": format_partie}
    headers = {"Accept": "application/x-ndjson", "Authorization": f"Bearer {token}"}

    r = None
    retries = 0
    base_wait_time = 5 

    while retries < max_retries:
        try:
            r = requests.get(url, params=params, headers=headers)
            if r.status_code == 200:
                break 
            elif r.status_code == 429:
                server_wait = r.headers.get("Retry-After")
                wait_time = int(server_wait) if server_wait else base_wait_time * (2 ** retries)
                print(f"⚠️ 429 pour {username}. Pause de {wait_time}s...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"Erreur HTTP {r.status_code} pour {username}")
                return pd.DataFrame() 
        except requests.exceptions.RequestException as e:
            print(f"Erreur connexion : {e}")
            time.sleep(5)
            retries += 1

    if r is None or r.status_code != 200:
        return pd.DataFrame()

    rows = []
    for line in r.iter_lines():
        if not line: continue
        try:
            game_data = json.loads(line.decode('utf-8'))
        except json.JSONDecodeError:
            continue

        rated = game_data.get("rated")
        timestamp = game_data.get("createdAt")

        try:
            white_user = game_data["players"]["white"]["user"]["id"].lower()
            player_color = "white" if white_user == username.lower() else "black"
        except KeyError:
            continue

        rating = game_data["players"][player_color].get("rating")
        rating_diff = game_data["players"][player_color].get("ratingDiff")
        winner = game_data.get("winner")
        result = "Win" if winner == player_color else "Loss"

        moves = game_data.get("moves", "").split()
        moves_joueur = moves[::2] if player_color == "white" else moves[1::2]
        nb_coups_joueur = len(moves_joueur)

        # IDENTIFICATION DE L'OUVERTURE (Avec tous les coups)
        eco, opening_name = identify_opening_fast(moves)

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

def import_games_df(nb_parties_extraites, token, max_workers=2): 
    all_dfs = []
    for format_partie in type_parties:
        print(f"--- Extraction pour {format_partie} ---")
        users_file = os.path.join(DATA_DIR, f"users_{format_partie}.parquet")
        
        if not os.path.exists(users_file):
            print(f"Fichier manquant: {users_file}")
            continue
            
        df_users = pd.read_parquet(users_file)
        users = df_users["user_id"].tolist()

        dfs = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_user = {executor.submit(extract_games_user, user, format_partie, nb_parties_extraites, token): user for user in users}
            for future in as_completed(future_to_user):
                user_df = future.result()
                if not user_df.empty:
                    dfs.append(user_df)

        if dfs:
            df_format = pd.concat(dfs, ignore_index=True)
            output_file = os.path.join(DATA_DIR, f"games_{format_partie}.parquet")
            df_format.to_parquet(output_file, index=False)
            print(f"✅ Sauvegardé {len(df_format)} parties dans {output_file}")
            
            # --- VERIFICATION IMMEDIATE DU RESULTAT ---
            filled_openings = df_format['opening_name'].notna().sum()
            print(f"📊 DEBUG : {filled_openings} / {len(df_format)} parties ont une ouverture identifiée.")
            
            all_dfs.append(df_format)
        else:
            print(f"Aucune donnée pour {format_partie}")

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()