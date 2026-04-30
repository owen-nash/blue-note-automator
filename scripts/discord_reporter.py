import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(content=None, embeds=None):
    """
    Sends a message to Discord via Webhook.
    """
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL not found in .env")
        return False
    
    # Discord content limit is 2000 chars
    if content and len(content) > 1900:
        content = content[:1900] + "... (truncated)"

    payload = {
        "username": "Blue Note Librarian"
    }
    
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds
        
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Discord message: {e}")
        return False

if __name__ == "__main__":
    # Test message
    send_discord_message("🎺 **Blue Note Automator Online.** Testing the new Discord reporting system.")
