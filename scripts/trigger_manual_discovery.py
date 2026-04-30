
import asyncio
import os
import discord
from discord_bot_v2 import JazzBot, load_settings
from dotenv import load_dotenv

load_dotenv()

async def trigger_manual_discovery():
    bot = JazzBot()
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        channel_id = load_settings()
        if channel_id:
            channel = bot.get_channel(channel_id)
            if channel:
                print(f"Triggering discovery for channel {channel_id}")
                await bot.run_discovery_quintet(channel)
                print("Discovery sent!")
            else:
                print(f"Could not find channel {channel_id}")
        else:
            print("No channel_id found in settings.")
        await bot.close()

    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(trigger_manual_discovery())
