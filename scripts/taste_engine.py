import os
import json
import pylast
from dotenv import load_dotenv
from ytmusicapi import YTMusic

load_dotenv(dotenv_path="/home/ownash/blue-note-automator/.env")

# The new persistent OAuth file
OAUTH_PATH = "/home/ownash/blue-note-automator/oauth.json"
API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")
LASTFM_USER = os.getenv("LASTFM_USER") or os.getenv("LASTFM_USERNAME")

def get_ytm_client():
    if not os.path.exists(OAUTH_PATH):
        return None
    try:
        return YTMusic(OAUTH_PATH)
    except: return None

def is_jazz_expert(network, artist_name):
    try:
        artist = network.get_artist(artist_name)
        top_tags = [t.item.get_name().lower() for t in artist.get_top_tags(limit=5)]
        jazz_keywords = ['jazz', 'fusion', 'bebop', 'hard bop', 'free jazz', 'contemporary jazz', 'post-bop', 'swing']
        for tag in top_tags:
            if any(kw in tag for kw in jazz_keywords):
                if 'hip-hop' in top_tags or 'rap' in top_tags:
                    return top_tags[0] == 'jazz'
                return True
        return False
    except: return False

def get_hybrid_taste_profile():
    raw_artists = set()
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    
    # 1. Fetch YTM History
    ytm = get_ytm_client()
    if ytm:
        try:
            print("Fetching YTM History (OAuth)...")
            history = ytm.get_history()
            for item in history[:100]:
                for artist in item.get('artists', []):
                    raw_artists.add(artist['name'])
            print(f"Found {len(raw_artists)} artists in YTM History.")
        except Exception as e:
            print(f"YTM History Error: {e}")

    # 2. Fetch Last.fm
    if LASTFM_USER:
        try:
            print("Fetching Last.fm Data...")
            user = network.get_user(LASTFM_USER)
            raw_artists.update([a.item.name for a in user.get_top_artists(period=pylast.PERIOD_1MONTH, limit=50)])
            raw_artists.update([a.item.name for a in user.get_top_artists(limit=50)])
        except Exception as e:
            print(f"Last.fm Error: {e}")

    # 3. Filter for JAZZ ONLY
    jazz_artists = []
    print(f"Filtering {len(raw_artists)} total artists for jazz purity...")
    for artist in raw_artists:
        if is_jazz_expert(network, artist):
            jazz_artists.append(artist)
            
    return sorted(list(set(jazz_artists)))

if __name__ == "__main__":
    profile = get_hybrid_taste_profile()
    print(f"Final Jazz Profile: {len(profile)} artists.")
    print(f"Samples: {profile[:15]}")
