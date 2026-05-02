import modal
import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Optional

MB_USER_AGENT = ("BlueNoteAutomator", "1.0", "owen.nash1306@gmail.com")

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
        "httpx",
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

# --- DISCOVERY HELPER ---

async def _run_discovery(user_id: str):
    from openai import OpenAI
    from mem0 import MemoryClient
    from ytmusicapi import YTMusic
    import musicbrainzngs

    musicbrainzngs.set_useragent(*MB_USER_AGENT)

    m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])

    raw = m0.get_all(filters={"user_id": user_id})
    all_memories = raw if isinstance(raw, list) else raw.get('results', [])
    taste_entries = []
    sent_entries = []
    for mem in all_memories:
        text = mem.get("text", "")
        if text.startswith("Artist: ") or text.startswith("Liked:") or text.startswith("Disliked:"):
            taste_entries.append(text)
        elif text.startswith("Sent:"):
            sent_entries.append(text)
    taste_context = "\n".join(taste_entries) if taste_entries else "Focus on classic hard-bop and post-bop jazz."

    three_months_ago = datetime.now() - timedelta(days=90)
    re_sendable = set()
    for sent_text in sent_entries:
        try:
            parts = sent_text.replace("Sent: ", "", 1).rsplit(" by ", 1)
            if len(parts) >= 2:
                album_name = parts[0].strip()
                rest = parts[1].strip()
                if rest.endswith(")") and "(" in rest:
                    artist_name = rest[:rest.rfind("(")].strip()
                    date_str = rest[rest.rfind("(")+1:rest.rfind(")")]
                    sent_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if sent_date < three_months_ago:
                        has_feedback = any(
                            album_name in t for t in taste_entries
                        )
                        if not has_feedback:
                            re_sendable.add(sent_text)
        except:
            pass

    sent_for_prompt = [s for s in sent_entries if s not in re_sendable]
    sent_context = ""
    if sent_for_prompt:
        sent_context = "\n\nCRITICAL: DO NOT RECOMMEND ANY OF THESE PREVIOUSLY SENT ALBUMS:\n" + "\n".join(sent_for_prompt)

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])

    sonnet_prompt = (
        "Historian persona. Analyze the user's complete jazz taste profile below. "
        "Identify patterns in their preferred artists, genres, and styles. "
        "Generate 5 novel but authentic discovery directions they have not heard yet "
        "but would likely love based on their taste. Each direction should be a "
        "specific seed_artist (a known artist the user may not have explored) and a "
        "new_artist/album that connects to it. Avoid obvious names already in the taste profile."
        f"\n\nTaste Profile:\n{taste_context[:3000]}"
        f"{sent_context}"
        "\n\nJSON Output: missions[seed_artist, new_artist, album, connection, personnel, vibe]"
    )

    res = client.chat.completions.create(
        model="anthropic/claude-sonnet-4.6",
        messages=[{"role": "user", "content": sonnet_prompt}]
    )
    parsed = extract_json(res.choices[0].message.content)
    if not parsed or "missions" not in parsed:
        raise Exception("No JSON")
    raw_missions = parsed["missions"]

    verified = []
    ytm = YTMusic()
    for m in raw_missions:
        try:
            mb_res = musicbrainzngs.search_releases(artist=m['new_artist'], release=m['album'], limit=1)
            if mb_res['release-count'] > 0:
                query = f"{m['new_artist']} {m['album']}"
                ytm_search_albums = ytm.search(query, filter="albums")
                if ytm_search_albums and 'browseId' in ytm_search_albums[0]:
                    m['ytm_link'] = f"https://music.youtube.com/browse/{ytm_search_albums[0]['browseId']}"
                    verified.append(m)
                    try: m0.add(f"Discovered {m['album']}", user_id=user_id)
                    except: pass
                else:
                    ytm_search_all = ytm.search(query)
                    link_found = False
                    for res in ytm_search_all:
                        if 'browseId' in res:
                            m['ytm_link'] = f"https://music.youtube.com/browse/{res['browseId']}"
                            link_found = True
                            break
                        elif 'videoId' in res:
                            m['ytm_link'] = f"https://music.youtube.com/watch?v={res['videoId']}"
                            link_found = True
                            break
                    if link_found:
                        verified.append(m)
                        try: m0.add(f"Discovered {m['album']}", user_id=user_id)
                        except: pass
            if len(verified) >= 5: break
        except: continue

    today_str = datetime.now().strftime("%Y-%m-%d")
    for m in verified:
        try:
            m0.add(f"Sent: {m['album']} by {m['new_artist']} ({today_str})", user_id=user_id)
        except:
            pass

    if not verified:
        raise Exception("No verified albums found.")

    drafted_message = "Here are your 5 verified jazz discoveries!"
    try:
        opus_res = client.chat.completions.create(
            model="anthropic/claude-opus-4.7",
            messages=[{"role": "user", "content": f"Write Discord post for: {json.dumps(verified)}"}]
        )
        drafted_message = opus_res.choices[0].message.content
    except:
        pass

    return verified, drafted_message


