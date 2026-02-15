"""Tests for Discord bot functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ctf_bot.discord_bot import create_bot


class TestDiscordBot:
    """Test cases for Discord bot functionality."""

    @pytest.fixture
    def bot(self):
        """Create a bot instance for testing."""
        return create_bot()

    @pytest.mark.asyncio
    async def test_add_agenda_command_success(self, bot):
        """Test successful add-agenda command."""
        ctx = MagicMock()
        ctx.reply = AsyncMock()
        ctx.trigger_typing = AsyncMock()
        
        with patch('asyncio.to_thread') as mock_thread:
            mock_thread.return_value = None
            
            # Get the command
            cmd = bot.get_command('add-agenda')
            await cmd(ctx, item="Test agenda item")
            
            ctx.reply.assert_called_with("✅ Added to 'meeting draft' agenda table.")

    @pytest.mark.asyncio
    async def test_add_agenda_command_empty_item(self, bot):
        """Test add-agenda command with empty item."""
        ctx = MagicMock()
        ctx.reply = AsyncMock()
        
        # Get the command
        cmd = bot.get_command('add-agenda')
        await cmd(ctx, item="   ")
        
        ctx.reply.assert_called_with("Usage: `!add-agenda <text>`")

    @pytest.mark.asyncio
    async def test_add_agenda_command_too_long(self, bot):
        """Test add-agenda command with item too long."""
        ctx = MagicMock()
        ctx.reply = AsyncMock()
        
        long_item = "x" * 501  # Over 500 character limit
        
        # Get the command
        cmd = bot.get_command('add-agenda')
        await cmd(ctx, item=long_item)
        
        ctx.reply.assert_called_with("Agenda item too long (max 500 chars).")

    @pytest.mark.asyncio
    async def test_add_agenda_command_exception(self, bot):
        """Test add-agenda command with exception."""
        ctx = MagicMock()
        ctx.reply = AsyncMock()
        ctx.trigger_typing = AsyncMock()
        
        with patch('asyncio.to_thread') as mock_thread:
            mock_thread.side_effect = Exception("Test error")
            
            # Get the command
            cmd = bot.get_command('add-agenda')
            await cmd(ctx, item="Test agenda item")
            
            ctx.reply.assert_called_with("Failed to add agenda item: `Test error`")