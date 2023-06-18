from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
    return render_template('index.html')

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('logged_in'))

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