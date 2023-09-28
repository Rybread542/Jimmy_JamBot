# -*- coding: utf-8 -*-

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize spotify client
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


# Uses Spotify API to search for an album given a title and an artist
# returns a link as a string
def get_album_URL(title, artist):
    
    # Attempts to retrieve an album from just a title string
    if artist == '':
        
        # Search album given title and print search to console for debugging
        album_tree = spotify.search(f'album:{title}', limit=1, offset=0, type='album', market='US')
        print(f'searching {title}')
        
        # Pulls link from album data returned by spotify search
        try:
            link = album_tree['albums']['items'][0]['external_urls']['spotify']
            return link
        
        # If the data doesn't return an accurate link, return 0
        except:
            print(f'cant find {title}')
            return 0
        
    # else if an artist is given, perform a more accurate search    
    else:
        
        album_tree = spotify.search(f'album:{title} artist:{artist}', limit=1, offset=0, type='album', market='US')
        print(f'searching {title} by {artist}')
        
        try:
            link = album_tree['albums']['items'][0]['external_urls']['spotify']
            return link
        
        except:
            print(f'cant find {title} by {artist}')
            return 0 
        

# Roughly same function as get_album_url but modified search parameters to link a specific song
def get_song_URL(title, artist):
    
    song_tree = spotify.search(f'track:{title} artist:{artist}', limit=1, offset=0, type='track', market='US')
    print(f'searching {title} by {artist}')
    
    try:
        link = song_tree['tracks']['items'][0]['external_urls']['spotify']
        return link
    
    except:
        print(f'cant find {title} by {artist}')
        return 0    


# Parses album data for relevant info and returns it as a dictionary
# For use in several album functions and for placing albums in SQL
# takes a spotify link or a spotify album ID as an input
def extract_album(link):
    
    # Grab album data from spotify in a dictionary of lists
    album_tree = spotify.album(link, 'US')
    
    # Set artist, title and release year based on static locations in
    # album data
    artist = album_tree['artists'][0]['name']
    title = album_tree['name']
    release_year = int(album_tree['release_date'][:4])
    
    # None of the album data ever has a genre. Doesn't seem to be anything
    # I can do about it for now
    # Sets genre to NONE
    genres = album_tree['genres']
    if len(genres) > 0:
        genre = genres[0]
    else:
        genre = 'NONE'
        
    # grabs list of album track data
    tracks = album_tree['tracks']['items']
    
    # initialize album length int
    length = 0
    
    # Iterate through track data and add each track length to total
    for track in range(len(tracks)):
        track_length = tracks[track]['duration_ms']
        length += track_length
    
    # convert milliseconds to minutes rounded down
    length = int(((length/1000)/60))
    
    # populate dictionary with album data
    album_data = {'artist': artist, 'title': title, 'year': release_year, 
                  'genre': genre, 'length': length}
    
    return album_data
    
    
