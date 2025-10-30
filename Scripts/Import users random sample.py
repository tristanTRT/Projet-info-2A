# Renvoie sample_size parties lues sur la période "période"

import requests, zstandard as zstd, io

def debug_n_games_every_x(n, periode, x):
    """
    Récupère n headers de parties du fichier Lichess, en prenant une partie tous les x.
    """
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{periode}.pgn.zst"
    headers_sample = []

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        dctx = zstd.ZstdDecompressor()
        stream_reader = dctx.stream_reader(r.raw)
        text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')

        current_headers = []
        game_count = 0  # compteur de parties totales

        for line in text_stream:
            line = line.rstrip()
            if line.startswith("["):
                current_headers.append(line)
            elif current_headers:
                # fin du header
                if game_count % x == 0:
                    headers_sample.append("\n".join(current_headers))
                    if len(headers_sample) >= n:
                        break
                current_headers = []
                game_count += 1

    return headers_sample

# Exemple d'appel
periode = "2025-09"
sample_size = 100   # nombre de parties "gardées"
every_x = 10       # prendre une partie tous les 10
sample = debug_n_games_every_x(sample_size, periode, every_x)









#Extrait des Id de joueurs pour les parties classées extraites 
import re

stockage = set()  # set pour éviter les doublons

for game in sample:
    white_match = re.search(r'\[White "(.*?)"\]', game)
    black_match = re.search(r'\[Black "(.*?)"\]', game)
    event_match = re.search(r'\[Event "(.*?)"\]', game)

    if white_match and black_match and event_match:
        white = white_match.group(1)
        black = black_match.group(1)
        event = event_match.group(1).lower()

        if "rated" in event:
            stockage.add(white)
            stockage.add(black)

print(stockage)

