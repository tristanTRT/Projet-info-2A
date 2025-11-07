# master.py
"""
Master script pour :
"""
import random as rd

from Scripts.Cleaner_data import run_clean_data
from Scripts.Import_des_users import import_users
from Scripts.Import_une_partie import import_games



def main():
    print("=== Début du master script ===")
    nombre_sample = int(input("Quel est le nombre de joueurs à étudier ?"))
    parsing = rd.randint(1,100)
    
    run_clean_data()

    import_users(parsing*nombre_sample, parsing)

    import_games(nb_parties_extraites=10)

    print("=== Master script terminé ===")

if __name__ == "__main__":
    main()
