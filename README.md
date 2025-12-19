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
Pour cette raison, un échantillon de taille raisonnable (+10 000 parties) a préalablement été généré et accessible depuis le cloud (S3). 

Ensuite, un notabook Analyse_data permet de générer les résultats obtenus en faisant tourner chacune des cellules qu'il contient. 

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

Pour faire tourner le MasterFile, il faut créer un fichier .env avec les identifiants de connexion de Tristan pour accéder à l'espace de stockage du S3, et se doter d'un token API Lichess qu'on appellera jeton_api.
