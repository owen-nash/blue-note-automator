import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from taste_engine import get_hybrid_taste_profile
from herald_scout import get_full_text

load_dotenv()

async def curate_articles(articles):
    """
    Curates a list of articles using Claude 3.7 Sonnet.
    Filters marketing fluff, rates relevance, and selects the best.
    """
    if not articles:
        return []

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    taste_profile = get_hybrid_taste_profile()
    
    # Prepare article summaries for the LLM
    article_summaries = []
    for a in articles:
        # For the curation prompt, we'll try to get full text if possible
        full_text = await get_full_text(a['link'])
        content_to_review = full_text if full_text else a['summary']
        
        article_summaries.append({
            "id": a['link'],
            "source": a['source'],
            "title": a['title'],
            "content": content_to_review[:5000] # Cap content for context window
        })

    system_prompt = f"""
    You are a world-class Jazz Editor and a professional Jazz Drummer. 
    Your goal is to curate a daily news digest for a sophisticated jazz listener and practitioner.

    CRITICAL FILTERS:
    1. NO MARKETING FLUFF: Ignore press releases, tour announcements without context, or superficial "buy this" notices.
    2. DEPTH ONLY: Prioritize deep-dive interviews, technical analysis, historical context, or major industry shifts.
    3. DRUMMER FOCUS: Strongly prioritize articles mentioning rhythmic innovation, drum hardware, rhythm section dynamics, or legendary/modern drummers (e.g., Bill Stewart, Brian Blade, Jeff Watts, Marcus Gilmore).
    4. PERSONALIZATION: High relevance to these artists: {", ".join(taste_profile[:100])}.

    YOUR TASK:
    - Review the provided articles.
    - Rate each out of 10 for "Relevance & Musical Importance" to this specific user.
    - Only include articles that score 8/10 or higher.
    - For each selected article, write a sharp, insightful 2-3 sentence summary explaining EXACTLY why it matters to a drummer/practitioner.

    RESPONSE FORMAT:
    You MUST respond with a valid JSON object in this format:
    {{
        "selected_articles": [
            {{
                "url": "original_url",
                "title": "Article Title",
                "source": "Source Name",
                "rating": 9,
                "summary": "Your custom, drummer-focused summary."
            }}
        ]
    }}
    """

    user_content = f"Articles to Curate:\n{json.dumps(article_summaries, indent=2)}"

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/ownash/blue-note-automator",
                "X-Title": "Blue Note Automator Herald",
            },
            model="anthropic/claude-sonnet-4.6",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
        )
        
        content = completion.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        result = json.loads(content)
        return result.get("selected_articles", [])
    except Exception as e:
        print(f"Error in Herald curation: {e}")
        return []

if __name__ == "__main__":
    import asyncio
    # Mock test
    test_articles = [
        {
            "source": "The Gig",
            "title": "The Art of the Ride Cymbal",
            "link": "https://example.com/ride",
            "summary": "A deep dive into how Bill Stewart and Elvin Jones approach ride cymbal patterns."
        },
        {
            "source": "JazzTimes",
            "title": "Buy our new JazzTimes T-Shirt",
            "link": "https://example.com/shirt",
            "summary": "Check out our merch!"
        }
    ]
    curated = asyncio.run(curate_articles(test_articles))
    print(f"Curated {len(curated)} articles.")
    print(json.dumps(curated, indent=2))
