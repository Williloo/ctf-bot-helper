#!/usr/bin/env python3
"""
CTF Bot Helper - Main Entry Point

A Discord bot that integrates with Google Docs to manage CTF meeting agendas.
"""
import sys
import os
from src.ctf_bot.config import DISCORD_TOKEN
from src.ctf_bot.discord_bot import create_bot

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the CTF bot."""
    bot = create_bot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
