import os
from anthropic import AnthropicVertex

def test_claude_vertex():
    print("--- Testing Claude 3.7 Sonnet on Vertex AI ---")
    project_id = "zeus-494700"
    region = "us-central1"
    
    # Set the credentials env var
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ownash/blue-note-automator/sa-key.json"
    
    client = AnthropicVertex(project_id=project_id, region=region)
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6@default",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, what is your name?"}
            ]
        )
        print(f"Response: {response.content[0].text}")
    except Exception as e:
        print(f"Vertex AI Error: {e}")

if __name__ == "__main__":
    test_claude_vertex()
