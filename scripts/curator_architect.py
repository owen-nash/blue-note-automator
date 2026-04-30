import os
import json
import random
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from discord_reporter import send_discord_message
from ytmusicapi import YTMusic

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-3.1-8b-instruct" 
VECTOR_DB_PATH = "library_vectors.json"
YTM_HEADERS_PATH = "/home/ownash/ytmusic_headers.json"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# YTM Setup
def get_ytm_client():
    if not os.path.exists(YTM_HEADERS_PATH):
        return None
    try:
        with open(YTM_HEADERS_PATH) as f:
            headers = json.load(f)
        session = requests.Session()
        session.headers.update(headers)
        return YTMusic(requests_session=session)
    except Exception as e:
        print(f"ERROR initializing YTMusic: {e}")
        return None

ytm = get_ytm_client()

def load_vectors():
    with open(VECTOR_DB_PATH, "r") as f:
        return json.load(f)

def get_curatorial_intent(library_summary):
    prompt = f"""
    You are a legendary Jazz Radio DJ and Curator. Your library consists of:
    {library_summary}
    
    Come up with a creative, specific theme for a 2-hour jazz playlist. 
    It should be sophisticated. Examples: "The Blue Note Bop of 1963", "Modern Electric Guitar Explorations", "The Soul of the Jazz Trio".
    
    Return a JSON object:
    {{
        "theme": "The Title",
        "description": "A poetic 2-3 sentence description of the vibe.",
        "search_keywords": ["keyword1", "keyword2", "artist_hint"],
        "logic": "Briefly explain the musical logic (e.g., 'Focus on tracks with John Scofield and Bill Stewart')"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/ownash/blue-note-automator",
                "X-Title": "Blue Note Curator",
            },
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error getting intent: {e}")
        return {"theme": "Daily Jazz Discovery", "description": "A fresh mix of your library.", "search_keywords": ["Jazz"], "logic": "Random selection"}

def select_tracks(intent, vectors):
    candidates = []
    keywords = [k.lower() for k in intent.get('search_keywords', [])]
    
    for v in vectors:
        text = f"{v.get('artist','')} {v.get('album','')} {v.get('genre','')}".lower()
        if any(k in text for k in keywords):
            candidates.append(v)
    
    if len(candidates) < 20:
        candidates.extend(random.sample(vectors, min(20, len(vectors))))
        
    selected = random.sample(candidates, min(25, len(candidates)))
    return selected

def create_ytm_playlist(theme, description, tracks):
    """
    Creates a playlist on YouTube Music and adds the selected tracks.
    """
    if not ytm:
        return None
    
    try:
        # Create the playlist
        playlist_id = ytm.create_playlist(theme, description)
        print(f"Created YTM Playlist: {theme} ({playlist_id})")
        
        video_ids = []
        for t in tracks:
            query = f"{t['artist']} {t['title']} {t['album']}"
            search_results = ytm.search(query, filter="songs")
            if search_results:
                video_ids.append(search_results[0]['videoId'])
                print(f"Found on YTM: {t['artist']} - {t['title']}")
        
        if video_ids:
            ytm.add_playlist_items(playlist_id, video_ids)
            print(f"Added {len(video_ids)} tracks to playlist.")
            return f"https://music.youtube.com/playlist?list={playlist_id}"
        return None
    except Exception as e:
        print(f"Error creating YTM playlist: {e}")
        return None

def generate_playlist_report(intent, tracks):
    track_list = "\n".join([f"- {t['artist']} - {t['title']} ({t['album']})" for t in tracks[:10]])
    
    prompt = f"""
    You created a jazz playlist themed: "{intent['theme']}"
    Description: {intent['description']}
    
    Here are some of the tracks:
    {track_list}
    
    Write an in-depth breakdown for a Discord message. 
    Include:
    1. **Why this theme?** (Musical context)
    2. **Personnel Highlights** (Mention interesting musicians on these tracks)
    3. **The Listening Experience** (What to listen for)
    
    Keep it flavorful but concise (Markdown supported).
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"New Playlist Created: **{intent['theme']}**\n{intent['description']}"

def run_curator():
    print("--- Curator Architect Starting (YTM Mode) ---")
    vectors = load_vectors()
    
    sample_artists = list(set([v.get('artist') for v in random.sample(vectors, 100) if v.get('artist')]))
    library_summary = f"A collection of {len(vectors)} tracks featuring artists like: {', '.join(sample_artists[:30])}"
    
    intent = get_curatorial_intent(library_summary)
    print(f"Theme: {intent['theme']}")
    
    tracks = select_tracks(intent, vectors)
    print(f"Selected {len(tracks)} tracks.")
    
    playlist_url = create_ytm_playlist(intent['theme'], intent['description'], tracks)
    
    report = generate_playlist_report(intent, tracks)
    
    embed = {
        "title": f"🎼 Today's Playlist: {intent['theme']}",
        "description": report,
        "color": 3447003, 
        "fields": [
            {"name": "Vibe", "value": intent['description'], "inline": False},
            {"name": "Logic", "value": intent['logic'], "inline": False}
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    if playlist_url:
        embed["url"] = playlist_url
        embed["fields"].append({"name": "🎧 Listen Now", "value": f"[Open in YouTube Music]({playlist_url})", "inline": False})
    
    send_discord_message(embeds=[embed])
    print("--- Curator Architect Finished ---")

if __name__ == "__main__":
    run_curator()
