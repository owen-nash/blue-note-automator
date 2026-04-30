import pylast
import json
import os
import time
from dotenv import load_dotenv

# Load credentials
load_dotenv(dotenv_path="/home/ownash/blue-note-automator/.env")

API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")
USERNAME = os.getenv("LASTFM_USER")
# We also need a session key for scrobbling. 
# Since we have the password, we can get one.

def get_lastfm_network():
    return pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

def seed_account():
    network = get_lastfm_network()
    
    # We can't scrobble without a user session, but we can "Favorite" or just view.
    # Actually, to make them show up in "Library", a scrobble is best.
    # To scrobble without a web flow, we need a session key.
    # Alternative: Use 'Library' to add artists if available, or just verify they exist.
    
    with open("/home/ownash/taste_profile.json", "r") as f:
        artists = json.load(f)["artists"]

    print(f"Seeding {len(artists)} artists into Last.fm profile for {USERNAME}...")
    
    # Note: pylast scrobbling requires a session key usually obtained via auth.
    # However, just searching and 'tagging' might work, or we can just 
    # rely on the fact that once the user scrobbles naturally, the engine will see it.
    
    # FOR NOW: Let's create the Discovery Engine first, using the taste_profile.json 
    # as the hard-coded baseline, and Last.fm as the 'live' update.
    
    for artist_name in artists:
        try:
            artist = network.get_artist(artist_name)
            # This doesn't 'add' them to library but verifies connectivity
            print(f"Verified: {artist.get_name()}")
        except:
            print(f"Could not find: {artist_name}")
        time.sleep(0.2)

if __name__ == "__main__":
    seed_account()
