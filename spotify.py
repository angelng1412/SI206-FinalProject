import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as urllib

client_id = input("what's your client id?: ")
client_secret = input("what's your client secret?: ")

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


class Spotify:
    def call_playlist(self, username, playlist_id):
            # this is what each track holds
            playlist_features_list = ["popularity_index", "album_release_date", "artist", "album","track_name",  "track_id", "danceability",
                                      "energy","key","loudness","mode", "speechiness","instrumentalness",
                                      "liveness","valence","tempo", "duration_ms","time_signature"]

            # begins to create the data table
            playlist_df = pd.DataFrame(columns = playlist_features_list)

            # searches the playlist
            print(username)
            print(playlist_id + '\n')

            # makes it so returns more than limit = 100
            tracks = sp.user_playlist_tracks(user = username, playlist_id = playlist_id)["tracks"]
            playlist = tracks["items"]
            while (tracks["next"]):
                tracks = sp.next(tracks)
                playlist.extend(tracks["items"])

    
            for track in playlist:
                # get playlist features
                playlist_features = {}
            
                if (track["track"] == None):
                    continue

                print(track["track"]["popularity"])
                playlist_features["popularity_index"] = track["track"]["popularity"]
                playlist_features["album_release_date"] = track["track"]["album"]["release_date"]
                playlist_features["artist"] = track["track"]["artists"][0]["name"]
                playlist_features["album"] = track["track"]["album"]["name"]
                playlist_features["track_name"] = track["track"]["name"]
                playlist_features["track_id"] = track["track"]["id"]

                # audio features
                audio_features = sp.audio_features(playlist_features["track_id"])[0]

                for feature in playlist_features_list[6:]:
                    playlist_features[feature] = audio_features[feature]


                track_df = pd.DataFrame(playlist_features, index = [0])
                playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)

            return playlist_df
