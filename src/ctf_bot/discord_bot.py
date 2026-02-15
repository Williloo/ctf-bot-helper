"""Discord bot integration for CTF bot."""
import asyncio

import discord
from discord.ext import commands

from .config import TARGET_DOC_NAME
from .integrations.google_docs import GoogleDocsManager


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (id={bot.user.id})")
    
    @bot.command(name="add-agenda")
    async def add_agenda(ctx: commands.Context, *, item: str):
        """Add an item to the meeting agenda."""
        item = item.strip()
        if not item:
            await ctx.reply("Usage: `!add-agenda <text>`")
            return
        if len(item) > 500:
            await ctx.reply("Agenda item too long (max 500 chars).")
            return

        async with ctx.channel.typing():
            # Build services (blocking work goes in a thread)
            def work():
                docs_manager = GoogleDocsManager()
                docs_manager.add_agenda_item(item)

            try:
                await asyncio.to_thread(work)
            except Exception as e:
                await ctx.reply(f"Failed to add agenda item: `{e}`")
                return

        await ctx.reply(f"✅ Added to '{TARGET_DOC_NAME}' agenda table.")
    
    @bot.command(name="create-doc")
    async def create_doc(ctx: commands.Context, *, name: str):
        """Create a new document from the template."""
        name = name.strip()
        if not name:
            await ctx.reply("Usage: `!create-doc <document name>`")
            return
        if len(name) > 100:
            await ctx.reply("Document name too long (max 100 chars).")
            return

        async with ctx.channel.typing():
            # Build services (blocking work goes in a thread)
            def work():
                docs_manager = GoogleDocsManager()
                doc_id = docs_manager.create_from_template(name)
                return doc_id

            try:
                doc_id = await asyncio.to_thread(work)
            except Exception as e:
                await ctx.reply(f"Failed to create document: `{e}`")
                return

        await ctx.reply(f"✅ Created document '{name}' from template. Document ID: {doc_id}")
    
    return bot