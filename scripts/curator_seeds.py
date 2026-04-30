import os
import json
import random
from curator_architect import create_m3u, load_vectors
from discord_reporter import send_discord_message
from datetime import datetime

def generate_seed_playlists():
    print("--- Generating Seed Playlists ---")
    vectors = load_vectors()
    
    # 1. By Era
    eras = {
        "The_50s_Hard_Bop_Era": (1950, 1959),
        "The_60s_Modal_Explorations": (1960, 1969),
        "The_70s_Jazz_Fusion_Vibe": (1970, 1979),
        "Modern_Jazz_Masters": (1990, 2026)
    }
    
    for name, (start, end) in eras.items():
        tracks = [v for v in vectors if v.get('year') and start <= int(str(v['year'])[:4]) <= end]
        if tracks:
            selected = random.sample(tracks, min(30, len(tracks)))
            path = create_m3u(name, selected)
            print(f"Created Era Playlist: {path}")

    # 2. By Common Labels (Fuzzy search in comments/paths)
    labels = ["Blue Note", "Prestige", "Impulse", "ECM", "Columbia"]
    for label in labels:
        tracks = [v for v in vectors if label.lower() in f"{v.get('label','')} {v.get('path','')}".lower()]
        if tracks:
            selected = random.sample(tracks, min(30, len(tracks)))
            path = create_m3u(f"Label_Focus_{label}", selected)
            print(f"Created Label Playlist: {path}")

    # 3. Artist Focus (Random high-count artist)
    artists = {}
    for v in vectors:
        a = v.get('artist')
        if a:
            artists[a] = artists.get(a, 0) + 1
    
    # Filter artists with >10 tracks
    prolific = [a for a, count in artists.items() if count > 10]
    if prolific:
        artist = random.choice(prolific)
        tracks = [v for v in vectors if v.get('artist') == artist]
        path = create_m3u(f"Essential_{artist.replace(' ', '_')}", tracks)
        print(f"Created Artist Focus: {path}")

    send_discord_message("🌱 **Seed Playlists Generated.** Foundation for the daily curator is ready.")

if __name__ == "__main__":
    generate_seed_playlists()
