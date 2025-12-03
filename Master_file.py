# Master_file.py
"""
Master script pour :
 - importer les users depuis les leaderboards Lichess
 - importer leurs parties
 - sauvegarder les DataFrames sur disque pour réutilisation
"""

import subprocess
import os
import pickle
from Scripts_génération_data.Import_des_users import import_users_df
from Scripts_génération_data.Import_une_partie import import_games_df

# Répertoire pour stocker les données
DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
os.makedirs(DATA_DIR, exist_ok=True)  # créer Data si nécessaire

def nettoyer_data(data_dir):
    for file in os.listdir(data_dir):
        full_path = os.path.join(data_dir, file)
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Supprimé : {full_path}")

def lancer_creation_openings():
    script_path = os.path.join(os.path.dirname(__file__), "Autres", "Creation_Df_openings.py")
    print("=== Exécution de Creation_Df_openings ===")
    subprocess.run(["/opt/python/bin/python", script_path], check=True)

def main():
    print("=== Début du master script ===")
    nettoyer_data(DATA_DIR)
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ? "))
    parsing = int(input("Prendre un joueur tous les ... "))
    nb_parties_extraites = int(input("Combien de parties extraire ? "))
    clé = "lip_CPVkHhmuMoSsZ11CRhXj" # Token Lichess Tristan

    # 1) Import des users
    dfs_users = import_users_df(nombre_sample, parsing, clé)

    # 2) Import des parties
    dfs_games = import_games_df(dfs_users, nb_parties_extraites, clé)

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
