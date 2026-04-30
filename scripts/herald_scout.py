import feedparser
import os
import requests
from herald_db import is_article_processed
from dotenv import load_dotenv

load_dotenv()

# RSS Feeds for the "Herald"
FEEDS = {
    "The Gig (Nate Chinen)": "https://natechinen.substack.com/feed",
    "DFSBP (Hank Shteamer)": "https://hankshteamer.substack.com/feed",
    "Big Butter & Egg Man (Will Layman)": "https://willlayman.substack.com/feed",
    "Transitional Technology (Ethan Iverson)": "https://ethaniverson.substack.com/feed",
    "LondonJazz News": "https://londonjazznews.com/feed/",
    "JazzTimes": "https://jazztimes.com/feed/",
    "DownBeat": "https://downbeat.com/site/rss"
}

from playwright.async_api import async_playwright
import asyncio

async def get_full_text(url):
    """
    Uses local Playwright to extract clean article text.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Simple extraction: Get the body text and some structural elements
            # We filter out scripts, styles, and navs
            content = await page.evaluate('''() => {
                const clones = document.body.cloneNode(true);
                const toRemove = clones.querySelectorAll('script, style, nav, footer, header, .ads, .sidebar');
                toRemove.forEach(el => el.remove());
                return clones.innerText;
            }''')
            
            await browser.close()
            return content
    except Exception as e:
        print(f"Playwright extraction failed for {url}: {e}")
    return None

def scout_new_articles():
    """Parses feeds and returns a list of new, unprocessed articles."""
    new_articles = []
    
    for source_name, feed_url in FEEDS.items():
        print(f"Scouting {source_name}...")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                link = entry.link
                if not is_article_processed(link):
                    # We have a new article!
                    article_data = {
                        "source": source_name,
                        "title": entry.title,
                        "link": link,
                        "published": getattr(entry, 'published', 'Unknown Date'),
                        "summary": getattr(entry, 'summary', entry.title),
                        "content": "" 
                    }
                    
                    # If the summary is very short, it's likely truncated.
                    # We will try to pull full text in the curation phase if needed.
                    new_articles.append(article_data)
        except Exception as e:
            print(f"Error scouting {source_name}: {e}")
            
    return new_articles

if __name__ == "__main__":
    articles = scout_new_articles()
    print(f"\nFound {len(articles)} new articles across all sources.")
    for a in articles[:3]:
        print(f"- [{a['source']}] {a['title']}")
