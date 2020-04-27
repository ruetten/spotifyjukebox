import requests
import json

URL = "https://api.spotify.com/v1/audio-analysis/spotify:track:0rQtoQXQfwpDW0c7Fw1NeM"

r = requests.get(url = URL) 
  
# extracting data in json format 
data = r.json() 
print(json.dumps(data, sort_keys=True, indent=4))