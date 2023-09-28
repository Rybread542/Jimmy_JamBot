# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 15:04:30 2023

@author: soycd
"""

import bot
import spotify
import sql
import requests
from bs4 import BeautifulSoup as bs

query = 'https://open.spotify.com/album/0GqpoHJREPp0iuXK3HzrHk?si=7zQDgJaaTGu_Zd0VfqLM5Q'
album = spotify.spotify.album(query, 'US')
print(album['artists'][0]['name'])
print(album['genres'])
print(album['name'])
print(album['release_date'])



print(sql.execute_read_query("SELECT order_id FROM pools ORDER BY order_id DESC LIMIT 1")[0][0])





