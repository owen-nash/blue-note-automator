import discord
from discord import app_commands
import os
import httpx
import asyncio
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
            return await super().on_interaction(interaction)
        custom_id = interaction.data.get("custom_id", "")
        if not (custom_id.startswith("like:") or custom_id.startswith("dislike:")):
            return await super().on_interaction(interaction)
        parts = custom_id.split(":", 2)
        if len(parts) != 3:
            return await interaction.response.send_message("Invalid feedback format.", ephemeral=True)
        rating, artist, album = parts
        if not MODAL_DISCOVER_URL:
            return await interaction.response.send_message("Feedback service unavailable.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        feedback_url = MODAL_DISCOVER_URL.replace("/discover", "/feedback")
        payload = {"artist": artist, "album": album, "rating": rating, "user_id": str(interaction.user.id)}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(feedback_url, json=payload)
            await interaction.followup.send("Feedback recorded!", ephemeral=True)
        except Exception as e:
            print(f"Webhook Feedback Error: {e}")
            await interaction.followup.send("Failed to record feedback.", ephemeral=True)

        emoji = "✅" if rating == "like" else "❌"
        await interaction.message.edit(content=f"{emoji} **{album}** by {artist}", view=None)

bot = JazzBot()

# --- FEEDBACK BUTTONS ---

class FeedbackView(discord.ui.View):
    def __init__(self, artist: str, album: str):
        super().__init__(timeout=None)
        self.artist = artist
        self.album = album
        like_btn = discord.ui.Button(style=discord.ButtonStyle.success, emoji="👍", custom_id=f"like:{artist}:{album}")
        self.add_item(like_btn)
        dislike_btn = discord.ui.Button(style=discord.ButtonStyle.danger, emoji="👎", custom_id=f"dislike:{artist}:{album}")
        self.add_item(dislike_btn)

# --- DISCOVERY COMMAND ---

@bot.tree.command(name="discover", description="Get 5 fresh jazz discoveries (Async)")
async def discover_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    print(f"TRIGGER: /discover by {interaction.user}")
    
    try:
        payload = {
            "user_id": os.getenv("TASTE_USER_ID"),
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(MODAL_DISCOVER_URL, json=payload)
            
        if res.status_code != 200:
            return await interaction.followup.send(f"❌ Intelligence Layer Error ({res.status_code}): {res.text[:200]}")
            
        data = res.json()
        
        if not data.get("missions"):
            return await interaction.followup.send("🎵 No discoveries found this time.")

        count = len(data["missions"])
        await interaction.followup.send(f"🎵 **{count} new {'discovery' if count == 1 else 'discoveries'}** based on your taste profile:")

        for m in data["missions"]:
            embed = discord.Embed(title=f"🎼 {m['album']}", description=f"**{m['new_artist']}**", color=3447003)
            embed.add_field(name="🤝 Connection", value=m['connection'][:150], inline=False)
            if m.get("personnel"):
                personnel = m['personnel']
                if isinstance(personnel, list):
                    val = ", ".join(personnel)
                else:
                    val = personnel
                if len(val) > 800:
                    val = val[:797] + "..."
                embed.add_field(name="🎹 Personnel", value=val, inline=False)
            ytm = m.get("ytm_link", "")
            embed.add_field(name="🎧 Listen", value=f"[YouTube Music]({ytm})" if ytm else "N/A", inline=False)

            total = len(embed.title or "") + len(embed.description or "")
            for f in embed.fields:
                total += len(f.name) + len(f.value)
            if total > 1950:
                print(f"WARNING: embed for {m['album']} is ~{total} chars, truncating")
                for f in embed.fields:
                    if len(f.value) > 100:
                        f.value = f.value[:97] + "..."

            view = FeedbackView(m['new_artist'], m['album'])
            try:
                await interaction.channel.send(embed=embed, view=view)
            except discord.HTTPException:
                await interaction.followup.send(f"🎼 **{m['album']}** by **{m['new_artist']}**... (truncated)", ephemeral=True)
            
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
