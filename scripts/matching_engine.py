import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-3.1-8b-instruct"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def clean_artist_name(raw_name):
    """
    Uses LLM to extract the core searchable artist name for YTM.
    """
    system_prompt = """
    You are a professional Music Librarian. 
    Your task is to take a raw folder name and return ONLY the core artist name.
    Example: 'The Miles Davis Quintet' -> 'Miles Davis'
    """
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/ownash/blue-note-automator",
                "X-Title": "Streaming Migration Cleaner",
            },
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Clean this artist name: {raw_name}"},
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error cleaning name '{raw_name}': {e}")
        return raw_name

if __name__ == "__main__":
    test_names = [
        "The Miles Davis Quintet",
        "John Coltrane & Johnny Hartman",
        "The Modern Jazz Quartet"
    ]
    for name in test_names:
        print(f"'{name}' -> '{clean_artist_name(name)}'")
