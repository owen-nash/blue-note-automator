import os
import json
import librosa
import numpy as np
from pathlib import Path
from tinytag import TinyTag
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/ownash/blue-note-automator/.env")
MUSIC_PATH = os.getenv("MUSIC_PATH", "/opt/selfhosted/media/music")
INSIGHT_FILE = "/home/ownash/blue-note-automator/library_insight.json"

def analyze_audio(file_path):
    """Extracts basic acoustic features using librosa."""
    try:
        # Load only 30 seconds from the middle to save time
        y, sr = librosa.load(file_path, duration=30, offset=60)
        
        # 1. Tempo (BPM)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # 2. Energy (RMS)
        rms = librosa.feature.rms(y=y)
        energy = np.mean(rms)
        
        # 3. Brightness (Spectral Centroid)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        brightness = np.mean(centroid)
        
        return {
            "bpm": float(tempo),
            "energy": float(energy),
            "brightness": float(brightness)
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def scan_library():
    print(f"Scanning library at {MUSIC_PATH}...")
    albums = {}
    
    # Walk the directory
    for root, dirs, files in os.walk(MUSIC_PATH):
        # Filter for audio files
        audio_files = [f for f in files if f.endswith(('.mp3', '.flac', '.m4a', '.wav'))]
        if not audio_files:
            continue
            
        # Group by folder (Album)
        album_path = Path(root)
        album_name = album_path.name
        artist_name = album_path.parent.name
        
        # Pick the representative track (longest one)
        max_duration = 0
        rep_track = None
        
        album_data = {
            "artist": artist_name,
            "album": album_name,
            "genres": set(),
            "years": set(),
            "tracks_count": len(audio_files)
        }
        
        for f in audio_files:
            file_path = album_path / f
            try:
                tag = TinyTag.get(str(file_path))
                if tag.genre: album_data["genres"].add(tag.genre)
                if tag.year: album_data["years"].add(tag.year)
                if tag.duration and tag.duration > max_duration:
                    max_duration = tag.duration
                    rep_track = file_path
            except:
                continue
        
        album_data["genres"] = list(album_data["genres"])
        album_data["years"] = list(album_data["years"])
        album_data["rep_track"] = str(rep_track) if rep_track else None
        
        albums[str(album_path)] = album_data

    print(f"Found {len(albums)} albums. Starting acoustic analysis...")
    
    # Run acoustic analysis on representative tracks
    results = []
    for i, (path, data) in enumerate(tqdm(albums.items())):
        if data["rep_track"]:
            acoustic = analyze_audio(data["rep_track"])
            if acoustic:
                data.update(acoustic)
        results.append(data)
        
        # Save every 5 albums to provide immediate feedback
        if i % 5 == 0:
            with open(INSIGHT_FILE, "w") as f:
                json.dump(results, f, indent=4)
        
    # Final save
    with open(INSIGHT_FILE, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"Analysis complete. Results saved to {INSIGHT_FILE}")

if __name__ == "__main__":
    scan_library()
