# Projet-info-2A


# Tâche n°1 : Récupération d'identifiants d'utilisateurs 
On scrappe les leaderboards des différents formats de parties. 
On est dans un premier temps partir sur une sélection des N meilleurs joueurs pour chaque format de partie.

Pour que nos anlyses et résultats gagnent en robustesse, on itère le code en prenant un joueur tous les 100 joueurs pour avoir une distribution un peu plus représentative.

Idées d'amélioration : 
Prendre non pas un joueur sur 100, mais choisir un joueur au hasard en respectant une distribution gaussienne. 
Nécessaire de trouve le max des joueurs par catégorie : créer une fonction qui demande à l'API si le joueur N existe et si renvoie 200, on fait N+1 jusqu'à renvoi d'une erreur.
Ensuite on utilise un rd.random qui simule une gaussienne centrée autour de 1/2 et on utilise ça pour renvoyer un joueur dont la position dans le leaderboard est centrée autour de 1/2.

Ou fonctionner par Elo : prendre une proportion plus importante de joueurs au elo concentré autour de la médiane ? 
Ou fonctionner par classe d'Elo pour classer nos joueurs choisis aléatoirement (uniformes) dans des catégories.


# Tâche n°2 : Aller chercher les parties associées aux joueurs receuillis
Convertir et exporter ces données d'utilisateurs (potentiellement rangées par Elo) dans un dataframe qu'on stocke dans le projet "Data".
