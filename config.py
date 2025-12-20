# config.py
import os
import env_helper
import discord

# -----------------------
# Bot configuration
# -----------------------
PREFIX = "?fw "  # Command prefix used to trigger bot commands
DATA_FILE = "data.json"  # Path to JSON file for storing keywords, sources, etc.
SEPARATOR_MODE = True  # If True, messages containing multiple lines will be split into separate lines by the bot and each line will be processed separately.

# Loading Discord token from .env
env_helper.load_env()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("Error: please set the DISCORD_TOKEN environment variable in .env")

# -----------------------
# Discord intents
# -----------------------
# Message content intent is required to read messages

INTENTS = discord.Intents.default()
INTENTS.message_content = True