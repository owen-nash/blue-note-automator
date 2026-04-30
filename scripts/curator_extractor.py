import os
import json
import librosa
import numpy as np
from tinytag import TinyTag
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MUSIC_PATH = os.getenv("MUSIC_PATH", "/opt/selfhosted/media/music")
VECTOR_DB_PATH = "library_vectors.json"

def extract_features(file_path, analyze_audio=False):
    """
    Extracts metadata and optionally basic audio features.
    """
    try:
        tag = TinyTag.get(file_path)
        
        bpm = 0
        energy = 0
        
        if analyze_audio:
            y, sr = librosa.load(file_path, duration=15, offset=30) if os.path.getsize(file_path) > 1024*1024 else (None, None)
            if y is not None:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                bpm = float(tempo)
                energy = float(np.mean(librosa.feature.rms(y=y)))
            
        return {
            "path": file_path,
            "title": tag.title,
            "artist": tag.artist,
            "album": tag.album,
            "year": tag.year,
            "genre": tag.genre,
            "duration": tag.duration,
            "bpm": bpm,
            "energy": energy,
            "label": getattr(tag, 'comment', '')
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def scan_library():
    print(f"Scanning library at {MUSIC_PATH}...")
    vectors = []
    
    # Supported extensions
    exts = ('.mp3', '.flac', '.m4a', '.wav', '.ogg')
    
    for root, _, files in os.walk(MUSIC_PATH):
        for file in files:
            if file.lower().endswith(exts):
                full_path = os.path.join(root, file)
                print(f"Processing: {file}")
                feat = extract_features(full_path)
                if feat:
                    vectors.append(feat)
                    
    with open(VECTOR_DB_PATH, "w") as f:
        json.dump(vectors, f, indent=2)
    
    print(f"Extraction complete. {len(vectors)} tracks vectorized.")

if __name__ == "__main__":
    scan_library()
