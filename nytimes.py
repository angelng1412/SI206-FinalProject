from fileinput import filename
from threading import local
from tkinter.tix import DirTree
from typing import final
from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import true

def database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def fetchData(db_name, conn, cur):
    # database connection
    conn, cur = database(db_name)
    # pull artist names from db
    res = cur.execute("""SELECT artist FROM artistinfo""")
    artists = res.fetchall()
    artists = [x[0] for x in artists]
    # print(artists)
    news_lst = {}
    for artist in artists:
        url = "https://www.nytimes.com/search?query=" + artist
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        tags = soup.find('div', class_ = 'css-nhmgdh')
        tag = tags.find('span', class_ = 'css-1dv1kvn').text.strip('Showingfor: ').replace(' ', "").replace('outof', "")
        final_tag = tag.replace('results', "")
        if len(final_tag) <= 2:
            artist_result = final_tag[1:].replace(",", "")
        elif len(final_tag) > 2:
            artist_result = final_tag[2:].replace(",", "")
        else:
            artist_result = 0
        news_lst[artist] = artist_result
    return news_lst

# curr, con = database("songstats.db")
# fetchData("songstats.db", curr, con)

def setUpNewsTable(news_lst, cur, conn):
    cur.execute("DROP TABLE IF EXISTS nynews")
    cur.execute("""CREATE TABLE IF NOT EXISTS nynews (name TEXT UNIQUE PRIMARY KEY, article_total INTEGER)""")
    conn.commit()
    cur.execute("""SELECT artist FROM artistinfo""")
    artists = cur.fetchall()
    artists = [x[0] for x in artists]
    for artist in artists:
        name = artist
        article_total = news_lst[artist]
        cur.execute("INSERT INTO nynews (name, article_total) VALUES (?, ?)", (name, article_total))
    conn.commit()

    cur.execute(
        """
        SELECT artistinfo.artist, article_total
        FROM nynews
        JOIN artistinfo ON nynews.name = artistinfo.artist
        GROUP BY article_total
        """
    )

    lst = cur.fetchall()
    # print(lst)

    finaldict = dict(lst)
    ylst = []
    for a in finaldict.keys():
        ylst.append(a)
    # print(ylst)
    
    xlst = []
    for a in finaldict.values():
        xlst.append(a)
    # print(xlst)
    
    color = ["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"]

    fig1, ax1 = plt.subplots()
    ax1.pie(xlst[-6:-1], labels=ylst[-6:-1], autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.legend()
    plt.title("Artists With Top 5 Number of Total Articles")
    plt.show()

    summ = sum(xlst[:-1])
    num = 0
    for a in xlst[:-1]:
        num += 1
    average = summ/num

    with open('nytimes.txt', 'w') as f:
        f.write('Average number of total articles: ')
        f.write(str(average))
        f.close()
    

def main():
    cur, conn = database('songstats.db')
    news_lst = fetchData("songstats.db", cur, conn)
    setUpNewsTable(news_lst, cur, conn)

main()
