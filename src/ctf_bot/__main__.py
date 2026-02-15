"""Main entry point for the CTF bot when run as a module."""
from .config import DISCORD_TOKEN
from .discord_bot import create_bot


def main():
    """Main entry point for the CTF bot."""
    bot = create_bot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()