import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SB_SPACE_PATH = os.getenv("SB_SPACE_PATH", "/opt/selfhosted/knowledge/sb_space")
VECTOR_DB_PATH = "/home/ownash/blue-note-automator/library_vectors.json"
ATELIER_ROOT = os.path.join(SB_SPACE_PATH, "Jazz Atelier")

def generate_atelier_index(data):
    """
    Generates the main Atelier index page using v2.6 syntax.
    """
    total_tracks = len(data)
    artists = sorted(list(set([v.get('artist') for v in data if v.get('artist')])))
    albums = sorted(list(set([v.get('album') for v in data if v.get('album')])))
    
    content = f"""# 🎷 Jazz Atelier
Welcome to your curated jazz library map.

## 📊 Quick Stats
- **Total Tracks:** {total_tracks}
- **Unique Artists:** {len(artists)}
- **Total Albums:** {len(albums)}

## 🗺️ Library Map
- [[Jazz Atelier/Artists|All Artists]]
- [[Jazz Atelier/Labels|Record Labels]]
- [[Jazz Atelier/Recent|Recently Added]]

## ⚡ Active Queries
### Recently Played (v2.6)
${{query[[ from item = index.tag "track" order by item.lastPlayed desc limit 10 render [[ * [[${{item.artist}}]] - ${{item.name}} ]] ]]}}

### Starred Albums
${{query[[ from item = index.tag "album" where item.starred == true render [[ * [[${{item.name}}]] by [[${{item.artist}}]] ]] ]]}}
"""
    os.makedirs(ATELIER_ROOT, exist_ok=True)
    with open(os.path.join(ATELIER_ROOT, "Atelier.md"), "w") as f:
        f.write(content)

def update_daily_note_template():
    """
    Adds the Atelier link to the Daily Note template.
    """
    template_path = os.path.join(SB_SPACE_PATH, "Templates", "Daily Note.md")
    if not os.path.exists(template_path):
        print(f"Warning: Template not found at {template_path}")
        return

    with open(template_path, "r") as f:
        lines = f.readlines()
    
    # Add link after the title if not already there
    new_lines = []
    link_added = False
    for line in lines:
        new_lines.append(line)
        if line.startswith("# ") and not link_added:
            new_lines.append("\nQuick Link: [[Jazz Atelier/Atelier|🎷 Jazz Atelier]]\n")
            link_added = True
            
    with open(template_path, "w") as f:
        f.writelines(new_lines)

def run_builder():
    print("--- Building Jazz Atelier ---")
    if not os.path.exists(VECTOR_DB_PATH):
        print("Error: library_vectors.json not found.")
        return
        
    with open(VECTOR_DB_PATH, "r") as f:
        data = json.load(f)
        
    generate_atelier_index(data)
    update_daily_note_template()
    print(f"Atelier index generated and Daily Note template updated in {SB_SPACE_PATH}")

if __name__ == "__main__":
    run_builder()
