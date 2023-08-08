import streamlit as st
from annotated_text import annotated_text
from singleton import spotify

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=80)

MEDIUM_QUALITY = 1
MUSICAL_NOTES = "\U0001F3B6"
EMOJIS_BOMB = "\U0001F4A3"

def show_spotify_logo():
    SPOTIFY_FULL_LOGO_URL = "https://developer.spotify.com/images/guidelines/design/logos.svg"
    LOGO_URL = "https://developer.spotify.com/images/guidelines/design/icon4@2x.png"

    st.image(LOGO_URL, width=70)


def show_tracks(tracks):
    for track in tracks:
        # check if track is worth showing
        # TODO put this track validation code in a
        # separate function

        if len(track['name']) == 0:
            print("no track name")
            continue

        images = track['album']['images']
        count = len(images)

        if count == 0:
            print("no cover art")
            continue

        image_index = MEDIUM_QUALITY if count >= 2 else 0

        left_col, right_col = st.columns([2, 4])

        with left_col:
            st.image(track['album']['images'][image_index]['url'], width=150)

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

            st.write("")

            if track["preview_url"] is not None and len(track['preview_url']) > 0:
                st.audio(track['preview_url'])
                annotated_text((f"Track {track['track_number']}", "preview"))
        st.divider()


def show_covers(tracks):
    BATCH_SIZE = 4
    for i in range(0, len(tracks), BATCH_SIZE):
        covers = tracks[i: i + BATCH_SIZE]
        cols = st.columns(BATCH_SIZE)

        for columnIndex, cover in enumerate(covers):
            with cols[columnIndex]:
                # check for image first
                images = cover['album']['images']
                count = len(images)
                if count == 0:
                    print("no cover art!!!")
                else:
                    image_index = MEDIUM_QUALITY if count >= 2 else 0
                    st.image(cover['album']['images'][image_index]['url'], width=150)


def view():
    with st.sidebar:
        selection = st.radio("**Genres**:", st.session_state['genres'])

        st.divider()
        show_spotify_logo()

    if st.session_state['genre'] is None:
        st.session_state['genre'] = selection
    elif st.session_state['genre'] != selection:
        st.session_state['genre'] = selection
    else:
       pass

    recommendations = spotify.get_recommendations(selection)

    st.header(selection)

    left_tab, right_tab = st.tabs(["Tracks", "Covers"])

    with left_tab:
        if 'tracks' in recommendations:
            show_tracks(recommendations['tracks'])
        else:
            print("can't find tracks in recommendation")

    with right_tab:
        if 'tracks' in recommendations:
            show_covers(recommendations['tracks'])
        else:
            print("can't find tracks in recommendation")
        st.divider()

    show_spotify_logo()


def main():
    st.set_page_config("Discover Music", page_icon=MUSICAL_NOTES,
                       menu_items={
                           "About": "(To be added)"
                       })

    if 'genres' not in st.session_state:
        st.session_state['genres'] = []
        st.session_state['genre'] = None

        results = spotify.get_available_genre_seeds()
        if 'genres' in results:
            st.session_state['genres'] = results['genres']
        else:
            st.error("Could not get available genres", icon=EMOJIS_BOMB)

    print("draw page")

    view()


if __name__ == "__main__":
    main()
