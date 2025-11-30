# Master_file.py
"""
Master script pour :
 - importer les users depuis les leaderboards Lichess
 - importer leurs parties
 - sauvegarder les DataFrames sur disque pour réutilisation
"""

import os
import pickle
from Scripts_génération_data.Import_des_users import import_users_df
from Scripts_génération_data.Import_une_partie import import_games_df

# Répertoire pour stocker les données
DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
os.makedirs(DATA_DIR, exist_ok=True)  # créer Data si nécessaire

def main():
    print("=== Début du master script ===")
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ? "))
    parsing = int(input("Prendre un joueur tous les ... "))
    nb_parties_extraites = int(input("Combien de parties extraire ? "))
    token = "lip_jwKnD5eHwEVhDubisYt5" #A UPDATER ABSOLUMENT

    # 1) Import des users
    dfs_users = import_users_df(nombre_sample, parsing, token)

    # 2) Import des parties
    dfs_games = import_games_df(dfs_users, nb_parties_extraites, token)

    # 3) Sauvegarde sur disque dans Data/
    users_file = os.path.join(DATA_DIR, "dfs_users.pkl")
    games_file = os.path.join(DATA_DIR, "dfs_games.pkl")

    with open(users_file, "wb") as f:
        pickle.dump(dfs_users, f)
    with open(games_file, "wb") as f:
        pickle.dump(dfs_games, f)

    print(f"=== Master script terminé et DataFrames sauvegardés dans {DATA_DIR} ! ===")
    return dfs_users, dfs_games

if __name__ == "__main__":
    main()
