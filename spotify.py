import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as urllib
import csv
import sqlite3
import os


client_id = input("what's your client id?: ")
client_secret = input("what's your client secret?: ")

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

class Spotify:
    def get_data(self, playlist_dictionary):
        fname = input("Enter .csv filename: ")
        try:
            fhand = pd.read_csv(fname)

        except:
            print("Cannot open file.")
            exit()

        for i in range(len(fhand)):
            # uniqname_dictionary[fhand["Username of Playlist Creator"][i]] = fhand["Uniqname"][i]              # don't rly need this

            # splits the playlist link into a useable id
            a = fhand["Spotify Playlist Link"][i].split("playlist/")
            playlistid = a[1]

            # inserts id to dictionary of spotify usernames
            playlist_dictionary[fhand["Number"][i]] = playlistid


    def playlist_sql(self, db_name, key, playlist_id):
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+db_name)
        cur = conn.cursor()

        # create the table
        cur.execute("DROP TABLE IF EXISTS songstats")
        cur.execute("CREATE TABLE songstats (artist TEXT PIMARY KEY, track_name TEXT, danceability NUMERIC, energy NUMERIC, tempo NUMERIC)")

        # searches the playlist
        print(key)
        print(playlist_id + '\n')

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


def main():
    a = Spotify()
    playlist_dictionary = dict()

    a.get_data(playlist_dictionary)

    # function for reading through all individual playlists
    for i in range(len(playlist_dictionary)):
        # get key and playlist id from list... key is just Spotify's playlists
        key = "Spotify"
        id = list(playlist_dictionary.values())[i]

        a.playlist_sql("songstats.db", key, id)


main()