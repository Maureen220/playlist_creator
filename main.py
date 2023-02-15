from pprint import pprint

import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from config import client_id, client_secret
from datetime import datetime

travel_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
date_converted = datetime.strptime(travel_date, '%Y-%m-%d')
year = date_converted.year

billboard_url = f"https://www.billboard.com/charts/hot-100/{travel_date}/"

response = requests.get(billboard_url)
soup = BeautifulSoup(response.text, "html.parser")

# The top song is a separate html tag
number_one = soup.find("a", href="#", class_="c-title__link lrv-a-unstyle-link")
number_one_text = number_one.getText()
number_one_cleaned = number_one_text.strip("\n\t")

# The rest of the top 100 are found here
ninety_nine_list = []
for titles in soup.find_all("h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 "
                                         "lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 "
                                         "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 "
                                         "u-max-width-230@tablet-only", id="title-of-a-story"):
    text_of_titles = titles.getText()
    ninety_nine_list.append(titles.getText())

cleaned_ninety_nine_list = [s.strip("\n\t") for s in ninety_nine_list]

final_list = [number_one_cleaned] + cleaned_ninety_nine_list

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private playlist-read-private",
                                               show_dialog=True,
                                               cache_path="token.txt"))

song_uris = []
for track in final_list:
    result = sp.search(q=f"track:{track} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{track} doesn't exist in spotify. Skipped")

results = sp.current_user()
user_id = results['id']

my_playlist = sp.user_playlist_create(user=f"{user_id}", name=f"{year} Billboard Top Tracks", public=False,
                                      collaborative=False, description="Creating Top Tracks Playlist with Python")

sp.playlist_add_items(playlist_id=my_playlist["id"], items=song_uris)
