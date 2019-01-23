#!/usr/bin/python3
import random, os
from spotipy import Spotify
from spotipy.util import prompt_for_user_token
from flask import Flask, request

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

client_secret = os.environ.get('CLIENT_SECRET')
client_id = os.environ.get('CLIENT_ID')
redirect_uri = os.environ.get('REDIRECT_URL')
username = os.environ.get('USERNAME')

scope = ('user-library-read '
         'playlist-read-private '
         'user-read-private '
         'user-read-playback-state '
         'user-modify-playback-state')

app = Flask(__name__)


def get_spotify_api_instance():
    token = prompt_for_user_token(
        username,
        scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )

    return Spotify(auth=token)


@app.route('/spotify/playlist/', methods=['GET'])
def playlist_start():
    playlist_name = request.args.get('playlist_name')
    device_name = request.args.get('device_name')
    shuffle = int(request.args.get('shuffle', 0))

    sp = get_spotify_api_instance()
    device = next(
        device
        for device in sp.devices()['devices']
        if device['name'] == device_name
    )

    playlist = next(
        playlist
        for playlist in sp.user_playlists(username)['items']
        if playlist['name'] == playlist_name
    )
    tracks = sp.user_playlist_tracks(username, playlist_id=playlist['id'])['items']
    track_uris = [track['track']['uri'] for track in tracks]
    if shuffle:
        random.shuffle(track_uris)

    sp.pause_playback(device_id=device['id'])
    sp.start_playback(device_id=device['id'], uris=track_uris)

    return "Playlist '{}' successfully started on '{}'.".format(playlist_name, device_name)


@app.route('/spotify/pause/', methods=['GET'])
def playlist_pause():
    device_name = request.args.get('device_name')

    sp = get_spotify_api_instance()
    device = next(
        device
        for device in sp.devices()['devices']
        if device['name'] == device_name
    )
    sp.pause_playback(device_id=device['id'])

    return "Playback on '{}' successfully paused.".format(device_name)


if __name__ == '__main__':
    app.run(host="localhost", port=8080)






