"""
Master script pour :
 - importer les users depuis les leaderboards Lichess
 - importer leurs parties
 - sauvegarder les DataFrames au format Parquet
 - uploader automatiquement les fichiers sur le S3 Onyxia
"""

import subprocess
import sys
import os
import shutil
import pandas as pd
from dotenv import load_dotenv
from Scripts_generation_data.Import_des_users import import_users_df
from Scripts_generation_data.Import_une_partie import import_games_df

# ------------------------------------------------------------
# Installation automatique de boto3 si absent
# ------------------------------------------------------------
try:
    import boto3
except ModuleNotFoundError:
    print("boto3 non trouvé. Installation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3

load_dotenv()

# ------------------------------------------------------------
# Dossier principal des données
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "Data")
OPENINGS_FILE = os.path.join(DATA_DIR, "openings.parquet")

os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------
def nettoyer_data(data_dir):
    """Supprime tous les fichiers du dossier Data."""
    for file in os.listdir(data_dir):
        full_path = os.path.join(data_dir, file)
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Supprimé : {full_path}")


def prepare_output_folder(src=DATA_DIR, dst=None):
    """Crée le dossier Data_projet_info à uploader."""
    if dst is None:
        dst = os.path.join(BASE_DIR, "Data_projet_info")

    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    return dst


def upload_folder_to_s3(local_folder, bucket, prefix="Data_projet_info"):
    """Upload récursif vers S3 Onyxia."""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        endpoint_url=f"https://{os.getenv('AWS_S3_ENDPOINT')}",
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

    # Suppression ancien contenu
    existing = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" in existing:
        for obj in existing["Contents"]:
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
        print(f"Anciennes données sous {prefix} supprimées.")

    # Upload
    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = f"{prefix}/{relative_path}"
            s3.upload_file(local_path, bucket, s3_key)

    print(f"Upload terminé dans s3://{bucket}/{prefix}")


def lancer_creation_openings():
    """Exécute Creation_Df_openings et vérifie la présence du fichier parquet."""
    script_path = os.path.join(BASE_DIR, "Autres", "Creation_Df_openings.py")

    print("=== Exécution de Creation_Df_openings ===")
    subprocess.run([sys.executable, script_path], check=True)

    # Vérification du fichier généré
    if not os.path.exists(OPENINGS_FILE):
        raise FileNotFoundError(
            f"Erreur : {OPENINGS_FILE} non trouvé après l'exécution de Creation_Df_openings.py. "
            f"Assure-toi que le script crée bien ce fichier."
        )


# ------------------------------------------------------------
# Logique principale
# ------------------------------------------------------------
def main():
    print("=== Début du master script ===")

    # Inputs utilisateur
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ? "))
    parsing = int(input("Prendre un joueur tous les ... "))
    nb_parties_extraites = int(input("Combien de parties extraire ? "))

    token = os.environ["jeton_api"]

    # --- 1) Import des utilisateurs ---
    dfs_users_dict = import_users_df(nombre_sample, parsing, token)

    # --- 2) Import des parties ---
    df_games = import_games_df(nb_parties_extraites, token)

    # --- 3) Sauvegarde en Parquet ---
    games_file = os.path.join(DATA_DIR, "dfs_games.parquet")
    df_games.to_parquet(games_file, index=False)
    print(f"Fichier global sauvegardé localement : {games_file}")

    # --- 4) Préparation du dossier final ---
    output_folder = prepare_output_folder()

    # --- 5) Upload vers S3 ---
    upload_folder_to_s3(
        local_folder=output_folder,
        bucket="tristant",
        prefix="Data_projet_info"
    )

    print("=== Master script terminé ===")
    return "=== Master script terminé ==="


# ------------------------------------------------------------
# Exécution principale
# ------------------------------------------------------------
if __name__ == "__main__":
    # 1) Nettoyer Data/
    nettoyer_data(DATA_DIR)

    # 2) Générer openings.parquet AVANT tout import
    lancer_creation_openings()

    # 3) Exécuter le master
    main()