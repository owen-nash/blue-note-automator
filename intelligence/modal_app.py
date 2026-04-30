import modal
import os
import json
import random
import traceback
from typing import List, Optional

# Define the container image with all 2026 dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libglib2.0-0", "libnss3", "libatk1.0-0", "libatk-bridge2.0-0", "libcups2", "libdrm2", "libxkbcommon0", "libxcomposite1", "libxdamage1", "libxrandr2", "libgbm1", "libpango-1.0-0", "libcairo2", "libasound2")
    .pip_install(
        "fastapi",
        "uvicorn",
        "openai",
        "ytmusicapi",
        "pydantic",
        "python-dotenv",
        "requests",
        "musicbrainzngs",
        "feedparser",
        "pylast",
        "mem0ai",
        "voyageai",
        "playwright",
        "psycopg2-binary"
    )
    .run_commands("playwright install chromium")
)

app = modal.App("blue-note-intelligence", image=image)
secrets = [modal.Secret.from_name("blue-note-secrets")]

# --- UTILS ---

def extract_json(text: str):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    return None

# --- TASTE SYNC PIPELINE ---

@app.function(secrets=secrets, timeout=300)
def sync_taste():
    import pylast
    import musicbrainzngs
    from mem0 import MemoryClient

    musicbrainzngs.set_useragent("BlueNoteAutomator", "1.0", "owen.nash1306@gmail.com")

    network = pylast.LastFMNetwork(
        api_key=os.environ["LASTFM_API_KEY"],
        api_secret=os.environ["LASTFM_API_SECRET"]
    )
    user = network.get_user(os.environ["LASTFM_USER"])
    top_artists = [a.item.name for a in user.get_top_artists(limit=50)]

    m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
    user_id = os.environ["TASTE_USER_ID"]

    existing = m0.get_all(user_id=user_id)
    existing_artists = set()
    for mem in existing:
        text = mem.get("text", "")
        if text.startswith("Artist: "):
            existing_artists.add(text.split("\n")[0].replace("Artist: ", "").strip())

    for artist_name in top_artists:
        if artist_name in existing_artists:
            print(f"Skipping {artist_name} (already ingested)")
            continue
        try:
            mb_results = musicbrainzngs.search_artists(artist=artist_name, limit=1)
            genres = []
            if mb_results.get("artist-list"):
                artist_id = mb_results["artist-list"][0]["id"]
                mb_artist = musicbrainzngs.get_artist_by_id(artist_id, includes=["tags", "genres"])
                if "artist" in mb_artist:
                    tags = mb_artist["artist"].get("tag-list", [])
                    genres = [t["name"] for t in tags[:5]]
            genre_str = ", ".join(genres) if genres else "jazz, improvisation"
            bio = f"they are pioneers of {genre_str}, shaping the sound of modern music"
            paragraph = (
                f"Artist: {artist_name}\n\n"
                f"{artist_name} is a celebrated force in music. "
                f"Widely recognized for their distinct voice, {bio}. "
                f"Their body of work spans {genre_str}, drawing from deep tradition "
                f"while constantly pushing forward. Listening to {artist_name} "
                f"reveals a masterful command of texture, timing, and emotion."
            )
            m0.add(paragraph, user_id=user_id)
            print(f"Ingested: {artist_name} [{genre_str}]")
        except Exception as e:
            print(f"Error ingesting {artist_name}: {e}")

# --- DISCOVERY ENDPOINT ---

