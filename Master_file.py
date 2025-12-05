# Master_file.py
"""
Master script pour :
 - importer les users depuis les leaderboards Lichess
 - importer leurs parties
 - sauvegarder les DataFrames au format Parquet
"""

import subprocess
import os
import pandas as pd
from dotenv import load_dotenv
from Scripts_generation_data.Import_des_users import import_users_df

load_dotenv()

# Répertoire pour stocker les données
DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
os.makedirs(DATA_DIR, exist_ok=True)

def nettoyer_data(data_dir):
    """Supprime tous les fichiers du dossier Data."""
    for file in os.listdir(data_dir):
        full_path = os.path.join(data_dir, file)
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Supprimé : {full_path}")

def lancer_creation_openings():
    """Exécute le script de création du parquet des ouvertures."""
    script_path = os.path.join(os.path.dirname(__file__), "Autres", "Creation_Df_openings.py")
    print("=== Exécution de Creation_Df_openings ===")
    subprocess.run(["/opt/python/bin/python", script_path], check=True)

def main():
    # Import tardif pour éviter circular import
    from Scripts_generation_data.Import_une_partie import import_games_df
    # Import des users (si besoin, ou importez la fonction depuis le bon script)
    # from Scripts_generation_data.Import_des_users import import_users_df 
    # Assurez-vous d'importer la fonction depuis le bon script si le nom a changé.

    print("=== Début du master script (Logique principale) ===")

    # Les étapes de Nettoyage et Création Openings sont désormais AVANT l'appel à main()

    # Inputs utilisateur
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ? "))
    parsing = int(input("Prendre un joueur tous les ... "))
    nb_parties_extraites = int(input("Combien de parties extraire ? "))

    token = os.environ["jeton_api"]  # Token Lichess

    # --- 1) Import des users ---
    # dfs_users est maintenant un dictionnaire (comme le montre votre script)
    # Le Parquet est SAUVEGARDÉ DIRECTEMENT DANS CETTE FONCTION.
    dfs_users_dict = import_users_df(nombre_sample, parsing, token)

    # --- 2) Import des parties ---
    df_games = import_games_df(nb_parties_extraites, token)

    # --- 3) Sauvegarde en Parquet ---
    games_file = os.path.join(DATA_DIR, "dfs_games.parquet")

    print(f"=== Master script terminé ===")
    
    return(f"=== Master script terminé ===")
    
if __name__ == "__main__":
    # 1. Nettoyer les données (étape déplacée ici)
    nettoyer_data(DATA_DIR)
    
    # 2. Créer le fichier des ouvertures
    lancer_creation_openings()
    
    # 3. Exécuter la logique principale (Import Users & Games, Sauvegarde)
    main()