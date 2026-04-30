import os
import json
import requests
from datetime import datetime
from taste_engine import get_hybrid_taste_profile

# Cloud Run Endpoint for Intelligence Layer
DISCOVERY_SERVICE_URL = "https://discovery-service-412081152192.us-central1.run.app/discover"

def get_blacklist():
    """Loads the blacklist of avoided artists/albums."""
    path = "/home/ownash/blue-note-automator/blacklist.json"
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except: pass
    return {"artists": [], "albums": []}

def get_discovery_missions(count=5):
    """Calls the Cloud Run Discovery Service to get verified missions and a drafted message."""
    jazz_profile = get_hybrid_taste_profile()
    blacklist = get_blacklist()
    
    payload = {
        "artists": list(jazz_profile),
        "blacklist_artists": blacklist.get("artists", []),
        "blacklist_albums": blacklist.get("albums", [])
    }
    
    print(f"Calling Cloud Run Discovery Service at {DISCOVERY_SERVICE_URL}...")
    response = requests.post(DISCOVERY_SERVICE_URL, json=payload)
    
    if response.status_code != 200:
        print(f"Cloud Run Error: {response.text}")
        raise Exception(f"Discovery Service failed: {response.text}")
        
    data = response.json()
    # Returns (missions, drafted_message)
    return data['missions'], data['drafted_message']

def get_platform_links(artist, album):
    """DEPRECATED: Now handled by the Cloud Run service."""
    return {"ytm": "#"}

def run_curator():
    print(f"--- Curator V3 Logic Invoked (Cloud Run Mode): {datetime.now()} ---")
    missions, drafted_message = get_discovery_missions(count=5)
    return missions, drafted_message

if __name__ == "__main__":
    missions, msg = run_curator()
    print(msg)
