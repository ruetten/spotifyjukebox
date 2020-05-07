import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
from time import sleep
import threading
## WBESERVER
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import requests
## LEDS
import board
import neopixel
import time
# LYRICS
import lyricsgenius

# sem = threading.Semaphore()
# kill_threads = False

default_image = "https://yt3.ggpht.com/-oSs8fntDxuw/AAAAAAAAAAI/AAAAAAAAAAA/17pzJmg8Gds/s900-c-k-no-mo-rj-c0xffffff/photo.jpg"
current_track = None # just the track name; used to update display

get_lyrics = False

"""
export SPOTIPY_CLIENT_ID='524a3c5def4d4cb08a4b98c48458543d'
export SPOTIPY_CLIENT_SECRET='5a4424bde8664bffbc2f8d55658f98f6'
export SPOTIPY_REDIRECT_URI='http://google.com/'
sudo python3 jukebox.py 22uiuzjxpc7khi3pprxs2lqma
spotify:track:0rQtoQXQfwpDW0c7Fw1NeM
"""

############ WEBSERVER ############
port = 8080
auto_refresh = 1

disp = "/disp.html"
qup = "/qup.html"
lyrics = "/lyrics.html"

class Serv(SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if auto_refresh > 0:
            sleep(0.1)
        get_current_track()
        if self.path == '/':
            self.path = qup
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

    def do_POST(self):
        content_length = int(self.headers['Content-length']) # get amount of data
        post_data = self.rfile.read(content_length) # get the data
        post_data = post_data.decode('unicode_escape')
        post_data = post_data[post_data.find('=')+1:]
        print(post_data)
        q_up_track(post_data)
        self._set_response()
        self.wfile.write("Your song should play shortly!".format(self.path).encode('utf-8'))

def host_server():
    httpd = HTTPServer(('', port), Serv)
    # httpd = socketserver.TCPServer(("", port), Serv)
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        httpd.handle_request()
    print("closing server")
    httpd.server_close()

def q_up_track(track_uri):
    print(track_uri)
    start = track_uri.find('%2Ftrack%2F') + len('%2Ftrack%2F') #/
    end = track_uri.find('%3F') #?
    track_uri = track_uri[start:end]
    print(track_uri)
    spotifyObject.add_to_queue(track_uri, device_id=get_device())
#     spotifyObject.next_track()

def edit_html(image_url, artist, track):
    f = open(disp[1:], 'w')
    f.write("<!DOCTYPE html><html><head><title>Spotify Jukebox</title><meta charset=\"UTF-8\"></head>")
#     f.write("<body style=>")
#     f.write("<body style=\"\">")
    f.write("<body style=text-align:center;font-family:courier;background-color:grey>")#1DB954>")
    f.write("<br><br><br>")
    f.write("<h1>" + artist + " - " + track + "</h1><img style=\"width:800px;height:800px;\" src=\"")
    f.write(image_url)
    f.write("\">")
    f.write("<h5>\"SPOTIFY JUKEBOX\" BY RUETTEN<h5></body></html>")
    f.close()
    if auto_refresh == 1 and track != current_track:
        os.system("pkill -o chromium")
        sleep(1)
    elif auto_refresh == 2 and track != current_track:
#         webbrowser.open("http://localhost:8080/")
        os.system("bash refresh")

def get_current_track():
    # current track playing
    global current_track
    track = spotifyObject.current_user_playing_track()
    if track != None:
        artist = track['item']['artists'][0]['name']
        track_name = track['item']['name']
        print("Currently playing " + artist + " - " + track_name)
        edit_html(track['item']['album']['images'][0]['url'], artist, track_name)
        #print(song_lyrics(track_name, artist))
        if get_lyrics:
            edit_lyrics_html(track['item']['album']['images'][0]['url'], artist, track_name)
#         print(str(current_track) + " " + track_name)
        if track_name != current_track:
            current_track = track_name

def refresh_regulary():
    global current_track
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        track = spotifyObject.current_user_playing_track()
        if track != None:
            track_name = track['item']['name']
            if track_name != current_track:
#                 print(json.dumps(track, sort_keys=True, indent=4))
                current_track = track_name
                os.system("bash refresh")
        sleep(auto_refresh) #the refresh rate for how often to check if new song playing 

############ LED SETUP ############
num_pixels = 300
pixels = neopixel.NeoPixel(board.D18, num_pixels)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

def rainbow_cycle(wait, j):
    for i in range(num_pixels):
        pixel_index = (i * 256 // num_pixels) + j*100
        pixels[i] = wheel(pixel_index & 255)
    pixels.show()
    time.sleep(wait)

def update_LED_dance():
    global kill_threads
    j = 0
    track_uri = None
    tempo = 60
    energy = 0.5
    correction = 0
    track = spotifyObject.current_user_playing_track()
    current_dance = track
    features = None
    if track != None:
        track_uri = track['item']['uri']
        #audio = spotifyObject.audio_analysis(track['item']['uri'])
        #print(json.dumps(track, sort_keys=True, indent=4))
        #tempo = audio['track']['tempo']
        features = spotifyObject.audio_features(track['item']['uri'])
        print(json.dumps(features, sort_keys=True, indent=4))
        tempo = features[0]['tempo']
        energy = features[0]['energy']
        danceability = features[0]['danceability']
        
    t = threading.currentThread()
    while getattr(t, "do_run", True):        
        track = spotifyObject.current_user_playing_track()
        if track != None:
            is_playing = str(track['actions']['disallows']).find('resuming') != -1
            if is_playing:
                track_uri = track['item']['uri']
                if track_uri != current_dance:
                    j=0
                    current_dance = track_uri
                    features = spotifyObject.audio_features(track['item']['uri'])
                    tempo = features[0]['tempo']
                    energy = features[0]['energy']
                    danceability = features[0]['danceability']
                    print(json.dumps(features, sort_keys=True, indent=4))
                    print(track['item']['name'] + " " + str(tempo))
                if danceability >= 0.6 or energy >= 0.6:
                    pixels.fill((255, 0, 0))
                    pixels.show()
                    time.sleep(60.0/(tempo+correction))
                    pixels.fill((0, 255, 0))
                    pixels.show()
                    time.sleep(60.0/(tempo+correction))
                    pixels.fill((0, 0, 255))
                    pixels.show()
                    time.sleep(60.0/(tempo+correction))
                else:
                    rainbow_cycle(1/(tempo+correction), j)
                    j = (j+1)%255
            else:
                pixels.fill((0, 0, 0))
                pixels.show()
        else:
            pixels.fill((0, 0, 0))
            pixels.show()

########## GENIUS LYRICS ###########

genius = lyricsgenius.Genius("F-6z9zjNCL_wF_mFpLCGd9y3aF1katSAs_oDEP-NKrCjvrBvjFt2GJE8nFqynMl6")

def song_lyrics(song_name, artist_name):
    artist = genius.search_artist(artist_name, max_songs=1)
    song = genius.search_song(song_name, artist.name)
    return song.lyrics

def edit_lyrics_html(image_url, artist, track):
    global lyrics
    f = open(lyrics[1:], 'w')
    f.write("<!DOCTYPE html><html><head><title>Spotify Jukebox</title><meta charset=\"UTF-8\">")
    f.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    f.write("<style>*{box-sizing: border-box;}.column {float: left;width: 50%;padding: 10px;height: 300px;}")
    f.write(".row:after { content: "";display: table; clear: both;}</style></head>")
    f.write("<body style=text-align:center;font-family:courier;background-color:#1DB954>")#1DB954>")
    lyrics_str = song_lyrics(track, artist)
    f.write("<div class=\"row\">")
    f.write("<div class=\"column\">")
    f.write("<br><br><br>")
    f.write("<h1>" + artist + " - " + track + "</h1>")
    f.write("<img style=\"width:800px;height:800px;\" src=\"")
    f.write(image_url)
    f.write("\">")
    f.write("<h6>\"SPOTIFY JUKEBOX\" BY RUETTEN<h6></body></html>")
    f.write("</div>")
    f.write("<div class=\"column\">")
    f.write("<h6>" + lyrics_str.replace("\n", "<br/>") + "</h6>")
    f.write("</div>")
    f.write("</div>")
    f.close()

############ MAIN PROG #############
serve_thr = None
refrsh_thr = None
led_thr = None
spotifyObject = None

# get device information
def get_device():
    global spotifyObject
    devices = spotifyObject.devices()
    deviceID = devices['devices'][0]['id']
    return deviceID

def main():
    global spotifyObject
    global serve_thr
    global refrsh_thr
    global led_thr
    # Get the username from terminal
    username = sys.argv[1]
    scope = 'user-read-private user-read-playback-state user-modify-playback-state'

    # user ID spotify:user:22uiuzjxpc7khi3pprxs2lqma

    # Erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(username, scope,
                               client_id='524a3c5def4d4cb08a4b98c48458543d',
                               client_secret='5a4424bde8664bffbc2f8d55658f98f6',
                               redirect_uri='http://google.com/')
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope,
                               client_id='524a3c5def4d4cb08a4b98c48458543d',
                               client_secret='5a4424bde8664bffbc2f8d55658f98f6',
                               redirect_uri='http://google.com/')

    # Create our spotiyObject
    spotifyObject = spotipy.Spotify(auth=token)

    deviceID = get_device()

    # webbrowser.open("http://localhost:" + str(port) + "/disp.html")

    serve_thr = threading.Thread(target=host_server)
    serve_thr.start()
    refrsh_thr = threading.Thread(target=refresh_regulary)
    refrsh_thr.start()
    led_thr = threading.Thread(target=update_LED_dance)
    led_thr.start()

    get_current_track()

    # user info
    user = spotifyObject.current_user()

    displayName = user['display_name']
    followers = user['followers']['total']
    
    #Debug code for token expiring
