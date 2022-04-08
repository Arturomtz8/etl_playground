from db_creation import get_database, get_session, declarative_base
import requests
from datetime import datetime
import datetime
import json
from local_settings import spotify, user_spotify

DATABASE_LOCATION = get_database()
SESSION = get_session()
BASE = declarative_base()
USER_ID = user_spotify
TOKEN = spotify

if __name__ == "__main__":
    headers = {
        'Accept': "application/json",
        'Content-type': "application/json",
        'Authorization': f"Bearer {TOKEN}"
    }

    today = datetime.datetime.now()
    fifteen_days = today - datetime.timedelta(days=15)
    custom_unix_timestamp = int(datetime.datetime.timestamp(fifteen_days)) * 1000
    print(custom_unix_timestamp)

    # example taken from the web
    # presentDate = datetime.datetime.now()
    # unix_timestamp = datetime.datetime.timestamp(presentDate)*1000
    # print(unix_timestamp)

    r = requests.get(f'https://api.spotify.com/v1/me/player/recently-played?limit=10&after={custom_unix_timestamp}', headers=headers)
    data = r.json()

    # with open('spotify_json', 'w') as f:
    #     data_str = json.dumps(data)
    #     f.write(data_str)
    
    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
    

    print(song_names, artist_names, played_at_list, timestamps)

