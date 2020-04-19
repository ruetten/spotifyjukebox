import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
from time import sleep
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests

default_image = "https://yt3.ggpht.com/-oSs8fntDxuw/AAAAAAAAAAI/AAAAAAAAAAA/17pzJmg8Gds/s900-c-k-no-mo-rj-c0xffffff/photo.jpg"
current_track = None

"""
export SPOTIPY_CLIENT_ID='524a3c5def4d4cb08a4b98c48458543d'
export SPOTIPY_CLIENT_SECRET='5a4424bde8664bffbc2f8d55658f98f6'
export SPOTIPY_REDIRECT_URI='http://google.com/'
python3 jukebox.py 22uiuzjxpc7khi3pprxs2lqma
"""
class Serv(BaseHTTPRequestHandler):
    def do_GET(self):
        sleep(0.1)
        get_current_track()
        if self.path == '/':
            self.path = '/index.html'
        try:
            f = open(self.path[1:])
            file_to_open = f.read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
        try:
            f.close()
        except:
            pass

def host_server():
    httpd = HTTPServer(('localhost', 8080), Serv)
    httpd.serve_forever()
    
def edit_html(image_url, artist, track):
    f = open('index.html', 'w')
    f.write("<!DOCTYPE html><html><head><title>Spotify Jukebox</title></head>")
#     f.write("<body style=>")
#     f.write("<body style=\"\">")
    f.write("<body style=text-align:center;font-family:courier;background-color:#1DB954>")
    f.write("<h1>" + artist + " - " + track + "</h1><img src=\"")
    f.write(image_url)
    f.write("\">")
    f.write("<h1>SPOTIFY JUKEBOX</h1><h2>BY RUETTEN<h2></body></html>")
    f.close()
    if track != current_track:
        os.system("pkill -o chromium")
        sleep(1)
        webbrowser.open("http://localhost:8080/")
    
def get_current_track():
    # current track playing
    global current_track
    track = spotifyObject.current_user_playing_track()
    if track != None:
        artist = track['item']['artists'][0]['name']
        track_name = track['item']['name']
        print("Currently playing " + artist + " - " + track_name)
        edit_html(track['item']['album']['images'][0]['url'], artist, track_name)
        print(str(current_track) + " " + track_name)
        if track_name != current_track:
            current_track = track_name

# Get the username from terminal
username = sys.argv[1]
scope = 'user-read-private user-read-playback-state user-modify-playback-state'

# user ID spotify:user:22uiuzjxpc7khi3pprxs2lqma

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

# Create our spotiyObject
spotifyObject = spotipy.Spotify(auth=token)

# get device information
devices = spotifyObject.devices()
deviceID = devices['devices'][0]['id']

threading.Thread(target=host_server).start()

get_current_track()

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
#             webbrowser.open(artist['images'][0]['url'])
#             time.sleep(3)
#             os.system("pkill -o chromium")
        
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
            r = requests.get(url = "http://localhost:8080/")
#                 edit_html(trackArt[int(songSelection)])
#                 webbrowser.open(trackArt[int(songSelection)])
#                 time.sleep(3)
#                 os.system("pkill -o chromium")
            
    # End the program
    if choice == "1":
        break
    
    # print(json.dumps(VARIABLE, sort_keys=True, indent=4))
