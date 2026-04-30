import os
import json
import musicbrainzngs
from mutagen.oggopus import OggOpus
from dotenv import load_dotenv

load_dotenv()

# Set a proper user agent for MusicBrainz
musicbrainzngs.set_useragent("BlueNoteAutomator", "0.2", "https://github.com/ownash")

MUSIC_ROOT = os.getenv("MUSIC_PATH", "/opt/selfhosted/media/music")

def fetch_mb_data(artist_name, album_name):
    """
    Fetches label and personnel from MusicBrainz.
    """
    try:
        # Search for the release
        result = musicbrainzngs.search_releases(artist=artist_name, release=album_name, limit=1)
        
        if not result['release-list']:
            return None, None
        
        release = result['release-list'][0]
        release_id = release['id']
        label = release.get('label-info-list', [{}])[0].get('label', {}).get('name', 'Unknown Label')
        
        # Get detailed release info including artist relations (personnel)
        full_release = musicbrainzngs.get_release_by_id(release_id, includes=["artist-rels"])
        
        personnel = []
        if 'artist-relation-list' in full_release['release']:
            for rel in full_release['release']['artist-relation-list']:
                name = rel['artist']['name']
                role = rel.get('type', 'performer')
                personnel.append(f"{name} ({role})")
        
        return label, ", ".join(personnel)
        
    except Exception as e:
        print(f"Error fetching MB data for {artist_name} - {album_name}: {e}")
        return None, None

def enrich_file(file_path):
    """
    Writes label and personnel tags to an Opus file.
    """
    try:
        audio = OggOpus(file_path)
        
        # Get current tags to help MB search
        artist = audio.get("artist", [""])[0]
        album = audio.get("album", [""])[0]
        
        if not artist or not album:
            return
            
        # Check if already enriched (optional: we can skip or overwrite)
        if "label" in audio and "personnel" in audio:
            return

        label, personnel = fetch_mb_data(artist, album)
        
        if label:
            audio["label"] = label
        if personnel:
            audio["personnel"] = personnel
            
        audio.save()
        print(f"Enriched: {artist} - {album}")
        
    except Exception as e:
        print(f"Error enriching {file_path}: {e}")

def run_enrichment():
    print("--- Starting Metadata Enrichment ---")
    for root, _, files in os.walk(MUSIC_ROOT):
        for file in files:
            if file.lower().endswith(".opus"):
                enrich_file(os.path.join(root, file))
    print("--- Metadata Enrichment Finished ---")

if __name__ == "__main__":
    run_enrichment()