#     sleep(600)
#     raise spotipy.exceptions.SpotifyException(None, None, "manual")

    while True:
        print()
        print("WELCOME TO THE SPOTIFY JUKEBOX " + displayName)
        
        choice = input("")

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
    #             spotifyObject.start_playback(deviceID, None, trackSelectionList)
                spotifyObject.add_to_queue(trackURIs[int(songSelection)], device_id=deviceID)
                spotifyObject.next_track()
                #if auto_refresh > 0:
                    #r = requests.get(url = "http://localhost:" + port + "/")
    #                 edit_html(trackArt[int(songSelection)])
    #                 webbrowser.open(trackArt[int(songSelection)])
    #                 time.sleep(3)
    #                 os.system("pkill -o chromium")

        # End the program
        if choice == "1":
            print("exiting")
            break
    return

        # print(json.dumps(VARIABLE, sort_keys=True, indent=4))

try:
    main()
except:
    print("Token expired, program restarting")
serve_thr.do_run = False
refrsh_thr.do_run = False
led_thr.do_run = False
refrsh_thr.join()
print("refresh joined")
led_thr.join()
print("LED joined")
serve_thr.join()
print("server joined")

    
"""ERROR:spotipy.client:HTTP Error for GET to https://api.spotify.com/v1/me/player/currently-playing returned 401 due to The access token expired
Exception in thread Thread-3:
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 170, in _internal_call
    response.raise_for_status()
  File "/usr/lib/python3/dist-packages/requests/models.py", line 940, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://api.spotify.com/v1/me/player/currently-playing

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "jukebox.py", line 183, in update_LED_dance
    track = spotifyObject.current_user_playing_track()
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 836, in current_user_playing_track
    return self._get("me/player/currently-playing")
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 205, in _get
    return self._internal_call("GET", url, payload, kwargs)
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 185, in _internal_call
    headers=response.headers,
spotipy.exceptions.SpotifyException: http status: 401, code:-1 - https://api.spotify.com/v1/me/player/currently-playing:
 The access token expired

ERROR:spotipy.client:HTTP Error for GET to https://api.spotify.com/v1/me/player/currently-playing returned 401 due to The access token expired
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 170, in _internal_call
    response.raise_for_status()
  File "/usr/lib/python3/dist-packages/requests/models.py", line 940, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://api.spotify.com/v1/me/player/currently-playing

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3.7/threading.py", line 917, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.7/threading.py", line 865, in run
    self._target(*self._args, **self._kwargs)
  File "jukebox.py", line 125, in refresh_regulary
    track = spotifyObject.current_user_playing_track()
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 836, in current_user_playing_track
    return self._get("me/player/currently-playing")
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 205, in _get
    return self._internal_call("GET", url, payload, kwargs)
  File "/usr/local/lib/python3.7/dist-packages/spotipy/client.py", line 185, in _internal_call
    headers=response.headers,
spotipy.exceptions.SpotifyException: http status: 401, code:-1 - https://api.spotify.com/v1/me/player/currently-playing:
 The access token expired

"""