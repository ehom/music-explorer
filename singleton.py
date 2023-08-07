import requests
import time
from config import CLIENT_ID, CLIENT_SECRET


class URLs:
    GET_ACCESS_TOKEN = f"https://accounts.spotify.com/api/token"
    AVAILABLE_GENRE_SEEDS = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    RECOMMENDATIONS_FOR_GENRES = "https://api.spotify.com/v1/recommendations?seed_genres={0}"


class Spotify:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_timestamp = None
        self.access_token = self.get_access_token()

    def get_access_token(self):
        ONE_HOUR_IN_SECS = 3600
        HALF_HOUR_IN_SECS = 1800
        EXPIRATION = HALF_HOUR_IN_SECS

        if self.access_token_timestamp is not None:
            current_epoch_time = int (time.time())
            diff_seconds = current_epoch_time - self.access_token_timestamp
            print("diff seconds:", diff_seconds)

            if diff_seconds < EXPIRATION:
                print("Use CURRENT access token")
                return self.access_token 

        print("Request NEW access token")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token_data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(URLs.GET_ACCESS_TOKEN, data=token_data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
        if response.status_code == 200:
            self.access_token_timestamp = int (time.time())
            object = response.json()

            print("Received NEW access token")

            access_token = object['access_token']
        else:
            print("status_code:", response.status_code)
            # TODO: throw exception?

        return access_token

    def send_request(self, url):
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
        }
        response = requests.get(url, headers=headers)

        object = {}

        if response.status_code == 200:
            object = response.json()
            print("Received response ... ok")
        else:
            print("status_code:", response.status_code)

        return object

    def get_available_genre_seeds(self):
        available_genre_seeds = self.send_request(URLs.AVAILABLE_GENRE_SEEDS)
        return available_genre_seeds

    def get_recommendations(self, genre):
        recommendations_for_genres = self.send_request(URLs.RECOMMENDATIONS_FOR_GENRES.format(genre))
        return recommendations_for_genres


spotify = Spotify(CLIENT_ID, CLIENT_SECRET)
