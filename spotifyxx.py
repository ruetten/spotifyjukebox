import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import time

"""
export SPOTIPY_CLIENT_ID='524a3c5def4d4cb08a4b98c48458543d'
export SPOTIPY_CLIENT_SECRET='5a4424bde8664bffbc2f8d55658f98f6'
export SPOTIPY_REDIRECT_URI='http://google.com/'
python3 spotifyxx.py 22uiuzjxpc7khi3pprxs2lqma
"""

# Get the username from terminal
username = sys.argv[1]
scope = 'user-read-private user-read-playback-state user-modify-playback-state'

# user ID spotify:user:22uiuzjxpc7khi3pprxs2lqma

# Erase chae and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

# Create our spotiyObject
spotifyObject = spotipy.Spotify(auth=token)

# get device information
devices = spotifyObject.devices()
print(json.dumps(devices, sort_keys=True, indent=4))
deviceID = devices['devices'][0]['id']

# current track playing
track = spotifyObject.current_user_playing_track()
print(json.dumps(track, sort_keys=True, indent=4))
print()
artist = track['item']['artists'][0]['name']
track = track['item']['name']

if artist != "":
    print("Currently playing " + artist + " - " + track)

# user info
user = spotifyObject.current_user()

displayName = user['display_name']
followers = user['followers']['total']

while True:
    
    print()
    print("WELCOME TO THE SPOTIFY JUKEBOX " + displayName)
    print("YOU HAVE " + str(followers) + " FOLLOWERS.")
    print()
    print("0 - Search for an artist")
    print("1 = exit")
    print()
    choice = input("Your choice: ")
    
    # Search for artist
    if choice == "0":
        print()
        searchQuery = input("Artist name: ")
        print()
        
        # Get search results
        searchResults = spotifyObject.search(searchQuery, 1, 0, "artist")
        
        # Artist details
        artist = searchResults['artists']['items'][0]
        
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print(artist['genres'][0])
        print()
        webbrowser.open(artist['images'][0]['url'])
        time.sleep(3)
        os.system("pkill -o chromium")
        
        artistID = artist['id']
        
        # Album and track details
        trackURIs = []
        trackArt = []
        z = 0
        
        # Extract album data
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']

        for item in albumResults:
            print("ALBUM " + item['name'])
            albumID = item['id']
            albumArt = item['images'][0]['url']
            
            # Extract track data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']
            
            for item in trackResults:
                print(str(z) + ": " + item['name'])
                trackURIs.append(item['uri'])
                trackArt.append(albumArt)
                z += 1
            print()
                
        # See album art
        while True:
            songSelection = input("Enter a song number to see album art associated (x to exit)")
            if songSelection == "x":
                break
            trackSelectionList = []
            trackSelectionList.append(trackURIs[int(songSelection)])
            spotifyObject.start_playback(deviceID, None, trackSelectionList)
            webbrowser.open(trackArt[int(songSelection)])
            time.sleep(3)
            os.system("pkill -o chromium")
            
    # End the program
    if choice == "1":
        break
    
    # print(json.dumps(VARIABLE, sort_keys=True, indent=4))
