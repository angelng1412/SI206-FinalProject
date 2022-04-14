import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as urllib
import csv, sqlite3, os

class Spotify:
    def get_data(self, fhand, playlist_dictionary):
        for i in range(len(fhand)):
            # uniqname_dictionary[fhand["Username of Playlist Creator"][i]] = fhand["Uniqname"][i]              # don't rly need this

            # splits the playlist link into a useable id
            a = fhand["Spotify Playlist Link"][i].split("playlist/")
            playlistid = a[1]

            # inserts id to dictionary of spotify usernames
            playlist_dictionary[fhand["Number"][i]] = playlistid


    def playlist_sql(self, db_name, key, playlist_id, count):
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+db_name)
        cur = conn.cursor()

        # create the table
        if (count == 0):
            cur.execute("DROP TABLE IF EXISTS songstats")
            
        cur.execute("CREATE TABLE IF NOT EXISTS songstats (artist TEXT PIMARY KEY, track_name TEXT UNIQUE, danceability NUMERIC, energy NUMERIC, tempo NUMERIC)")

        # searches the playlist
        print(key)
        print(playlist_id)

        # gathers the json file data
        tracks = sp.user_playlist_tracks(user = key, playlist_id = playlist_id)["tracks"]
        playlist = tracks["items"]

        # for loop size
        size = 25

        if (len(playlist) < 25):
            size = len(playlist)

        for track in playlist[:size]:
            # if can't find track... continue
            if (track["track"] == None):
                 continue

            # gets audio features
            audio_features = sp.audio_features(track["track"]["id"])[0]

            danceability = audio_features["danceability"]
            energy = audio_features["energy"]
            tempo = audio_features["tempo"]

            cur.execute(
                """
                INSERT OR IGNORE INTO songstats (artist, track_name, danceability, energy, tempo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (track["track"]["artists"][0]["name"], track["track"]["name"], danceability, energy, tempo)
            )

        conn.commit()

        ########################################################################################################################

        # second table
        # create the table
        if (count == 0):
            cur.execute("DROP TABLE IF EXISTS artistinfo")
            
        cur.execute("CREATE TABLE IF NOT EXISTS artistinfo (artist TEXT PIMARY KEY UNIQUE, followers INTEGER, genre1 TEXT, genre2 TEXT, genre3 TEXT)")

        # for loop size
        size = 25

        if (len(playlist) < 25):
            size = len(playlist)

        for track in playlist[:size]:
            # if can't find track... continue
            if (track["track"] == None):
                 continue

            # get artist info
            artist_info = sp.artist(track["track"]["artists"][0]["id"])

            followers = artist_info["followers"]["total"]
            genre1 = None
            genre2 = None
            genre3 = None

            if (len(artist_info["genres"]) > 0):
                genre1 = artist_info["genres"][0]

            if (len(artist_info["genres"]) > 1):
                genre2 = artist_info["genres"][1]

            if (len(artist_info["genres"]) > 2):
                genre3 = artist_info["genres"][2]


            cur.execute(
                """
                INSERT OR IGNORE INTO artistinfo (artist, followers, genre1, genre2, genre3)
                VALUES (?, ?, ?, ?, ?)
                """,
                (track["track"]["artists"][0]["name"], followers, genre1, genre2, genre3)
            )

        conn.commit()


    def data_processing(self, db_name):
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+db_name)
        cur = conn.cursor()



def join_sql(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT artistinfo.genre1, Avg(artistinfo.followers), Avg(songstats.danceability), Avg(songstats.energy), Avg(songstats.tempo)
        FROM songstats
        INNER JOIN artistinfo ON songstats.artist = artistinfo.artist
        GROUP BY artistinfo.genre1
        """
        )

    # fetch all lines in the table (as tuples)
    res = cur.fetchall()
    conn.commit()

    for data in res:
        print(data)










def main():
    # count variable
    count = 0

    a = Spotify()

    # initialize fname 
    fname = input("Enter .csv filename: ")

    while (fname != "quit"):
        playlist_dictionary = dict()

        # read the file
        try:
            fhand = pd.read_csv(fname)

        except:
            print("Cannot open file.")
            exit()

        a.get_data(fhand, playlist_dictionary)
   

        # function for reading through all individual playlists
        for i in range(len(playlist_dictionary)):
            # get key and playlist id from list... key is just Spotify's playlists
            key = "Spotify"
            id = list(playlist_dictionary.values())[i]

            a.playlist_sql("songstats.db", key, id, count)

            # keep track of executions
            count += 1
            print("Executed " + str(count) + " time(s)\n")

        fname = input("Enter .csv filename or quit: ")

    join_sql("songstats.db")


client_id = input("what's your client id?: ")
client_secret = input("what's your client secret?: ")

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

main()