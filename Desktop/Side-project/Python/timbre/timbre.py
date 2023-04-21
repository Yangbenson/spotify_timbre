import json
import random
import warnings
import spotipy
import spotipy.util as util
import requests
import pandas as pd
import datetime
import numpy as np
import pymysql
from ML_function import strFilter,URL_scraper


total_songs = pd.DataFrame()

username = 'Benson yang'
scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope,
                                   client_id='d0ec07ad19d247f3b12aad4821097d5d',
                                   client_secret='e52c914739db43f7b0c00909c3dd7cc7',
                                   # 注意需要在自己的web app中添加redirect url
                                   redirect_uri='http://localhost:8888/callback')
headers = {"Authorization": "Bearer {}".format(token), "Accept-Language": "en"}

# responses = requests.get("https://api.spotify.com/v1/playlists/37i9dQZEVXbNG2KDcFcKOF", headers=headers)

# "https://open.spotify.com/genre/section0JQ5DAzQHECxDlYNI6xD1h" top 50
# "https://open.spotify.com/genre/section0JQ5IMCbQBLoSVpnseIhn6" pop
# "https://open.spotify.com/genre/section0JQ5IMCbQBLvzsc9IsbuOK" K pop
# "https://open.spotify.com/genre/section0JQ5IMCbQBLvhGBYx1XOBO" chill
# "https://open.spotify.com/genre/section0JQ5IMCbQBLimFASeYpIu3" Classic Blue
# "https://open.spotify.com/genre/section0JQ5IMCbQBLjM0PD2WsCNe" Electronic
# "https://open.spotify.com/genre/section0JQ5IMCbQBLuRvGbRRoxQW" R&B
# "https://open.spotify.com/genre/section0JQ5IMCbQBLnjETREflcqJ" HH

table_name = 'Pop'

URLs = URL_scraper.Spotify_Genre_scraper("https://open.spotify.com/genre/section0JQ5IMCbQBLoSVpnseIhn6")
for n, i in enumerate(URLs):
    responses = requests.get("https://api.spotify.com/v1/playlists/" + i, headers=headers)
    myjson_data = json.loads(responses.text)

    # song's detail
    songs_analysis = []
    songs_r_date = []
    songs_artist = []
    songs_popularity = []
    songs_length = []
    songs_names = []

    def get_song_attributes(response_text):
        return json.loads(response_text)

    def diff(x):
        result = []

        for i,j in zip(x.iloc[-1],x.iloc[0]):
            result.append(round(i-j, 4))

        return result

    # 这边先放其中一个歌单的歌曲请求
    for i in myjson_data.get('tracks')['items']:
        if i['track'] is not None and i['track']['uri'] is not None and len(i['track']['uri'].split(':')[2]) != 0:
            song_ids = i['track']['uri'].split(':')[2]
            # print(song_ids)
            song_name = i['track']['name']
            song_popularity = i['track']['popularity']

            if len(i['track']['album']['release_date']) == 4:
                song_r_date = i['track']['album']['release_date'] + "-01-01"
            else:
                song_r_date = i['track']['album']['release_date']

            song_artist = i['track']['artists'][0]['name']
            song_length = i['track']['duration_ms']

            song_analysis = requests.get(f"https://api.spotify.com/v1/audio-analysis/{song_ids}", headers=headers)
            data = get_song_attributes(song_analysis.text)
            song_segments = pd.DataFrame(data["segments"])

            # 把秒的小數去掉
            song_segments["start"] = np.array(song_segments["start"]).round(0)
            # 把每一段的尾數減去頭數
            timbre = song_segments.groupby("start")['timbre'].agg(diff)

            print(len(timbre))
            songs_analysis.append(timbre)
            songs_names.append(song_name)
            songs_r_date.append(song_r_date)
            songs_artist.append(song_artist)
            songs_length.append(song_length)
            songs_popularity.append(song_popularity)

        else:
            continue

    # add name to song attributes
    songs = pd.DataFrame()
    songs['timbre'] = songs_analysis
    songs['length'] = songs_length
    songs['song_name'] = songs_names
    songs['release_date'] = songs_r_date
    songs['artist'] = songs_artist
    songs['popularity'] = songs_popularity


    # all in one
    total_songs = pd.concat([total_songs, songs]).reset_index(drop=True)
    print(n, 'times')

    if n == 15:
        break

# print(total_songs.columns)
# print(total_songs["mode"].describe())
# print(total_songs)

# insert to database ------------------------------------------------
def SQL(table, db, kind, df_insert=""):
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d")

    try:
        db_settings = {
            "host": "18.217.232.100",
            "port": 3306,
            "user": "benson",
            "password": "",
            "db": "my_db",
            "charset": "utf8"
        }
        conn = pymysql.connect(**db_settings)

        if kind == "create":
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS "'`' + str(date_time_str) + '_' + table + '`')

                cursor.execute(
                    'CREATE TABLE ' + '`' + str(date_time_str) + '_' + table + '`(' +
                    '`id` INT NOT NULL AUTO_INCREMENT,' +
                    '`timbre` TEXT,' +
                    '`length` FlOAT NOT NULL,' +
                    '`song_name` VARCHAR(128),' +
                    '`release_date` DATE,' +
                    '`artist` VARCHAR(128),' +
                    '`popularity` FlOAT NOT NULL,' +
                    'PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
                )

        if kind == "insert":

            df = df_insert

            values = []

            for i in range(len(df)):
                values.append(tuple(df.iloc[i, :]))

            head = 'INSERT INTO ' + db + ".`" + str(
                date_time_str) + "_" + table + """` (timbre,length,song_name,release_date,artist,popularity) """ \
                   + """VALUES (%s, %s, %s, %s, %s, %s)"""

            print('-------------print query--------------')
            # print(head)
            print(values)
            with conn.cursor() as cursor:
                cursor.executemany(str(head), (values))
                insert = cursor.fetchall()
                conn.commit()
                conn.close()

            print(insert)

    except Exception as err:
        print(err)

        conn.close()
        raise (err)

data = total_songs[['timbre','length','song_name','release_date','artist','popularity']]

total_songs.to_csv(
    'timbre.csv',  # 檔案名稱
    encoding='utf-8-sig',  # 編碼
    index=True  # 是否保留index
)

# import to database
SQL(table_name, "my_db", "create")
SQL(table_name, "my_db", "insert", data)

