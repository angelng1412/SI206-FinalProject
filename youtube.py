import requests
import json
import sys
import os
import matplotlib
import sqlite3
import unittest
import csv
import matplotlib.pyplot as plt
# API client library
import googleapiclient.discovery


def database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return conn, cur

def fetchData(db_name):
    # database connection
    conn, cur = database(db_name)
    # pull artist names from db
    artists = cur.execute("SELECT artist FROM artistinfo LIMIT 10").fetchall()
    artists = [x[0] for x in artists] # list of artist names

    # API information
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = 'AIzaSyBoY-LgHz8TZI-sY7RFZcQIktB-OsDrnmg'
    # API client
    youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)

    for artist in artists:
    # get top 5 music videos by view count for each artist
    # TODO: put lines 38-60 in for loop looping through every artist 
        search_request = youtube.search().list(
                part="id,snippet",
                type='video',
                videoCategoryId=10, # music category id 
                q=artist + "Music Video",
                videoDefinition='high',
                maxResults=5,
                fields="items(id(videoId),snippet(publishedAt,channelId,channelTitle,title))"
        )
        search_response = search_request.execute()
        print(len(search_response['items']))
        print(search_response)

        # for each of the videos returned, get stats (e.g. views, likes, and comments counts)
        for video in search_response['items']:
            video_request = youtube.videos().list(
                part="id,statistics",
                id=video['id']['videoId'],
                fields="items"
            )

            video_response = video_request.execute()
            print(video_response)

def main():
    fetchData("songstats.db")

if __name__ == '__main__':
    main()