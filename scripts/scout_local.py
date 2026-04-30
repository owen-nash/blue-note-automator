import os
from pathlib import Path

def get_local_taste_profile(music_path):
    """
    Scans the local music directory and returns a list of unique artists.
    This serves as the 'Taste Profile' anchor.
    """
    if not os.path.exists(music_path):
        print(f"Error: Music path {music_path} does not exist.")
        return []
    
    # We assume the structure is Artist/Album/Tracks
    # So we list the first level of directories
    artists = [f.name for f in Path(music_path).iterdir() if f.is_dir()]
    return sorted(artists)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    music_path = os.getenv("MUSIC_PATH", "/opt/selfhosted/media/music")
    artists = get_local_taste_profile(music_path)
    print(f"Detected {len(artists)} artists in local library.")
    print(f"Sample: {artists[:10]}")
