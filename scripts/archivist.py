import subprocess
import os

# Correct path to tiddl
TIDDL_PATH = "/home/ownash/.local/bin/tiddl"
# Redirecting to the Watchdog directory
DOWNLOAD_TARGET = "/home/ownash/temp_download"

def run_tiddl(search_query):
    """
    Calls the tiddl CLI to download music.
    Downloads to the shared temp directory so the Opus Watchdog can process it.
    """
    if not os.path.exists(DOWNLOAD_TARGET):
        os.makedirs(DOWNLOAD_TARGET)
    
    print(f"Starting tiddl download for: {search_query} -> {DOWNLOAD_TARGET}")
    try:
        # Download to the watchdog folder in lossless quality
        result = subprocess.run([
            TIDDL_PATH, "search", search_query, "download", 
            "--path", DOWNLOAD_TARGET, 
            "--quality", "lossless"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Download successful. Watchdog will handle Opus conversion and moving.")
            return True
        else:
            print(f"Download failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running tiddl: {str(e)}")
        return False

if __name__ == "__main__":
    # Test path check
    print(f"Target directory verified: {DOWNLOAD_TARGET}")
