import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Import our modules
from scout_local import get_local_taste_profile
from scout_metadata import get_album_personnel
from gatekeeper import evaluate_album
from curator_v3 import run_curator
from correspondent import generate_digest, save_to_silverbullet, send_digest_to_discord

load_dotenv()

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"processed_albums": []}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

async def main():
    print(f"--- Blue Note Automator Start: {datetime.now()} ---")
    
    # 1. Load History & Taste
    history = load_history()
    
    # 2. Run Discovery Mission (YTM Focus)
    print("Executing YTM Discovery Mission...")
    missions = run_curator()
    
    if not missions:
        print("No discovery missions generated.")
        return

    print(f"Processing {len(missions)} discovery missions...")
    
    approved_for_digest = []
    watchlist_for_digest = []
    
    # 3. Process each mission
    for mission in missions:
        album_id = f"{mission['album']}|{mission['new_artist']}"
        if album_id in history["processed_albums"]:
            continue
            
        print(f"\nAnalyzing Discovery: {mission['album']} by {mission['new_artist']}")
        
        # Format mission data for the Gatekeeper/Digest flow
        album_data = {
            "title": mission['album'],
            "artist": mission['new_artist'],
            "personnel": mission.get('personnel', []),
            "reasoning": mission.get('connection', 'Strategic discovery link.')
        }
        
        # These are pre-approved by the Curator's high-fidelity model
        approved_for_digest.append(album_data)
        history["processed_albums"].append(album_id)

    # 4. Generate & Save Digest
    if approved_for_digest:
        print("\nGenerating editorial digest for Discord...")
        # Note: generate_digest and correspondent logic is now YTM-link focused
        digest = generate_digest(approved_for_digest, [])
        send_digest_to_discord(digest)
        
    save_history(history)
    print(f"\n--- Blue Note Automator Finished: {datetime.now()} ---")

if __name__ == "__main__":
    asyncio.run(main())
