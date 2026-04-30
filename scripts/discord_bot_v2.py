import discord
from discord import app_commands
from discord.ext import tasks
import os
import json
import asyncio
import pylast
import requests
from datetime import time, datetime
from dotenv import load_dotenv
from ytmusicapi import YTMusic

# Import our custom modules
from curator_v3 import get_discovery_missions, get_platform_links
from herald_db import init_db, mark_article_processed, prune_old_articles
from herald_scout import scout_new_articles
from herald_curator import curate_articles

# Load credentials
load_dotenv(dotenv_path="/home/ownash/blue-note-automator/.env")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SETTINGS_FILE = "/home/ownash/blue-note-automator/bot_settings.json"
BLACKLIST_FILE = "/home/ownash/blue-note-automator/blacklist.json"
OAUTH_PATH = "/home/ownash/blue-note-automator/oauth.json"

# Last.fm Setup
API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

# YTM Setup
def get_ytm_client():
    if not os.path.exists(OAUTH_PATH):
        print(f"CRITICAL: {OAUTH_PATH} not found.")
        return None
    try:
        return YTMusic(OAUTH_PATH)
    except Exception as e:
        print(f"ERROR initializing YTMusic: {e}")
        return None

ytm = get_ytm_client()

def save_settings(channel_id):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"channel_id": channel_id}, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f).get("channel_id")
        except: return None
    return None

def update_blacklist(artist=None, album=None):
    if not os.path.exists(BLACKLIST_FILE):
        data = {"artists": [], "albums": []}
    else:
        with open(BLACKLIST_FILE, "r") as f:
            data = json.load(f)
    
    if artist and artist not in data["artists"]:
        data["artists"].append(artist)
    if album and album not in data["albums"]:
        data["albums"].append(album)
        
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

class DiscoveryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def extract_info(self, interaction: discord.Interaction):
        if not interaction.message or not interaction.message.embeds:
            return None, None
        
        embed = interaction.message.embeds[0]
        album = embed.title.replace("🎼 ", "").strip()
        artist = embed.description.split("\n")[0].replace("**", "").strip()
        return artist, album

    @discord.ui.button(label="Save to Library", style=discord.ButtonStyle.green, custom_id="save_btn")
    async def save_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        artist, album = self.extract_info(interaction)
        if not artist or not album:
            return await interaction.response.send_message("❌ Could not extract album info.", ephemeral=True)

        print(f"INTERACTION: Save click for {album}")
        await interaction.response.send_message(f"⌛ Adding **{album}** to your YTM Library...", ephemeral=True)
        
        if not ytm:
            await interaction.followup.send("❌ YTM client not initialized.", ephemeral=True)
            return

        def ytm_save():
            search_results = ytm.search(f"{artist} {album}", filter="albums")
            if not search_results:
                return False, "Album not found on YTM."
            
            album_id = search_results[0]['browseId']
            album_details = ytm.get_album(album_id)
            track_ids = [t['videoId'] for t in album_details['tracks'] if t.get('videoId')]
            
            if not track_ids:
                return False, "No tracks found in album."
            
            for tid in track_ids:
                ytm.edit_song_library_status(tid)
            
            return True, None

        loop = asyncio.get_event_loop()
        success, error = await loop.run_in_executor(None, ytm_save)
        
        if success:
            await interaction.followup.send(f"✅ **{album}** added to your YouTube Music library!", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed to save: {error}", ephemeral=True)

    @discord.ui.button(label="Love", style=discord.ButtonStyle.blurple, custom_id="love_btn")
    async def love_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        artist, album = self.extract_info(interaction)
        if not artist or not album:
            return await interaction.response.send_message("❌ Could not extract artist info.", ephemeral=True)

        print(f"INTERACTION: Love click for {artist}")
        await interaction.response.send_message(f"❤️ Loving **{artist}** on YTM...", ephemeral=True)
        
        if not ytm:
            await interaction.followup.send("❌ YTM client not initialized.", ephemeral=True)
            return

        def ytm_love():
            search_results = ytm.search(f"{artist} {album}", filter="songs")
            if search_results:
                ytm.rate_song(search_results[0]['videoId'], 'LIKE')
                return True
            return False

        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, ytm_love)
        
        if success:
            await interaction.followup.send(f"❤️ Recorded your preference for **{artist}**. I'll keep it in mind!", ephemeral=True)
        else:
            await interaction.followup.send(f"⚠️ Couldn't find a matching song to 'Love' on YTM, but I've noted the artist!", ephemeral=True)

    @discord.ui.button(label="Not For Me", style=discord.ButtonStyle.gray, custom_id="ignore_btn")
    async def ignore_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        artist, album = self.extract_info(interaction)
        print(f"INTERACTION: Blacklist click for {artist}")
        update_blacklist(artist=artist, album=album)
        await interaction.response.send_message(f"🚫 Got it. I will avoid **{artist}** and **{album}** in the future.", ephemeral=True)

class JazzBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.active_channel_id = load_settings()
        init_db()
        self.add_commands()

    def add_commands(self):
        @self.tree.command(name="setup", description="Lock daily discoveries to this channel")
        async def setup(interaction: discord.Interaction):
            self.active_channel_id = interaction.channel.id
            save_settings(interaction.channel.id)
            await interaction.response.send_message(f"✅ **Blue Note Automator** is now locked to **#{interaction.channel.name}**!", ephemeral=True)

        @self.tree.command(name="discover", description="Get 5 fresh jazz discoveries right now")
        async def discover(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            await self.run_discovery_quintet(interaction.channel)
            await interaction.followup.send("🎷 Discovery Quintet delivered!", ephemeral=True)

        @self.tree.command(name="herald", description="Scout and curate the latest high-signal jazz news")
        async def herald(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            await self.run_herald_digest(interaction.channel)
            await interaction.followup.send("🎺 Herald digest delivered!", ephemeral=True)

    async def setup_hook(self):
        self.add_view(DiscoveryView())
        self.daily_discovery_loop.start()
        self.daily_herald_loop.start()

    async def on_ready(self):
        print(f"\n--- BLUE NOTE AUTOMATOR READY (2026 CLOUD RUN MODE) ---")
        print(f"User: {self.user} (ID: {self.user.id})")
        await self.tree.sync()
        if self.active_channel_id:
            print(f"Target Discovery Channel: {self.active_channel_id}")
        print("---------------------------------\n")

    @tasks.loop(time=time(hour=9, minute=0))
    async def daily_discovery_loop(self):
        if not self.active_channel_id: return
        channel = self.get_channel(self.active_channel_id)
        if channel:
            await self.run_discovery_quintet(channel)

    @tasks.loop(time=time(hour=8, minute=0))
    async def daily_herald_loop(self):
        if not self.active_channel_id: return
        channel = self.get_channel(self.active_channel_id)
        if channel:
            await self.run_herald_digest(channel)
            prune_old_articles()

    async def run_herald_digest(self, channel):
        try:
            new_articles = scout_new_articles()
            if not new_articles: return
            await channel.send("🗞️ **Scanning the latest Jazz dispatches...**")
            curated = await curate_articles(new_articles)
            if not curated:
                for a in new_articles: mark_article_processed(a['source'], a['title'], a['link'])
                return
            await channel.send("## 🎺 The Jazz News Herald")
            for art in curated:
                embed = discord.Embed(title=f"🗞️ {art['title']}", url=art['url'], description=art['summary'], color=15105570)
                embed.add_field(name="📍 Source", value=art['source'], inline=True)
                embed.add_field(name="⭐ Relevance", value=f"{art['rating']}/10", inline=True)
                await channel.send(embed=embed)
                mark_article_processed(art['source'], art['title'], art['url'])
        except Exception as e:
            print(f"ERROR HERALD: {e}")

    async def run_discovery_quintet(self, channel):
        try:
            missions, drafted_message = get_discovery_missions(count=5)
            # Post the Narrative Message from Opus
            await channel.send(drafted_message)
            
            # Post Technical Breakdown Embeds
            for m in missions:
                embed = discord.Embed(title=f"🎼 {m['album']}", description=f"**{m['new_artist']}**", color=3447003)
                embed.add_field(name="🤝 The Connection", value=f"**{m['seed_artist']}**: {m['connection']}", inline=False)
                embed.add_field(name="🎹 Personnel", value=", ".join(m['personnel']), inline=False)
                embed.add_field(name="🎧 Listen", value=f"[YouTube Music]({m['ytm_link']})", inline=False)
                await channel.send(embed=embed, view=DiscoveryView())
        except Exception as e:
            print(f"ERROR: {e}")
            await channel.send(f"❌ Error generating discovery: {e}")

if __name__ == "__main__":
    bot = JazzBot()
    bot.run(TOKEN)
