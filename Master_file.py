"""
Master script pour :
 - importer les users depuis les leaderboards Lichess
 - importer leurs parties
 - sauvegarder les DataFrames au format Parquet
 - uploader automatiquement les fichiers sur le S3 Onyxia (Dossier Public 'diffusion')
"""

import subprocess
import sys
import os
import shutil
import pandas as pd
from dotenv import load_dotenv
from Scripts_generation_data.Import_des_users import import_users_df


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
    for file in os.listdir(data_dir):
        full_path = os.path.join(data_dir, file)
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Supprimé : {full_path}")

def prepare_output_folder(src=DATA_DIR, dst=None):
    if dst is None:
        # Le dossier local temporaire reste 'Data_projet_info'
        dst = os.path.join(BASE_DIR, "Data_projet_info")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst

# ====================================================================
# MODIFICATION ICI : Tentative d'ACL public-read et suppression du prefix par défaut
# ====================================================================
def upload_folder_to_s3(local_folder, bucket, prefix):
    """
    Upload le contenu de local_folder dans le bucket:prefix sur S3.
    Tente d'appliquer l'ACL 'public-read'.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        endpoint_url=f"https://{os.getenv('AWS_S3_ENDPOINT', 'minio.lab.sspcloud.fr')}",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )

    # Nettoyage des anciennes données
    try:
        existing = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" in existing:
            print(f"Nettoyage des anciens fichiers dans s3://{bucket}/{prefix}...")
            for obj in existing["Contents"]:
                s3.delete_object(Bucket=bucket, Key=obj["Key"])
            print("Nettoyage terminé.")
    except Exception as e:
        print(f"⚠️ Impossible de lister/supprimer les anciens fichiers : {e}")


    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            # relative_path est juste le nom du fichier, car on copie le contenu du dossier
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = f"{prefix}/{relative_path}"
            
            print(f"Upload de {file} -> s3://{bucket}/{s3_key}")
            try:
                # Tente de forcer l'ACL public-read pour l'accès anonyme
                s3.upload_file(
                    local_path, 
                    bucket, 
                    s3_key, 
                    ExtraArgs={'ACL': 'public-read'}
                )
            except Exception as e:
                # Fallback si l'ACL échoue (si la politique du bucket s'y oppose)
                print(f"⚠️ Warning ACL: {e}. Tentative d'upload standard...")
                s3.upload_file(local_path, bucket, s3_key)

    print(f"✅ Upload terminé dans s3://{bucket}/{prefix}")

    # Affichage du lien public pour vérification
    endpoint = os.getenv('AWS_S3_ENDPOINT', 'minio.lab.sspcloud.fr')
    print(f"\n📂 Vos données sont accessibles publiquement ici :")
    print(f"https://{endpoint}/{bucket}/{prefix}/")
# ====================================================================


def lancer_creation_openings():
    script_path = os.path.join(BASE_DIR, "Autres", "Creation_Df_openings.py")
    print("=== Exécution de Creation_Df_openings.py ===")
    subprocess.run([sys.executable, script_path], check=True)
    if not os.path.exists(OPENINGS_FILE):
        raise FileNotFoundError(f"ERREUR : {OPENINGS_FILE} non trouvé après exécution de Creation_Df_openings.")


# ------------------------------------------------------------
# Logique principale
# ------------------------------------------------------------
def main():
    print("=== Début du master script ===")

    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ? "))
    parsing = int(input("Prendre un joueur tous les ... "))
    nb_parties_extraites = int(input("Combien de parties extraire ? "))

    token = os.environ["jeton_api"]

    dfs_users_dict = import_users_df(nombre_sample, parsing, token)
    lancer_creation_openings()
    from Scripts_generation_data.Import_une_partie import import_games_df
    df_games = import_games_df(nb_parties_extraites, token)

    games_file = os.path.join(DATA_DIR, "dfs_games.parquet")
    df_games.to_parquet(games_file, index=False)
    print(f"Fichier global sauvegardé : {games_file}")

    output_folder = prepare_output_folder()

    # ====================================================================
    # MODIFICATION ICI : Cible le dossier 'diffusion'
    # ====================================================================
    upload_folder_to_s3(
        local_folder=output_folder,
        bucket="tristant",
        prefix="diffusion" 
    )
    # ====================================================================
    print("\n🗑 Suppression des fichiers locaux dans le dossier Data...")
    nettoyer_data(DATA_DIR)
    print("✅ Fichiers locaux supprimés.")

    print("=== Master script terminé ===")
    return "=== Master script terminé ==="

# ------------------------------------------------------------
# Exécution
# ------------------------------------------------------------
if __name__ == "__main__":
    nettoyer_data(DATA_DIR)
    lancer_creation_openings()
    main()