@app.function(secrets=secrets, timeout=300)
@modal.fastapi_endpoint(method="POST")
async def discover(payload: dict):
    from openai import OpenAI
    from mem0 import MemoryClient
    from ytmusicapi import YTMusic
    from fastapi import HTTPException
    import musicbrainzngs

    print(f"--- DISCOVERY START: {payload.get('user_id')} ---")
    musicbrainzngs.set_useragent("BlueNoteAutomator", "1.0", "owen.nash1306@gmail.com")

    # Initialize Mem0
    try:
        m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
        user_id = payload.get("user_id", "default_user")
        memories = m0.get_all(user_id=user_id)
        soul_context = "\n".join([mem["text"] for mem in memories]) if memories else "Focus on classic hard-bop."
    except Exception as e:
        print(f"Mem0 Error: {e}")
        soul_context = "Focus on classic hard-bop."

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])

    # STAGE 1: Musical Analysis
    artists = payload.get("artists", ["Miles Davis"])
    sonnet_prompt = f"Historian persona. User soul: {soul_context}. Current: {artists}. Pick 5 links. JSON Output: missions[seed_artist, new_artist, album, connection, personnel, vibe]"
    
    try:
        res = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.6",
            messages=[{"role": "user", "content": sonnet_prompt}]
        )
        content = res.choices[0].message.content
        parsed = extract_json(content)
        if not parsed or "missions" not in parsed:
            raise Exception("No JSON")
        raw_missions = parsed["missions"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stage 1: {str(e)}")

    verified = []
    ytm = YTMusic()
    for m in raw_missions:
        try:
            mb_res = musicbrainzngs.search_releases(artist=m['new_artist'], release=m['album'], limit=1)
            if mb_res['release-count'] > 0:
                ytm_search = ytm.search(f"{m['new_artist']} {m['album']}", filter="albums")
                if ytm_search:
                    m['ytm_link'] = f"https://music.youtube.com/browse/{ytm_search[0]['browseId']}"
                    verified.append(m)
                    try: m0.add(f"Discovered {m['album']}", user_id=user_id)
                    except: pass
            if len(verified) >= 5: break
        except: continue

    if not verified:
        raise HTTPException(status_code=500, detail="No verified albums found.")

    # STAGE 2: Drafting
    try:
        opus_res = client.chat.completions.create(
            model="anthropic/claude-opus-4.7",
            messages=[{"role": "user", "content": f"Write Discord post for: {json.dumps(verified)}"}]
        )
        drafted_message = opus_res.choices[0].message.content
    except:
        drafted_message = "Here are your 5 verified jazz discoveries!"

    return {"missions": verified, "drafted_message": drafted_message}

# --- HERALD ENDPOINT ---

@app.function(secrets=secrets, timeout=600)
@modal.fastapi_endpoint(method="POST")
async def curate_herald(payload: dict):
    from openai import OpenAI
    import feedparser
    from playwright.async_api import async_playwright

    FEEDS = {"The Gig": "https://natechinen.substack.com/feed", "DownBeat": "https://downbeat.com/site/rss"}
    processed_links = payload.get("processed_links", [])
    new_articles = []

    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.link not in processed_links:
                    new_articles.append({"source": source, "title": entry.title, "link": entry.link})
        except: pass

    if not new_articles: return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for art in new_articles[:3]:
            page = await browser.new_page()
            try:
                await page.goto(art['link'], timeout=15000)
                art['full_text'] = (await page.evaluate("document.body.innerText"))[:3000]
            except: art['full_text'] = ""
            await page.close()
        await browser.close()

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    try:
        res = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.6",
            messages=[{"role": "user", "content": f"Curate these 8/10+: {json.dumps(new_articles[:3])}. JSON: selected_articles[url, title, source, rating, summary]"}]
        )
        return extract_json(res.choices[0].message.content).get("selected_articles", [])
    except: return []


# --- TASTE SYNC CRON (every 6 hours) ---

@app.function(secrets=secrets, schedule=modal.Cron("0 */6 * * *"), timeout=120)
async def sync_taste():
    from mem0 import MemoryClient
    import pylast

    print("--- TASTE SYNC START ---")

    api_key = os.environ["LASTFM_API_KEY"]
    api_secret = os.environ["LASTFM_API_SECRET"]
    lastfm_user = os.environ["LASTFM_USER"]
    taste_user_id = os.environ.get("TASTE_USER_ID", "taste_profile")

    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)
    user = network.get_user(lastfm_user)

    recent_tracks = user.get_recent_tracks(limit=50)

    artists = set()
    for track in recent_tracks:
        try:
            artists.add(track.track.artist.name)
        except Exception:
            pass

    print(f"Synced {len(artists)} unique artists from last {len(recent_tracks)} scrobbles")

    m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
    m0.add(
        f"Current taste profile artists: {', '.join(sorted(artists))}",
        user_id=taste_user_id
    )

    print("--- TASTE SYNC COMPLETE ---")
