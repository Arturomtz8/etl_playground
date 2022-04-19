from db_creation import get_database, get_session, declarative_base
import requests
from datetime import datetime
import datetime
import json
import pandas as pd
from local_settings import spotify, user_spotify

DATABASE_LOCATION = get_database()
SESSION = get_session()
BASE = declarative_base()
USER_ID = user_spotify
TOKEN = spotify

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # check if df is empty
    if df.empty:
        print('No songs recently listened. Finishing execution')
        return False
    
    # check primary key is unique
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # check for nulls in the df
    if df.isnull().values.any():
        raise Exception ("Null values found")
    
    # check that all the timestamps are from at least yesterday
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    print(timestamps)
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') < yesterday:
            print(datetime.datetime.strptime(timestamp, '%Y-%m-%d'), "-----DATETIME")
            print(yesterday, "------YESTERDAY")
            raise Exception("At least one of the returned songs was played before yesterday")
            

    return True
if __name__ == "__main__":
    headers = {
        'Accept': "application/json",
        'Content-type': "application/json",
        'Authorization': f"Bearer {TOKEN}"
    }

    # today = datetime.datetime.now()
    # yesterday = today - datetime.timedelta(days=1)
    # print(yesterday, "--------YESTERDAY FROM MAIN")
    # custom_unix_timestamp = int(datetime.datetime.timestamp(yesterday)) * 1000
    # print(custom_unix_timestamp)

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000
    print(yesterday_unix_timestamp, "---------UNIXTIMESTAMP")

    # example taken from the web
    # presentDate = datetime.datetime.now()
    # unix_timestamp = datetime.datetime.timestamp(presentDate)*1000
    # print(unix_timestamp)

    r = requests.get(f'https://api.spotify.com/v1/me/player/recently-played?limit=10&after={yesterday_unix_timestamp}', headers=headers)
    data = r.json()
    # print(data)
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

    # print(song_names, artist_names, played_at_list, timestamps)

    # prepare a dict to convert it to a dataframe
    songs_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps
    }

    song_df = pd.DataFrame(songs_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])


    if check_if_valid_data(song_df):
        print('Data valid, proceed to Load stage')