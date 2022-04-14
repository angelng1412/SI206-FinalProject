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
    # create music videos table if it doesn't exist
    cur.execute("""CREATE TABLE IF NOT EXISTS musicvideos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    views INTEGER, 
                    likes INTEGER, 
                    comments INTEGER)""")
    # pull artist names from db
    artists = cur.execute("""SELECT artist FROM artistinfo 
                            WHERE artist NOT IN 
                            (SELECT artist from musicvideos)
                            LIMIT 5""").fetchall()
    artists = [x[0] for x in artists] # list of artist names

    print(artists)

    # API information
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = 'AIzaSyBMsk07FQ1eNeZUIHLX4TTZe__Hc4BeJNE'
    # API client
    youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)

    for artist in artists:
    # get top 5 music videos by view count for each artist
        search_req = youtube.search().list(
                part="id,snippet",
                type='video',
                videoCategoryId=10, # music category id 
                q=artist + "Music Video",
                videoDefinition='high',
                maxResults=5,
                fields="items(id(videoId),snippet(title))"
        )
        search_resp = search_req.execute()
        # print(search_resp)

        # for each of the videos returned, get stats (e.g. views, likes, and comments counts)
        for video in search_resp['items']:
            # if video result does not actually belong to artist, skip
            if artist not in video['snippet']['title']:
                continue

            video_req = youtube.videos().list(
                part="id,snippet,statistics",
                id=video['id']['videoId'],
                fields="items(id,snippet(title,channelTitle),statistics(viewCount,likeCount,commentCount))"
            )

            video_resp = video_req.execute()
            print(video_resp)
            
            target = video_resp['items'][0]
            # insert video into db
            cur.execute("""INSERT OR IGNORE INTO musicvideos (youtube_id, title, channel, artist, views, likes, comments) 
                            VALUES(?, ?, ?, ?, ?, ?, ?)""", 
                            (target['id'], 
                            target['snippet']['title'],
                            target['snippet']['channelTitle'],
                            artist,
                            target['statistics']['viewCount'],
                            target['statistics'].get('likeCount', -1),
                            target['statistics']['commentCount']))

    conn.commit()

def calculate_average_views(db_name):
    # connect to database
    conn, cur = database(db_name)

    # get unique artist names
    artists = cur.execute("SELECT DISTINCT artist FROM musicvideos").fetchall()
    artists = [x[0] for x in artists] # list of artist names

    avg_views = {}
    for artist in artists:
        views = cur.execute("SELECT views FROM musicvideos WHERE artist = ?", (artist,)).fetchall()
        views = [x[0] for x in views]
        avg_views[artist] = sum(views) / len(views)

    return avg_views

def calculate_average_likes(db_name):
    # connect to database
    conn, cur = database(db_name)

    # get unique artist names
    artists = cur.execute("SELECT DISTINCT artist FROM musicvideos").fetchall()
    artists = [x[0] for x in artists] # list of artist names

    avg_likes = {}
    for artist in artists:
        likes = cur.execute("SELECT likes FROM musicvideos WHERE artist = ?", (artist,)).fetchall()
        likes = [x[0] for x in likes]
        avg_likes[artist] = sum(likes) / len(likes)

    return avg_likes

def write_avgs(filename):
    pass

def scatterplot(db_name, file):

    # connect to database
    conn, cur = database(db_name)

    # get artists, followers on spotify, and average views from top music videos
    results = cur.execute("""SELECT a.artist, a.followers, m.views FROM 
                            (SELECT artist, AVG(views) as views FROM musicvideos GROUP BY artist) AS m 
                            JOIN artistinfo AS a 
                            ON a.artist = m.artist""").fetchall()
    # print(results)
    followers = []
    avg_views = []
    dir = os.path.dirname(file)
    outfile = open(os.path.join(dir, file), "w")
    writer = csv.writer(outfile, delimiter=",")
    writer.writerow(('artist', 'followers', 'average views'))
    for row in results:
        writer.writerow(row) # write artist name, spotify followers, and average views on music videos to csv
        followers.append(row[1])
        avg_views.append(row[2])
    outfile.close()

    fig, ax = plt.subplots()
    ax.scatter(followers, avg_views, alpha=0.8, edgecolors='none', s=30)
    ax.ticklabel_format(useOffset=False, style='plain')
    plt.title('Hello')
    ax.set_ylabel('Average number of views')
    ax.set_xlabel('Number of followers on Spotify')
    plt.tight_layout()
    plt.savefig("followersviews.png")
        

def main():
    # fetchData("songstats.db")
    # avg_views = calculate_average_views("songstats.db")
    # avg_likes = calculate_average_likes("songstats.db")
    scatterplot("songstats.db", "followersvsviews.csv")

if __name__ == '__main__':
    main()