# --- TASTE SYNC PIPELINE ---

@app.function(secrets=secrets, timeout=300)
def enrich_taste_profile(artist_name: str):
    import musicbrainzngs
    from mem0 import MemoryClient

    musicbrainzngs.set_useragent(*MB_USER_AGENT)

    m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
    user_id = os.environ["TASTE_USER_ID"]

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
    from fastapi import HTTPException

    print(f"--- DISCOVERY START: {payload.get('user_id')} ---")
    user_id = os.environ["TASTE_USER_ID"]

    try:
        verified, drafted_message = await _run_discovery(user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"missions": verified, "drafted_message": drafted_message}


# --- FEEDBACK ENDPOINT ---

@app.function(secrets=secrets, timeout=30)
@modal.fastapi_endpoint(method="POST")
async def feedback(payload: dict):
    from mem0 import MemoryClient
    from fastapi import HTTPException

    artist = payload.get("artist")
    album = payload.get("album")
    rating = payload.get("rating")
    user_id = payload.get("user_id")

    if not all([artist, album, rating]):
        raise HTTPException(status_code=400, detail="Missing required fields: artist, album, rating")
    if rating not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="rating must be 'like' or 'dislike'")

    try:
        m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
        label = "Liked" if rating == "like" else "Disliked"
        text = f"{label}: {artist} - {album}"
        m0.add(text, user_id=user_id or os.environ["TASTE_USER_ID"])
        print(f"Feedback recorded: {text}")
    except Exception as e:
        print(f"Feedback Mem0 Error: {e}")

    return {"status": "ok"}


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

    taste_context = ""
    try:
        from mem0 import MemoryClient
        m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
        raw_search = m0.search(query="jazz taste profile", filters={"user_id": os.environ["TASTE_USER_ID"]}, limit=10)
        results = raw_search if isinstance(raw_search, list) else raw_search.get('results', [])
        raw = "\n".join([r["text"] for r in results]) if results else ""
        taste_context = raw[:2000]
    except:
        pass

    try:
        res = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.6",
            messages=[{"role": "user", "content": f"Taste context: {taste_context}\nCurate these 8/10+: {json.dumps(new_articles[:3])}. JSON: selected_articles[url, title, source, rating, summary]"}]
        )
        return extract_json(res.choices[0].message.content).get("selected_articles", [])
    except: return []


# --- TASTE SYNC CRON (every 6 hours) ---

