def extraction_users_leaderboard (nombre_sample, type_parties) :
    #Extraction des IDs pour les users du top X d'un type de parties Y 
    import requests
    url_Lichess_example = f"https://lichess.org/api/player/top/{nombre_sample}/{type_parties}"
    req = requests.get(url_Lichess_example).json()
    ids = [user['id'] for user in req['users']]
    return(ids)


#Appel fonction : 

nombre_sample = int(input("Nombre de joueurs extraits"))
type_parties = input("Type de parties (ultraBullet, bullet, blitz, rapid, classical) : ")

print(extraction_users_leaderboard(nombre_sample,type_parties))

