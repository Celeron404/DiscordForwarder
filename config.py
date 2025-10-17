﻿# config.py
import os
import env_helper
import discord

# -----------------------
# Bot configuration
# -----------------------
PREFIX = "?fw "  # Command prefix used to trigger bot commands
DATA_FILE = "data.json"  # Path to JSON file for storing keywords, sources, etc.

# Loading Discord token from .env
env_helper.load_env()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("Error: please set the DISCORD_TOKEN environment variable in .env")

# -----------------------
# Discord intents
# -----------------------
# Message content intent is required to read messages
# Members intent is required for DM subscriptions

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True