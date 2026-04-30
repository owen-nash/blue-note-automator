import os
import json

MUSIC_ROOT = "/opt/selfhosted/media/music"
OUTPUT_FILE = "/home/ownash/blue-note-automator/migration_queue.json"

def get_artists():
    if not os.path.exists(MUSIC_ROOT):
        print(f"Error: {MUSIC_ROOT} not found.")
        return []

    # Get all first-level directories
    artists = [d for d in os.listdir(MUSIC_ROOT) if os.path.isdir(os.path.join(MUSIC_ROOT, d))]
    
    # Clean up names (remove trailing slashes, though listdir doesn't have them)
    artists = [a.strip() for a in artists]
    
    # Sort for consistency
    artists.sort()
    
    return artists

if __name__ == "__main__":
    print(f"Scanning {MUSIC_ROOT} for artists...")
    artist_list = get_artists()
    
    # Create the queue with status tracking
    queue = {
        "total_count": len(artist_list),
        "migration_date": str(os.uname().nodename), # or date
        "artists": [
            {"name": artist, "ytm_status": "pending", "presto_status": "pending"} 
            for artist in artist_list
        ]
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully extracted {len(artist_list)} artists to {OUTPUT_FILE}")
