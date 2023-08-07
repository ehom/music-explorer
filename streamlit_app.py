import json
import requests
import streamlit as st
from annotated_text import annotated_text
import os

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=80)

MEDIUM_QUALITY = 1
MUSICAL_NOTES = "\U0001F3B6"
st.set_page_config("Discover Music", page_icon=MUSICAL_NOTES)


def saveTo(filename, object):
    with open(filename, "w") as f:
        json.dump(object, f, indent=4)


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


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

            # pp.pprint(object)
            print("got access token")

            access_token = object['access_token']
            # TODO: keep track of time.
            # each access_token expires in 1 hour (3600 seconds)
        else:
            print("status_code:", response.status_code)
            # TODO: throw exception?

        return access_token

    def send_request(self, url):
        # Check periodically to see if we need to refresh the access token
        # maybe we should have a get_access_token() method and at that time
        # check to make sure it hasn't expired.
        # if so, renew immediately.

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        response = requests.get(url, headers=headers)

        object = {}

        if response.status_code == 200:
            object = response.json()
            # pp.pprint(object)
            print("sent request...ok")
        else:
            print("status_code:", response.status_code)

        return object

    def get_available_genre_seeds(self):
        url_available_genre_seeds = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
        available_genre_seeds = self.send_request(url_available_genre_seeds)
        return available_genre_seeds

    def get_recommendations(self, genre):
        url_recommendations_for_genres = f"https://api.spotify.com/v1/recommendations?seed_genres={genre}"
        recommendations_for_genres = self.send_request(url_recommendations_for_genres)
        return recommendations_for_genres


def show_tracks(tracks):
    for track in tracks:
        left_col, right_col = st.columns([2, 4])
        with left_col:
            st.image(track['album']['images'][MEDIUM_QUALITY]['url'], width=150)
        with right_col:
            annotated_text((track['name'], " "))
            arr = []
            arr.append((track['artists'][0]['name'], "artist"))
            arr.append(" ")
            arr.append((track['album']['release_date'], "release date"))
            if track['popularity'] > 0:
                arr.append(" ")
                arr.append((str(track['popularity']), "popularity"))
            annotated_text(arr)

            # annotated_text((track['name'], ""))
            # annotated_text((track['artists'][0]['name'], "artist"))
            # annotated_text((track['album']['release_date'], "release date"))

            st.write("")

            if track["preview_url"] is not None and len(track['preview_url']) > 0:
                st.audio(track['preview_url'])
                annotated_text((f"Track {track['track_number']}", "preview"))
        st.divider()


def show_covers(tracks):
    BATCH_SIZE = 3
    for i in range(0, len(tracks), BATCH_SIZE):
        covers = tracks[i: i + BATCH_SIZE]
        cols = st.columns(BATCH_SIZE)

        for columnIndex, cover in enumerate(covers):
            with cols[columnIndex]:
                st.image(cover['album']['images'][MEDIUM_QUALITY]['url'], width=150)


def view():
    with st.sidebar:
        selection = st.radio("**Genres**:", st.session_state['genres'])

    if st.session_state['genre'] is None:
        st.session_state['genre'] = selection
    elif st.session_state['genre'] == selection:
        print("no change in genre. don't redraw")
    else:
        st.session_state['genre'] = selection

    recommendations = spotify.get_recommendations(selection)

    st.header(selection)

    left_tab, right_tab = st.tabs(["Tracks", "Covers"])

    with left_tab:
        show_tracks(recommendations['tracks'])

    with right_tab:
        show_covers(recommendations['tracks'])


def main():
    global spotify

    spotify = Spotify(CLIENT_ID, CLIENT_SECRET)

    if 'genres' not in st.session_state:
        object = spotify.get_available_genre_seeds()
        st.session_state['genres'] = object['genres']
        st.session_state['genre'] = None

    view()


if __name__ == "__main__":
    main()
