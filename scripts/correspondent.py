import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_digest(approved_albums, watchlist_albums):
    """
    Generates a Markdown digest for SilverBullet using Llama-3-70b via OpenRouter.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    date_str = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    Write a warm, sophisticated editorial email for a Jazz collector. 
    The tone should be insightful, like a column in a premium jazz magazine.
    
    New Arrivals (Approved for Library):
    {json.dumps(approved_albums, indent=2)}
    
    The Watchlist (Interesting but not for library yet):
    {json.dumps(watchlist_albums, indent=2)}
    
    Format as Markdown. 
    Include sections:
    1. Introduction (Brief commentary on this week's haul)
    2. The New Arrivals (Detail each album, its personnel, and a short blurb)
    3. From the Watchlist (Briefly mention these and why they were deferred)
    4. Closing
    
    Be concise but flavorful.
    """

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/ownash/blue-note-automator",
                "X-Title": "Blue Note Automator",
            },
            model="meta-llama/llama-3.3-70b-instruct", # Using Llama 3.3 70b as a high-quality summary model
            messages=[
                {"role": "system", "content": "You are a world-class Jazz Correspondent."},
                {"role": "user", "content": prompt},
            ]
        )
        
        digest_content = completion.choices[0].message.content
        return digest_content
    except Exception as e:
        return f"Error generating digest: {str(e)}"

def save_to_silverbullet(content):
    """
    Saves the content as a new Markdown page in SilverBullet.
    """
    sb_path = os.getenv("SB_SPACE_PATH")
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Blue Note Digest {date_str}.md"
    full_path = os.path.join(sb_path, filename)
    
    try:
        with open(full_path, "w") as f:
            f.write(content)
        print(f"Digest saved to SilverBullet: {full_path}")
        return True
    except Exception as e:
        print(f"Error saving to SilverBullet: {str(e)}")
        return False

from discord_reporter import send_discord_message

def send_digest_to_discord(content):
    """
    Sends the weekly digest to Discord.
    """
    embed = {
        "title": f"🎺 Weekly Blue Note Digest: {datetime.now().strftime('%Y-%m-%d')}",
        "description": content,
        "color": 15844367, # Gold
        "timestamp": datetime.now().isoformat()
    }
    return send_discord_message(embeds=[embed])

import json # For the test block below
if __name__ == "__main__":
    # Mock data for testing
    approved = [
        {
            "title": "Past Present",
            "artist": "John Scofield",
            "personnel": "John Scofield, Joe Lovano, Larry Grenadier, Bill Stewart",
            "reasoning": "A masterful reunion of Scofield's classic quartet voice."
        }
    ]
    watchlist = [
        {
            "title": "Heaven and Earth",
            "artist": "Kamasi Washington",
            "reasoning": "Fits the nu-jazz/maximalist profile, interesting but outside current curation goals."
        }
    ]
    
    print("Generating test digest...")
    digest = generate_digest(approved, watchlist)
    print("\n--- DIGEST START ---\n")
    print(digest)
    print("\n--- DIGEST END ---\n")
    # save_to_silverbullet(digest) # Test save