@app.function(secrets=secrets, schedule=modal.Cron("0 */6 * * *"), timeout=600)
async def sync_taste():
    from mem0 import MemoryClient
    from ytmusicapi import YTMusic
    import pylast

    print("--- TASTE SYNC START ---")

    api_key = os.environ["LASTFM_API_KEY"]
    api_secret = os.environ["LASTFM_API_SECRET"]
    lastfm_user = os.environ["LASTFM_USER"]
    taste_user_id = os.environ["TASTE_USER_ID"]

    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)
    user = network.get_user(lastfm_user)

    top_artists = user.get_top_artists(limit=200)
    all_artists = {a.item.name for a in top_artists}

    print(f"Found {len(all_artists)} unique artists across all scrobbles")

    # Fetch liked YTMusic albums
    liked_albums = []
    try:
        headers_raw_str = os.environ.get("YT_COOKIE_HEADERS")
        if headers_raw_str:
            headers_raw = json.loads(headers_raw_str)
            YTMusic.setup("headers_auth.json", headers_raw=headers_raw)
            ytm = YTMusic("headers_auth.json")
            library_albums = ytm.get_library_albums(limit=100)
            print(f"Found {len(library_albums)} liked YTMusic albums")
            for album in library_albums:
                artists = album.get("artists", [])
                artist_name = artists[0]["name"] if artists else "Unknown Artist"
                title = album.get("title", "Unknown Album")
                liked_albums.append({"artist": artist_name, "title": title})
                if artist_name != "Unknown Artist":
                    all_artists.add(artist_name)
    except Exception as e:
        print(f"YTMusic library fetch failed: {e}")

    m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
    raw = m0.get_all(filters={"user_id": taste_user_id})
    existing = raw if isinstance(raw, list) else raw.get('results', [])
    existing_artists = set()
    existing_liked = set()
    for mem in existing:
        text = mem.get("text", "")
        if text.startswith("Artist: "):
            existing_artists.add(text.split("\n")[0].replace("Artist: ", "").strip())
        elif text.startswith("Sent:"):
            try:
                sent_artist = text.replace("Sent: ", "", 1).split(" by ", 1)[1].strip()
                if "(" in sent_artist:
                    sent_artist = sent_artist[:sent_artist.rfind("(")].strip()
                existing_artists.add(sent_artist)
            except:
                pass
        elif text.startswith("Liked: "):
            existing_liked.add(text)

    for album in liked_albums:
        like_text = f"Liked: {album['artist']} - {album['title']}"
        if like_text not in existing_liked:
            try:
                m0.add(like_text, user_id=taste_user_id)
                print(f"Recorded new YTMusic liked album: {like_text}")
            except Exception as e:
                print(f"Failed to record liked album {like_text}: {e}")

    for artist_name in sorted(all_artists):
        if artist_name in existing_artists:
            print(f"Skipping {artist_name} (already ingested)")
            continue
        enrich_taste_profile.remote(artist_name)

    print("--- TASTE SYNC COMPLETE ---")


# --- DAILY DISCOVER CRON (12:00 UTC) ---

@app.function(secrets=secrets, schedule=modal.Cron("0 12 * * *"), timeout=300)
async def daily_discover():
    import httpx

    print("--- DAILY DISCOVER CRON START ---")

    user_id = os.environ["TASTE_USER_ID"]

    try:
        verified, drafted_message = await _run_discovery(user_id)
    except Exception as e:
        print(f"Discovery pipeline failed: {e}")
        verified, drafted_message = [], "Discovery pipeline failed today."

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not set, skipping webhook post")
        return

    try:
        async with httpx.AsyncClient(timeout=30.0) as hx:
            await hx.post(webhook_url, json={"content": drafted_message})
            for m in verified:
                embed_payload = {
                    "title": f"🎼 {m['album']}",
                    "description": f"**{m['new_artist']}**",
                    "color": 3447003,
                    "fields": [
                        {"name": "🤝 Connection", "value": m['connection'], "inline": False}
                    ]
                }
                if m.get("personnel"):
                    personnel = m['personnel']
                    if isinstance(personnel, list):
                        embed_payload["fields"].append({"name": "🎹 Personnel", "value": ", ".join(personnel), "inline": False})
                    else:
                        embed_payload["fields"].append({"name": "🎹 Personnel", "value": personnel, "inline": False})
                embed_payload["fields"].append({"name": "🎧 Listen", "value": f"[YouTube Music]({m['ytm_link']})", "inline": False})

                components = [{
                    "type": 1,
                    "components": [
                        {"type": 2, "style": 3, "custom_id": f"like:{m['new_artist']}:{m['album']}", "emoji": {"name": "👍"}},
                        {"type": 2, "style": 4, "custom_id": f"dislike:{m['new_artist']}:{m['album']}", "emoji": {"name": "👎"}}
                    ]
                }]
                await hx.post(webhook_url, json={"embeds": [embed_payload], "components": components})
    except Exception as e:
        print(f"Webhook POST failed: {e}")

    print("--- DAILY DISCOVER CRON COMPLETE ---")


