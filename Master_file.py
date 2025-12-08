# Master_file.py
"""
Master script pour :
 - importer les users depuis les leaderboards Lichess
 - importer leurs parties
 - sauvegarder les DataFrames au format Parquet
 - uploader automatiquement les fichiers sur le S3 Onyxia
"""

import subprocess
import os
import boto3
import pandas as pd
import shutil
from dotenv import load_dotenv
from Scripts_generation_data.Import_des_users import import_users_df
from Scripts_generation_data.Import_une_partie import import_games_df

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

def prepare_output_folder(src=DATA_DIR, dst=None):
    if dst is None:
        dst = os.path.join(os.path.dirname(__file__), "Data_projet_info")

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def upload_folder_to_s3(local_folder, bucket, prefix="Data_projet_info"):
    import boto3

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        endpoint_url=f"https://{os.getenv('AWS_S3_ENDPOINT')}",
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

    # Supprime tous les fichiers existants sous ce préfixe
    existing = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" in existing:
        for obj in existing["Contents"]:
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
        print(f"Anciennes données sous {prefix} supprimées.")

    # Upload des fichiers locaux
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = f"{prefix}/{relative_path}"
            s3.upload_file(local_path, bucket, s3_key)
    print(f"Upload terminé dans s3://{bucket}/{prefix}")


def lancer_creation_openings():
    """Exécute le script de création du parquet des ouvertures."""
    script_path = os.path.join(os.path.dirname(__file__), "Autres", "Creation_Df_openings.py")
    print("=== Exécution de Creation_Df_openings ===")
    subprocess.run(["/opt/python/bin/python", script_path], check=True)

def main():
    print("=== Début du master script ===")

    # Inputs utilisateur
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ? "))
    parsing = int(input("Prendre un joueur tous les ... "))
    nb_parties_extraites = int(input("Combien de parties extraire ? "))

    token = os.environ["jeton_api"]  # Token Lichess

    # --- 1) Import des users ---
    dfs_users_dict = import_users_df(nombre_sample, parsing, token)

    # --- 2) Import des parties ---
    # Retourne un DataFrame global avec toutes les parties
    df_games = import_games_df(nb_parties_extraites, token)

    # --- 3) Sauvegarde en Parquet ---
    games_file = os.path.join(DATA_DIR, "dfs_games.parquet")
    df_games.to_parquet(games_file, index=False)
    print(f"Fichier global sauvegardé localement : {games_file}")

    # --- 4) Préparer le dossier pour l'upload ---
    output_folder = prepare_output_folder()  # src=DATA_DIR, dst=Data_projet_info


    # --- 5) Upload vers S3 Onyxia ---
    bucket_name = "tristant"  # Ton bucket Onyxia
    s3_prefix = "Data_projet_info"

    upload_folder_to_s3(
        local_folder=output_folder,
        bucket=bucket_name,
        prefix=s3_prefix
    )

    print("=== Master script terminé ===")
    return "=== Master script terminé ==="

if __name__ == "__main__":
    # 1. Nettoyer les données
    nettoyer_data(DATA_DIR)
    
    # 2. Créer le fichier des ouvertures
    lancer_creation_openings()
    
    # 3. Exécuter la logique principale (Import Users & Games + Upload)
    main()
