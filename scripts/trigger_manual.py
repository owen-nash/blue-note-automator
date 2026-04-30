import asyncio
import discord
import os
from dotenv import load_dotenv

# We can't easily 'send' a command to a running bot process from outside without a socket,
# but we can run a one-off script that uses the bot logic to send the message.
# Or just wait for the user to type !discover in discord.
# Let's just run the discovery function once manually from a script to get the message out.

from blue_note_automator.curator_v3 import get_discovery_missions, get_platform_links
import requests

load_dotenv(dotenv_path="/home/ownash/blue-note-automator/.env")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Actually, the webhook doesn't support the buttons.
# The user needs to see the bot message.
# I'll just tell the user to type !discover in their Discord channel.
