import os
import pexpect
import sys
import json
import re
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

def get_llm_choice(prompt_context):
    """
    Asks the LLM to analyze Beets candidates and choose the best action.
    """
    system_prompt = """
    You are a professional Music Librarian using the Beets tagger.
    You will be provided with the terminal output showing a music album and potential matches found in the database.
    
    Your goal:
    1.  **Analyze** the "Original" metadata vs the "Candidates".
    2.  **Choose 'a' (Apply)**: Only if a candidate is a very high confidence match for the actual album.
    3.  **Choose 'U' (Use as-is)**: If no database match is perfect, but the original tags are already correct.
    4.  **Choose 's' (Skip)**: If the candidates are wrong and the original tags are also messy/incorrect.
    
    Rules:
    - If there are NO candidates listed (e.g., "No matching release found"), look at the original tags. If they look good, choose 'U'. If they are bad, choose 's'.
    - If you are NOT confident, choose 's'.
    - Respond with ONLY the single character: 'a', 's', or 'U'.
    """
    
    # Clean up ANSI escape codes before sending to LLM
    clean_context = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', prompt_context)
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/ownash/blue-note-automator",
                "X-Title": "Beets LLM Tagger",
            },
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Decide the best action for this Beets output:\n\n{clean_context}"},
            ]
        )
        choice = completion.choices[0].message.content.strip().lower()
        # Ensure we only return one of the valid choices
        for char in choice:
            if char in 'asu':
                return char
        return 's'
    except Exception as e:
        print(f"Error consulting LLM: {e}")
        return 's'

def run_beets_import():
    # Use -i only, pexpect will handle the terminal emulation
    cmd = "docker exec -i media-beets-1 beet import /music"
    
    print(f"Spawning: {cmd}")
    # Spawn through bash to handle the piping correctly if needed
    child = pexpect.spawn("/bin/bash", ["-c", cmd], encoding='utf-8', timeout=900)
    child.logfile_read = sys.stdout

    while True:
        try:
            # We add a pattern for the "Scanning" phase to know it's working
            index = child.expect([
                r'\[a\]pply, \[m\]ore candidates, \[s\]kip, \[U\]se as-is',
                r'\[S\]kip, Use as-is, as Tracks, Group albums',
                r'Enter search, enter Id, a\[b\]ort, \[s\]kip',
                r'Scanning',
                pexpect.EOF,
                pexpect.TIMEOUT
            ], timeout=600)

            if index == 0 or index == 1:
                print("\n\n[LLM Tagger] PROMPT DETECTED.")
                prompt_context = child.before
                choice = get_llm_choice(prompt_context)
                print(f"[LLM Tagger] LLM DECISION: {choice.upper()}")
                child.sendline(choice)
            
            elif index == 2:
                print("\n\n[LLM Tagger] NO MATCH. SKIPPING.")
                child.sendline('s')
            
            elif index == 3:
                # Just logged "Scanning", continue waiting
                continue

            elif index == 4:
                print("\n\n[LLM Tagger] FINISHED.")
                break
                
            elif index == 5:
                print("\n\n[LLM Tagger] TIMEOUT.")
                break
            
            elif index == 1:
                print("\n[LLM Tagger] Import finished.")
                break
            
            elif index == 2:
                print("\n[LLM Tagger] Timeout. Exiting.")
                break

        except pexpect.exceptions.EOF:
            break
        except Exception as e:
            print(f"\n[LLM Tagger] Error: {e}")
            break

if __name__ == "__main__":
    run_beets_import()
