import sys
import os
import pickle

type_parties = ["ultraBullet", "bullet", "blitz", "rapid", "classical"]

# 🔹 Répertoires principaux
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(current_dir, "../Scripts-génération-data")  # remonte d'un niveau
data_dir = os.path.join(current_dir, "../Data")  # remonte d'un niveau pour Data

# Ajouter Scripts-génération-data au path si besoin
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# Charger les DataFrames sauvegardés depuis Data/
dfs_users_file = os.path.join(data_dir, "dfs_users.pkl")
dfs_games_file = os.path.join(data_dir, "dfs_games.pkl")

with open(dfs_users_file, "rb") as f:
    dfs_users = pickle.load(f)

with open(dfs_games_file, "rb") as f:
    dfs_games = pickle.load(f)

# Fonction pratique pour explorer les parties d'un joueur
def show_player_games(username, dfs_games, max_rows=5):
    for format_partie, players_dict in dfs_games.items():
        if username in players_dict:
            df = players_dict[username]
            print(f"\nFormat : {format_partie} | Joueur : {username}")
            print(df.head(max_rows))
        else:
            print(f"\nFormat : {format_partie} | Joueur : {username} : pas de données")

# Exemple d'utilisation
# show_player_games("elconceto", dfs_games)

# Exemple affichage classique




print(dfs_games["classical"]["chesstheory64"])
print('Parties de yuuki-asuna, user classical')
