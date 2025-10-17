# env_helper.py
"""
Environment variable loader with UTF-8 BOM protection.
Ensures .env is loaded correctly and strips any BOM characters
from variable names (e.g. \ufeffDISCORD_TOKEN).
"""

import os
from dotenv import load_dotenv


def load_env():
    """Load environment variables from .env and fix BOM issues."""
    load_dotenv()

    # Clean BOM (e.g. \ufeffDISCORD_TOKEN)
    for key in list(os.environ.keys()):
        clean_key = key.lstrip("\ufeff")
        if clean_key != key:
            os.environ[clean_key] = os.environ.pop(key)


# Auto-run when imported
load_env()