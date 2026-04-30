import os
import vertexai
from vertexai.generative_models import GenerativeModel

def test_gemini_vertex():
    print("--- Testing Gemini on Vertex AI ---")
    project_id = "zeus-494700"
    region = "us-central1"
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ownash/blue-note-automator/sa-key.json"
    
    vertexai.init(project=project_id, location=region)
    model = GenerativeModel("gemini-3.1-flash-lite-preview@default")
    
    try:
        response = model.generate_content("Hello, what is your name?")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Gemini Vertex Error: {e}")

if __name__ == "__main__":
    test_gemini_vertex()
