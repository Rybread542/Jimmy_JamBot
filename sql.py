# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 19:19:45 2023

@author: soycd
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd = user_password,
            database = db_name
            )
        
        print("Connected to db")
        
    except Error as e:
        print(f"The error '{e}' occurred")
            
    return connection

load_dotenv()
sql_host = os.getenv('SQL_HOST')
sql_user = os.getenv('SQL_USER')
sql_pass = os.getenv('SQL_KEY')
sql_db = os.getenv('SQL_DEFAULT_DB')
    
connection = create_connection(sql_host, sql_user, sql_pass, sql_db)

pool_ids_nicknames = {'its.mahover': 1, 'riley': 1, 'riling': 1, 'emeritus': 1, 'mark': 2, 
        'themagicalmark': 2, 'markus': 2, 'simon': 3, 'amanita.': 3, 'amanita': 3,
        'kibie': 4, 'waylon': 4, 'angie': 5, 'ngeezy': 5, 'annie': 5, 'quinton': 6, 'quantumvevo': 6,
        'vinie': 7, 'vince': 7, 'viniebara': 7, 'ryan': 8, 'rybread': 8, 'ry': 8, 'ry.bread': 8,
        'YYB': 9, 'yungyaboi': 9, 'brandon': 9}

pool_names_from_id = {1: 'Riley', 2: 'Mark', 3: 'Simon', 4: 'Kibie', 
                      5: 'Angie', 6: 'Quinton', 7: 'Vinie', 8: 'Ryan', 9: 'Brandon'}

def get_pool_names_from_id(pool_id):
    return pool_names_from_id[pool_id]
    
def get_pool_id_from_name(name):
    return pool_ids_nicknames[name]

def pools():
    return {'its.mahover': 'riley', 'themagicalmark': 'mark', 'amanita.':'simon', 
             'kibie': 'kibie', 'ngeezy': 'angie', 'quantumvevo': 'quinton',
             'vinibara': 'vinie', 'ry.bread': 'ryan', 'yungyaboi': 'brandon'}
    
           
def execute_read_query(query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"the error '{e}' occurred")
        
def insert_album(data):
    cursor = connection.cursor()
    try:
        insert_string = f"INSERT INTO albums(artist, title, release_year, genre, length, pool_id) VALUES ('{data['artist']}', '{data['title']}', {data['year']}, '{data['genre']}', {data['length']}, {data['pool_id']})"
        cursor.execute(insert_string)
        connection.commit()
        print(f"Successfully entered the following album: '{data['artist']}', '{data['title']}', {data['year']}, '{data['genre']}', {data['length']}, {data['pool_id']}")
    except Error as e:
        print(f"the error '{e}' occurred")
        
def remove_album_from_pool(title, artist, pool_id):
    cursor = connection.cursor()
    
    try:
        remove_string = f"DELETE FROM albums WHERE title = '{title}' AND artist = '{artist}' AND pool_id = {pool_id}"
        cursor.execute(remove_string)
        connection.commit()
        name = get_pool_names_from_id(pool_id)
        print(f"Successfully removed the following album: {artist} | {title} from {name}\'s pool")
        
    except Error as e:
        print(f"the error '{e}' occurred")
        
def remove_album_from_db(title, artist):
    cursor = connection.cursor()
    
    try:
        remove_string = f"DELETE FROM albums WHERE title = '{title}' AND artist = '{artist}'"
        cursor.execute(remove_string)
        connection.commit()
        print(f"Successfully removed the following album: {artist} | {title} from the database.")
        
    except Error as e:
        print(f"the error '{e}' occurred")
        
def get_pool_id(name):
    pool_id_list = execute_read_query(f"SELECT id FROM pools WHERE name = '{name}'")
    try:
        pool_id = pool_id_list[0][0]
        return pool_id
    except Error as e:
        print(f"the error '{e}' occurred")
    
def get_pool(pool_id):
    return execute_read_query(f"SELECT artist, title, release_year, genre, length FROM albums WHERE pool_id = {pool_id}")
          
def query_title(title):
    return f"SELECT * FROM albums WHERE title = '{title}'"

def is_in_db(title, artist):
    result = execute_read_query(f"SELECT title, artist FROM albums WHERE title = '{title}' AND artist = '{artist}'")
    return bool(result)
    
def check_duplicate(title, artist, pool_id):
    result = execute_read_query(f"SELECT title, artist FROM albums WHERE title = '{title}' AND artist = '{artist}' AND pool_id = {pool_id}")
    return bool(result)
        
def get_random_album_from_pool(pool_name):
    pool_id = pool_ids_nicknames[pool_name.lower()]
    album = execute_read_query(f"SELECT artist, title, pool_id FROM albums WHERE pool_id = {pool_id} ORDER BY RAND() LIMIT 1")
    return album

def get_random_album_from_db():
    album = execute_read_query("SELECT artist, title, pool_id FROM albums ORDER BY RAND() LIMIT 1")
    return album

def get_next_album_member():
    return execute_read_query("SELECT id FROM pools WHERE order_id = 1")[0][0]

def decrement_album_members():
    num_members = execute_read_query("SELECT order_id FROM pools ORDER BY order_id DESC LIMIT 1")[0][0]
    cursor = connection.cursor()
    try:
        for i in range(1, num_members+1):
              cursor.execute(f'UPDATE pools SET order_id = {i-1} WHERE order_id = {i}')
              connection.commit()
              
        cursor.execute(f'UPDATE pools SET order_id = {num_members} WHERE order_id = 0')
        connection.commit()
          
    except Error as e:
        print(f"the error '{e}' occurred")
    
    
    
