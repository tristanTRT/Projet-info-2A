# Hot Hand dans les parties d’échecs en ligne  
*Projet de data science – Python*

## 1) Pitch & contexte

Le phénomène de **Hot Hand** désigne l’idée selon laquelle une série récente de succès
augmente la probabilité de succès futurs. Bien que longtemps débattu en psychologie et
en économie comportementale, il a été largement étudié dans des contextes sportifs
(basket-ball, baseball, tennis), mais beaucoup plus rarement dans des jeux **purement
stratégiques** comme les échecs.

Les échecs en ligne constituent pourtant un terrain d’étude particulièrement pertinent :
- le résultat de chaque partie est clairement défini (victoire/défaite/nulle),
- les joueurs disputent souvent plusieurs parties consécutives,
- de nombreuses variables observables sont disponibles (niveau Elo, cadence, ouverture).

Ce projet exploite des données issues de la plateforme **Lichess** afin d’évaluer
empiriquement l’existence et la nature d’un effet *Hot Hand* dans les parties d’échecs en
ligne.  
L’objectif n’est pas d’établir une causalité psychologique stricte, mais de déterminer
si les performances récentes sont associées à une probabilité accrue de succès à court
terme, et sous quelles conditions.

---

## 2) Problématique

> **Une victoire récente augmente-t-elle la probabilité de gagner la partie suivante
dans les échecs en ligne ?**

Plus précisément, le projet cherche à répondre aux questions suivantes :
- Existe-t-il une dépendance statistique entre résultats consécutifs ?
- Cette dépendance est-elle locale dans le temps (intra-session) ?
- Les résultats récents exercent-ils un effet cumulatif (mémoire > 1 match) ?
- Ces effets persistent-ils après contrôle du niveau du joueur et de facteurs
  structurels ?
- Les séries observées sont-elles compatibles avec un simple modèle aléatoire ?

---