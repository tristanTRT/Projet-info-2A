# Python pour la datascience - Projet 

## Sujet :  Le phénomène « hot hand » analysé à partir de données de parties d'échecs
Contexte
Le « hot hand » est un phénomène psychologique et statistique qui postule qu'un individu connaissant une série de
succès aurait une probabilité accrue de réussir ses actions suivantes. Longtemps débattu en économie
comportementale et en psychologie, ce phénomène a été étudié notamment dans le sport (basket-ball, baseball,
tennis), mais rarement dans le cadre des échecs.
Or, la plateforme en ligne Lichess met à disposition des bases de données ouvertes contenant des millions de parties
d'échecs jouées par des amateurs et professionnels. Ces données massives et riches (résultats, cadence de jeu, elo
des joueurs, ouverture choisie, séquence de coups) offrent une opportunité unique pour tester empiriquement
l'existence du « hot hand » dans un contexte stratégique et intellectuel, et non purement physique.

## Problématique : 
Vérifier l'existence et la nature du phénomène de « hot hand » dans les parties d'échecs en ligne.


## Navigation au sein du projet : 
Une extraction d'un échantillon de parties de plusieurs natures (classical, blitz, rapid...) est réalisée (cf. MasterFile dans Scripts_Génération_Données). Ces scripts prennent un certain temps à tourner et nécessitent la création d'un fichier .env comprenant notamment une clé d'accès à l'API Lichess (token) qui doit être appelée : "jeton_api". 
Pour cette raison, un échantillon de taille raisonnable (env. 15 000 parties) a préalablement été généré et accessible depuis le cloud (S3). 

Ensuite, un notabook Analyse_data permet de générer les résultats obtenus en faisant tourner chacune des cellules qu'il contient. 

Pour faire tourner l'Analyse de données, il faut créer un fichier .env avec le chemin de connexion vers le lieu de stockage de données (S3) : S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "minio.lab.sspcloud.fr")
Pour faire tourner le MasterFile, il faut créer un fichier .env avec les identifiants de connexion de Tristan pour accéder à l'espace de stockage du S3, et se doter d'un token API Lichess qu'on appellera jeton_api.

## Analyses effectuées : 


Le projet visera à :
1.	Définir et mesurer plusieurs indicateurs du « hot hand » (séries de victoires, qualité de coups joués mesurée par le
moteur, performance relative à l'elo attendu).
2.	Étudier la robustesse de ces indicateurs selon le niveau des joueurs, le type de cadence (bullet, blitz, rapid, classical),
et le contexte des parties (tournoi, parties amicales).
3.	Mobiliser des modèles statistiques pour tester si les performances récentes augmentent significativement la
probabilité de succès futur.
Elements techniques / statistiques
La réalisation du projet nécessitera plusieurs étapes :
?	Collecte et préparation des données : extraction d'échantillons représentatifs de parties à partir des bases publiques
Lichess (PGN ou API), nettoyage des données (format, doublons, gestion des comptes « bots », filtrage par cadence et
niveau elo).
?	Construction des variables :
o	Séries de victoires/défaites et longueur des « streaks » ;
o	Indicateurs de performance ajustés à l'elo attendu (logit de Bradley-Terry, Elo-diff attendu vs. résultat effectif) ;
o	Qualité des coups via l'évaluation Stockfish (mesure des inexactitudes, erreurs, gaffes).
?	Méthodes d'analyse :
o	Tests d'indépendance des résultats consécutifs (tests de Markov, chaînes de Bernoulli, modèles logistiques avec
mémoire).
o	Modélisation par régressions logistiques et modèles de survie pour évaluer l'effet d'un « streak » sur la probabilité de
victoire suivante.
o	Comparaison avec simulations « null model » (permutations aléatoires des séquences de résultats) pour évaluer si le
hot hand est statistiquement significatif ou seulement une illusion cognitive.
?	Validation et robustesse : analyses selon sous-échantillons (par elo, cadence, période de la journée, nature du
tournoi).
""


## Limitations : 
L'API Lichess est cependant limitée. Nous pouvons l'interroger sur les 100 meilleurs joueurs pour chaque type de parties. Elle peut également s'interroger pour un joueur spécifique, mais il est nécessaire de spécifier son identifiant sur la plateforme. 
Une des principales limitations du jeu de données à disposition est donc qu'il ne se concentre que sur les 100 meilleurs joueurs de chaque format de parties.

Améliorations éventuelles : nous aurions pu récupérer des noms de joueurs par une identification 'ricochet' en commençant avec le 1er de la catégorie, puis en s'intéressant sur l'adversaire de sa dernière victoire, puis sur l'adversaire de la dernière victoire de ce dernier... Pour finalement descendre le reste du leaderboard de manière plus homogène. Cela dit cette méthode aurait posé des problèmes en termes de temps computationnel puisqu'il n'est pas possible de surcharger l'API de Lichess qui reste assez sensible. 
Alors que l'extraction du Top100 se fait par une seule requête, et est donc beaucoup plus économe en terme de temps. 
