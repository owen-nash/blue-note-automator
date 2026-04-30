import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"--- Blue Note Command Center Online: {bot.user} ---")

@bot.command(name="prune")
async def prune_unloved(ctx):
    """
    Placeholder for Phase 2 unloved pruning logic.
    """
    await ctx.send("🔍 Scanning for unloved albums (unplayed for >6 months)...")
    # Logic to query Navidrome and LLM pitch goes here.
    await ctx.send("Coming soon: Interactive 'Keep' or 'Archive' buttons.")

@bot.command(name="sideman")
async def sideman_discovery(ctx):
    """
    Placeholder for Phase 2 sideman discovery logic.
    """
    await ctx.send("🎸 Identifying your favorite sidemen for discovery suggestions...")
    # Logic to find sideman links goes here.
    await ctx.send("Suggestion: 'Bill Stewart' features on 15 of your albums. Check out Kevin Hays' '7th Ave South'.")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN not found in .env")
