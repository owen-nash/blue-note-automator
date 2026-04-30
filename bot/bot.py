import discord
from discord import app_commands
import os
import json
import httpx
import asyncio
import pylast
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MODAL_DISCOVER_URL = os.getenv("MODAL_DISCOVER_URL")
MODAL_HERALD_URL = os.getenv("MODAL_HERALD_URL")

# --- BOT SETUP ---

class JazzBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        print("Syncing command tree...")
        await self.tree.sync()

    async def on_ready(self):
        print(f"--- 🎷 BLUE NOTE AUTOMATOR ONLINE ---")
        print(f"Logged in as: {self.user}")
        print(f"Time: {datetime.now()}")

    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return
        custom_id = interaction.data.get("custom_id", "")
        if custom_id.startswith("like|") or custom_id.startswith("dislike|"):
            parts = custom_id.split("|", 2)
            if len(parts) != 3:
                return
            rating, artist, album = parts
            if interaction.response.is_done():
                return
            await interaction.response.defer()
            feedback_url = MODAL_DISCOVER_URL.replace("/discover", "/feedback")
            payload = {"artist": artist, "album": album, "rating": rating, "user_id": str(interaction.user.id)}
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(feedback_url, json=payload)
            except Exception as e:
                print(f"Webhook Feedback Error: {e}")

bot = JazzBot()

# --- FEEDBACK BUTTONS ---

class FeedbackView(discord.ui.View):
    def __init__(self, artist: str, album: str):
        super().__init__(timeout=None)
        self.artist = artist
        self.album = album
        like_btn = discord.ui.Button(style=discord.ButtonStyle.success, emoji="👍", custom_id=f"like|{artist}|{album}")
        like_btn.callback = self.like_callback
        self.add_item(like_btn)
        dislike_btn = discord.ui.Button(style=discord.ButtonStyle.danger, emoji="👎", custom_id=f"dislike|{artist}|{album}")
        dislike_btn.callback = self.dislike_callback
        self.add_item(dislike_btn)

    async def _send_feedback(self, interaction: discord.Interaction, rating: str):
        await interaction.response.defer()
        feedback_url = MODAL_DISCOVER_URL.replace("/discover", "/feedback")
        payload = {"artist": self.artist, "album": self.album, "rating": rating, "user_id": str(interaction.user.id)}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(feedback_url, json=payload)
        except Exception as e:
            print(f"Feedback Error: {e}")

    async def like_callback(self, interaction: discord.Interaction):
        await self._send_feedback(interaction, "like")

    async def dislike_callback(self, interaction: discord.Interaction):
        await self._send_feedback(interaction, "dislike")

# --- DISCOVERY COMMAND ---

@bot.tree.command(name="discover", description="Get 5 fresh jazz discoveries (Async)")
async def discover_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    print(f"TRIGGER: /discover by {interaction.user}")
    
    try:
        payload = {
            "user_id": os.getenv("TASTE_USER_ID"),
            "artists": ["Miles Davis", "John Coltrane", "Billy Hart", "Elvin Jones", "Tony Williams"]
        }
        
        # Use httpx.AsyncClient to avoid blocking the heartbeat
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(MODAL_DISCOVER_URL, json=payload)
            
        if res.status_code != 200:
            return await interaction.followup.send(f"❌ Intelligence Layer Error ({res.status_code}): {res.text[:200]}")
            
        data = res.json()
        
        # 1. Post Narrative
        await interaction.followup.send(data["drafted_message"])
        
        # 2. Post technical embeds
        for m in data["missions"]:
            embed = discord.Embed(title=f"🎼 {m['album']}", description=f"**{m['new_artist']}**", color=3447003)
            embed.add_field(name="🤝 Connection", value=m['connection'], inline=False)
            if m.get("personnel"):
                embed.add_field(name="🎹 Personnel", value=", ".join(m['personnel']), inline=False)
            embed.add_field(name="🎧 Listen", value=f"[YouTube Music]({m['ytm_link']})", inline=False)
            await interaction.channel.send(embed=embed)
            view = FeedbackView(m['new_artist'], m['album'])
            await interaction.channel.send(view=view)
            
    except Exception as e:
        print(f"ERROR /discover: {e}")
        await interaction.followup.send(f"❌ Critical Error: {str(e)}")

# --- HERALD COMMAND ---

@bot.tree.command(name="herald", description="Scout and curate the latest jazz news (Async)")
async def herald_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    print(f"TRIGGER: /herald by {interaction.user}")
    
    try:
        payload = {"processed_links": [], "taste_profile": ["Bill Stewart", "Brian Blade"]}
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            res = await client.post(MODAL_HERALD_URL, json=payload)
            
        if res.status_code != 200:
            return await interaction.followup.send(f"❌ Herald Service Error: {res.text[:200]}")
            
        articles = res.json()
        if not articles:
            return await interaction.followup.send("🗞️ No new high-signal dispatches found today.")

        await interaction.followup.send("## 🎺 The Jazz News Herald")
        for art in articles:
            embed = discord.Embed(title=f"🗞️ {art['title']}", url=art['link'], description=art['summary'], color=15105570)
            embed.add_field(name="📍 Source", value=art['source'], inline=True)
            await interaction.channel.send(embed=embed)

    except Exception as e:
        print(f"ERROR /herald: {e}")
        await interaction.followup.send(f"❌ Critical Error: {str(e)}")

if __name__ == "__main__":
    bot.run(TOKEN)
