import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as urllib
import csv, sqlite3, os
import matplotlib.pyplot as plt

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

    # create dictionary for followers, danceability, energy, tempo
    follower_dict = dict()
    danceability_dict = dict()
    energy_dict = dict()
    tempo_dict = dict()

    # open a text file and write the calculations
    with open("Average_artist_followers_by_genre.txt", 'w') as f:
        with open("Average_genre_danceability.txt", 'w') as g:
            with open("Average_genre_energy.txt", 'w') as h:
                with open("Average_genre_tempo.txt", 'w') as i:
                    # write the header first:
                    f.write("Genre, Average Artist Followers")
                    f.write('\n')

                    g.write("Genre, Average Danceability")
                    g.write('\n')

                    h.write("Genre, Average Energy")
                    h.write('\n')

                    i.write("Genre, Average Tempo")
                    i.write('\n')


                    # go through each row
                    for data in res:
                        # write to text file
                        f.write(str(data[0]) + ", " + str(data[1]))
                        f.write('\n')

                        g.write(str(data[0]) + ", " + str(data[2]))
                        g.write('\n')

                        h.write(str(data[0]) + ", " + str(data[3]))
                        h.write('\n')

                        i.write(str(data[0]) + ", " + str(data[4]))
                        i.write('\n')

                        # store in dictionaries
                        follower_dict[data[0]] = data[1]
                        danceability_dict[data[0]] = data[2]
                        energy_dict[data[0]] = data[3]
                        tempo_dict[data[0]] = data[4]

                    # close files
                    i.close()
                h.close()
            g.close()
        f.close()

    visualization(follower_dict, danceability_dict, energy_dict, tempo_dict)


def visualization(follower_dict, danceability_dict, energy_dict, tempo_dict):
    # get data
    fnames = list(follower_dict.keys())
    fvalues = list(follower_dict.values())

    dnames = list(danceability_dict.keys())
    dvalues = list(danceability_dict.values())

    enames = list(energy_dict.keys())
    evalues = list(energy_dict.values())

    tnames = list(tempo_dict.keys())
    tvalues = list(tempo_dict.values())

    # format: range(len(dict)), values, names
    color = ["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"]

    # follower data
    plt.barh(range(len(follower_dict)), fvalues, tick_label=fnames, color=color)
    plt.yticks(fontsize=5)
    plt.suptitle("Average Follower Count Per Top Genre")
    plt.xlabel("Average Follower Count")
    plt.ylabel("Genre from the Top Songs")
    plt.tight_layout()
    plt.savefig("follower_data.png")

    plt.clf()

    # danceability data
    plt.barh(range(len(danceability_dict)), dvalues, tick_label=dnames, color=color)
    plt.yticks(fontsize=5)
    plt.suptitle("Average Danceability of Each Top Genre")
    plt.xlabel("Average Danceability")
    plt.ylabel("Genre from the Top Songs")
    plt.tight_layout()
    plt.savefig("danceability_data.png")

    plt.clf()

    # energy data
    plt.barh(range(len(energy_dict)), evalues, tick_label=enames, color=color)
    plt.yticks(fontsize=5)
    plt.suptitle("Average Energy of Each Top Genre")
    plt.xlabel("Average Energy")
    plt.ylabel("Genre from the Top Songs")
    plt.tight_layout()
    plt.savefig("energy_data.png")

    plt.clf()

    # energy data
    plt.barh(range(len(tempo_dict)), tvalues, tick_label=tnames, color=color)
    plt.yticks(fontsize=5)
    plt.suptitle("Average Tempo of Each Top Genre")
    plt.xlabel("Average Tempo")
    plt.ylabel("Genre from the Top Songs")
    plt.tight_layout()
    plt.savefig("tempo_data.png")

    plt.clf()



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