from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = os.getenv('SESSION_COOKIE_NAME')

# Spotify client credentials
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@app.route('/')
def index():
    playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]

    data = {
        "track_uri": [],
        "track_name": [],
        "artist_uri": [],
        "artist_name": [],
        "artist_popularity": [],
        "artist_genres": [],
        "album": [],
        "track_popularity": []
    }

    for track in sp.playlist_tracks(playlist_URI)["items"]:
        # URI
        data["track_uri"].append(track["track"]["uri"])

        # Track name
        data["track_name"].append(track["track"]["name"])

        # Main Artist
        artist_uri = track["track"]["artists"][0]["uri"]
        artist_info = sp.artist(artist_uri)

        # Name, popularity, genre
        data["artist_uri"].append(artist_uri)
        data["artist_name"].append(track["track"]["artists"][0]["name"])
        data["artist_popularity"].append(artist_info["popularity"])
        data["artist_genres"].append(artist_info["genres"])

        # Album
        data["album"].append(track["track"]["album"]["name"])

        # Popularity of the track
        data["track_popularity"].append(track["track"]["popularity"])

    df = pd.DataFrame(data)

    return render_template('index.html', table=df.to_html())

# Rest of the code...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv("PORT", default=5000))
