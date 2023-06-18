from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = os.getenv('SESSION_COOKIE_NAME')

@app.route('/')
def index():
    if 'token_info' not in session:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:
        return render_template('index.html')

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('index'))

@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(os.getenv('RAILWAY_DEPLOYMENT_URL', default='http://localhost:5000') + '/callback')

@app.route('/logged_in')
def logged_in():
    sp_oauth = create_spotify_oauth()
    token_info = get_token()
    if not token_info:
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return "You are logged in."

@app.route('/data')
def data():
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

    token_info = get_token()
    if not token_info:
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])

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

    return render_template('data.html', table=df.to_html())

def create_spotify_oauth():
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', default='http://localhost:5000/callback')
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=redirect_uri,
        scope="user-library-read"
    )

def get_token():
    token_info = session.get("token_info", None)
    if not token_info:
        return None

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv("PORT", default=5000))

