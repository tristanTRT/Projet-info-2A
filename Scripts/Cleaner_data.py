# clean_data.py
import os
def run_clean_data():
    chemin_dossier = "/home/onyxia/work/Projet-info-2A/Data"

    # Vérifier que le dossier existe
    if os.path.exists(chemin_dossier):
        for filename in os.listdir(chemin_dossier):
            file_path = os.path.join(chemin_dossier, filename)
            # Supprime seulement si c'est un fichier
            if os.path.isfile(file_path):
                os.remove(file_path)
    print("Dossier Data nettoyé.")
