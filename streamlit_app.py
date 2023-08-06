import json
import requests
import streamlit as st
from annotated_text import annotated_text

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=80)

MUSICAL_NOTES = "\U0001F3B6"
st.set_page_config("Discover Music", page_icon=MUSICAL_NOTES)

def saveTo(filename, object):
    with open(filename, "w") as f:
        json.dump(object, f, indent=4)


CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

class Spotify:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()

    def get_access_token(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token_data = {
            "grant_type": "client_credentials"
        }

        url = f"https://accounts.spotify.com/api/token"
        response = requests.post(url, data=token_data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
        access_token = None
        if response.status_code == 200:
            object = response.json()
            pp.pprint(object)
            access_token = object['access_token']
            # TODO: keep track of time. 
            # each access_token expires in 1 hour (3600 seconds)
        else:
            print("status_code:", response.status_code)
            # TODO: throw exception?

        return access_token

    def send_request(self, url):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)

        object = {}

        if response.status_code == 200:
            object = response.json()
            pp.pprint(object)
        else:
            print("status_code:", response.status_code)
        return object

    def get_available_genre_seeds(self):
        url_available_genre_seeds = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
        response = self.send_request(url_available_genre_seeds)
        return response

    def get_recommendations(self, genre):
        url_recommendations_for_genres = f"https://api.spotify.com/v1/recommendations?seed_genres={genre}"
        response = self.send_request(url_recommendations_for_genres)
        return response


# todo
# 1. save access token in session state
# 2. check periodically to see if we need to refresh the access token

spotify = Spotify(CLIENT_ID, CLIENT_SECRET)

object = spotify.get_available_genre_seeds()

with st.sidebar:
    selection = st.radio("**Genres**:", object['genres'])

st.header(selection)

recommendations = spotify.get_recommendations(selection)


MEDIUM_QUALITY = 1

def show_tracks():
    for track in recommendations['tracks']:
        left_col, right_col = st.columns([2, 4])
        with left_col:
            st.image(track['album']['images'][MEDIUM_QUALITY]['url'], width=150)
        with right_col:
            annotated_text((track['name'], ""))
            annotated_text((track['artists'][0]['name'], "artist"))
            annotated_text((track['album']['release_date'], "release date"))
            if track['popularity'] > 0:
                annotated_text((str(track['popularity']), "popularity"))

            if track["preview_url"] is not None and len(track['preview_url']) > 0:
                st.markdown(f"[Preview]({track['preview_url']}) Track {track['track_number']}")
        st.divider()


def show_covers(tracks):
    for i in range(0, len(tracks), 3):
        covers = tracks[i: i + 3]
        cols = st.columns(3)

        for columnIndex, cover in enumerate(covers):
            with cols[columnIndex]:
                st.image(cover['album']['images'][MEDIUM_QUALITY]['url'], width=150)


left_tab, right_tab = st.tabs(["Tracks", "Covers"])

with left_tab:
    show_tracks()

with right_tab:
    show_covers(recommendations['tracks'])
