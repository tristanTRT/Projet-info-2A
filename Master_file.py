# master.py
"""
Master script pour :
"""
import random as rd

from Scripts_génération_data.Cleaner_data import run_clean_data
from Scripts_génération_data.Import_des_users import import_users
from Scripts_génération_data.Import_une_partie import import_games



def main():
    print("=== Début du master script ===")
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ?"))
    parsing = int(input("Prendre un joueur tous les ..."))
    nb_parties_extraites = int(input("Combien de parties extraire ?"))
    
    run_clean_data()

    import_users(nombre_sample, parsing)

    import_games(nb_parties_extraites)

    print("=== Master script terminé ===")

if __name__ == "__main__":
    main()
