from db_creation import get_database
import requests
from datetime import datetime
import datetime
import json
import pandas as pd
from local_settings import spotify, user_spotify

DATABASE = get_database()
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
    
    # check that all the timestamps are from at least the last week
    last_week = datetime.datetime.now() - datetime.timedelta(days=7)
    last_week = last_week.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    print(timestamps)
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') < last_week:
            print(datetime.datetime.strptime(timestamp, '%Y-%m-%d'), "-----DATETIME")
            print(last_week, "------last week")
            raise Exception("At least one of the returned songs was played before last week")
            

    return True
if __name__ == "__main__":
    headers = {
        'Accept': "application/json",
        'Content-type': "application/json",
        'Authorization': f"Bearer {TOKEN}"
    }

    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    last_week_unix_timestamp = int(last_week.timestamp()) * 1000
    print(last_week_unix_timestamp, "---------UNIXTIMESTAMP")

    r = requests.get(f'https://api.spotify.com/v1/me/player/recently-played?limit=10&after={last_week_unix_timestamp}', headers=headers)
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


    # load songs to db
    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """
 
    with DATABASE.connect() as conn:
        conn.execute(sql_query)
        print("Opened database successfully")
        try:
            song_df.to_sql("my_played_tracks", DATABASE, index=False, if_exists='append')
        except Exception as e:
            print(e)
    
    print("database closed")

