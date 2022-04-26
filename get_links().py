from fileinput import filename
from threading import local
from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest

from sqlalchemy import true



def get_links():
    url = "https://genius.com/artists/Post-malone"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    link_list = []
    tags = soup.find_all('div', class_ = 'mini_card-info')
    print(tags)

    # for tag in tags:
    #     each_song = tag.find('span')
    #     print(each_song)


def main():
    get_links()


main()
