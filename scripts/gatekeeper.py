import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def evaluate_album(album_data, taste_profile):
    """
    Evaluates an album using Claude 3.5 Sonnet via OpenRouter.
    Categorizes into 'Approved' or 'Watchlist'.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    system_prompt = f"""
    You are a sophisticated Jazz Correspondent and Library Curator. 
    Your goal is to manage a high-quality library of acoustic and modern-electric jazz.
    
    CRITICAL CONSTRAINT: 
    - Explicitly BLOCK maximalist/nu-jazz (e.g., Kamasi Washington, Shabaka Hutchings) from the library.
    - Focus on acoustic, straight-ahead, hard bop, post-bop, or modern electric jazz that maintains a certain sophisticated aesthetic.
    
    User Taste Profile (Artist Names): {", ".join(taste_profile[:50])} (and similar).
    
    You will be given an album title, artist, and personnel.
    Decide if this album should be 'Approved' for download or put on the 'Watchlist' (Notify only).
    
    Your response must be a valid JSON object with the following keys:
    {{
        "decision": "Approved" or "Watchlist",
        "reasoning": "A short 1-2 sentence blurb on why it fits or why it's on the watchlist.",
        "genre_tags": ["tag1", "tag2"]
    }}
    """

    user_content = f"Album: {album_data['title']}\nArtist: {album_data['artist']}\nPersonnel: {album_data.get('personnel', 'Unknown')}"

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/ownash/blue-note-automator",
                "X-Title": "Blue Note Automator",
            },
            model="anthropic/claude-3.7-sonnet",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
        )
        
        content = completion.choices[0].message.content
        # Basic cleanup in case of markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        return json.loads(content)
    except Exception as e:
        return {"decision": "Watchlist", "reasoning": f"Error in evaluation: {str(e)}", "genre_tags": []}

if __name__ == "__main__":
    # Test cases
    taste_profile = ["Miles Davis", "John Coltrane", "John Scofield", "Bill Stewart"]
    
    test_albums = [
        {
            "title": "Heaven and Earth",
            "artist": "Kamasi Washington",
            "personnel": "Kamasi Washington (sax), Thundercat (bass), etc."
        },
        {
            "title": "Past Present",
            "artist": "John Scofield",
            "personnel": "John Scofield (guitar), Joe Lovano (sax), Larry Grenadier (bass), Bill Stewart (drums)"
        }
    ]
    
    for album in test_albums:
        print(f"\nEvaluating: {album['title']} by {album['artist']}...")
        result = evaluate_album(album, taste_profile)
        print(json.dumps(result, indent=2))