# --- DAILY PLAYLIST CRON (11:00 UTC) ---

@app.function(secrets=secrets, schedule=modal.Cron("0 11 * * *"), timeout=600)
async def create_daily_playlist():
    import httpx
    from openai import OpenAI
    from mem0 import MemoryClient
    from ytmusicapi import YTMusic
    import json

    print("--- DAILY PLAYLIST CRON START ---")

    user_id = os.environ["TASTE_USER_ID"]

    # 1. Query Mem0 for taste entries
    try:
        m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
        raw = m0.get_all(filters={"user_id": user_id})
        all_memories = raw if isinstance(raw, list) else raw.get('results', [])
    except Exception as e:
        print(f"Mem0 query failed: {e}")
        return

    taste_entries = []
    for mem in all_memories:
        text = mem.get("text", "")
        if text.startswith("Artist: ") or text.startswith("Liked:") or text.startswith("Disliked:"):
            taste_entries.append(text)

    taste_context = "\n".join(taste_entries[:20]) if taste_entries else "Focus on classic hard-bop and post-bop jazz."
    print(f"Taste context: {len(taste_entries)} entries")

    # 2. Ask Sonnet for track suggestions
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])

    sonnet_prompt = (
        "You are a jazz historian and DJ. Based on the user's taste profile below, "
        "recommend 10-15 specific tracks (song + artist) that connect to their taste "
        "through shared personnel, record label, era, or style. "
        "Include a brief connection note for each track. "
        "Do NOT recommend tracks already mentioned in the taste profile."
        f"\n\nTaste Profile:\n{taste_context[:3000]}"
        "\n\nJSON Output: tracks[artist, title, connection]"
    )

    try:
        res = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.6",
            messages=[{"role": "user", "content": sonnet_prompt}]
        )
        parsed = extract_json(res.choices[0].message.content)
        if not parsed or "tracks" not in parsed:
            raise Exception("No tracks in LLM response")
        suggested_tracks = parsed["tracks"]
        print(f"LLM suggested {len(suggested_tracks)} tracks")
    except Exception as e:
        print(f"LLM track suggestion failed: {e}")
        return

    # 3. Search YTMusic for videoIds
    ytm = None
    auth_failed = False
    try:
        headers_raw_str = os.environ.get("YT_COOKIE_HEADERS")
        if not headers_raw_str:
            raise Exception("YT_COOKIE_HEADERS not set")
        headers_raw = json.loads(headers_raw_str)
        YTMusic.setup("headers_auth.json", headers_raw=headers_raw)
        ytm = YTMusic("headers_auth.json")
    except Exception as e:
        print(f"YTMusic auth failed: {e}")
        auth_failed = True

    found_tracks = []
    for t in suggested_tracks:
        try:
            query = f"{t['artist']} {t['title']}"
            search_results = ytm.search(query, filter="songs") if ytm else None
            if search_results and len(search_results) > 0:
                video_id = search_results[0].get("videoId")
                if video_id:
                    found_tracks.append({
                        "artist": t["artist"],
                        "title": t["title"],
                        "videoId": video_id,
                        "connection": t.get("connection", "")
                    })
        except Exception as e:
            print(f"YTMusic search failed for {t.get('artist', '?')} - {t.get('title', '?')}: {e}")

    print(f"Found {len(found_tracks)}/{len(suggested_tracks)} tracks on YTMusic")

    # 4. If auth failed, log and exit
    if auth_failed or not ytm:
        print("Auth failed — tracks that would have been added:")
        for t in found_tracks:
            print(f"  {t['artist']} - {t['title']} ({t['videoId']})")
        print("--- DAILY PLAYLIST CRON COMPLETE (auth failed, skipped playlist creation) ---")
        return

    if not found_tracks:
        print("No tracks found on YTMusic, skipping playlist creation")
        print("--- DAILY PLAYLIST CRON COMPLETE ---")
        return

    # 5. Create playlist
    today_str = datetime.now().strftime("%Y-%m-%d")
    playlist_name = f"Daily Jazz Discoveries {today_str}"

    try:
        playlist_id = ytm.create_playlist(
            playlist_name,
            description=f"Daily jazz discoveries curated from your taste profile — {today_str}"
        )
        print(f"Created playlist: {playlist_name} ({playlist_id})")
    except Exception as e:
        print(f"Playlist creation failed: {e}")
        return

    # 6. Add tracks to playlist
    video_ids = [t["videoId"] for t in found_tracks]
    try:
        ytm.add_playlist_items(playlist_id, video_ids)
        print(f"Added {len(video_ids)} tracks to playlist")
    except Exception as e:
        print(f"Adding tracks to playlist failed: {e}")

    playlist_url = f"https://music.youtube.com/playlist?list={playlist_id}"

    # 7. Post to Discord webhook
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        try:
            track_lines = "\n".join(
                f"• **{t['artist']}** — *{t['title']}*  _{t['connection']}_"
                for t in found_tracks
            )
            message = (
                f"## 🎵 Daily Jazz Discoveries — {today_str}\n\n"
                f"**Playlist:** {playlist_url}\n\n"
                f"{track_lines}"
            )
            async with httpx.AsyncClient(timeout=30.0) as hx:
                await hx.post(webhook_url, json={"content": message[:1900]})
        except Exception as e:
            print(f"Discord webhook post failed: {e}")
    else:
        print("DISCORD_WEBHOOK_URL not set, skipping webhook post")

    print("--- DAILY PLAYLIST CRON COMPLETE ---")


# --- WEEKLY HERALD CRON (Sunday 10:00 UTC) ---

@app.function(secrets=secrets, schedule=modal.Cron("0 10 * * 0"), timeout=300)
async def weekly_herald():
    import httpx
    from openai import OpenAI
    import feedparser
    from playwright.async_api import async_playwright

    print("--- WEEKLY HERALD CRON START ---")

    FEEDS = {"The Gig": "https://natechinen.substack.com/feed", "DownBeat": "https://downbeat.com/site/rss"}
    new_articles = []

    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                new_articles.append({"source": source, "title": entry.title, "link": entry.link})
        except:
            pass

    curated = []
    if new_articles:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            for art in new_articles[:3]:
                page = await browser.new_page()
                try:
                    await page.goto(art['link'], timeout=15000)
                    art['full_text'] = (await page.evaluate("document.body.innerText"))[:3000]
                except:
                    art['full_text'] = ""
                await page.close()
            await browser.close()

        taste_context = ""
        try:
            from mem0 import MemoryClient
            m0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
            raw_search = m0.search(query="jazz taste profile", filters={"user_id": os.environ["TASTE_USER_ID"]}, limit=10)
            results = raw_search if isinstance(raw_search, list) else raw_search.get('results', [])
            raw = "\n".join([r["text"] for r in results]) if results else ""
            taste_context = raw[:2000]
        except:
            pass

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
        try:
            res = client.chat.completions.create(
                model="anthropic/claude-sonnet-4.6",
                messages=[{"role": "user", "content": f"Taste context: {taste_context}\nCurate these 8/10+: {json.dumps(new_articles[:3])}. JSON: selected_articles[url, title, source, rating, summary]"}]
            )
            result = extract_json(res.choices[0].message.content)
            if result:
                curated = result.get("selected_articles", [])
        except:
            pass

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not set, skipping webhook post")
        return

    try:
        async with httpx.AsyncClient(timeout=30.0) as hx:
            if not curated:
                await hx.post(webhook_url, json={"content": "🗞️ No new high-signal dispatches found this week."})
            else:
                await hx.post(webhook_url, json={"content": "## 🎺 The Jazz News Herald (Weekly Edition)"})
                for art in curated:
                    embed_payload = {
                        "title": f"🗞️ {art['title']}",
                        "url": art['link'],
                        "description": art['summary'],
                        "color": 15105570,
                        "fields": [{"name": "📍 Source", "value": art['source'], "inline": True}]
                    }
                    await hx.post(webhook_url, json={"embeds": [embed_payload]})
    except Exception as e:
        print(f"Webhook POST failed: {e}")

    print("--- WEEKLY HERALD CRON COMPLETE ---")
