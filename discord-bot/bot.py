"""
Discord Bot - Main Application

Monitors Discord channel for trade signals and forwards to Trading Server.
Self-contained service that can run independently.
"""
import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent))

from parser import SignalParser
from trading_client import TradingServerClient
from shared.models import TradeSignal
import aiohttp

# Load environment variables
load_dotenv()

# Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0))
DISCORD_NOTIFICATION_WEBHOOK = os.getenv('DISCORD_NOTIFICATION_WEBHOOK')
TRADING_SERVER_URL = os.getenv('TRADING_SERVER_URL', 'http://localhost:8000')
TRADING_SERVER_API_KEY = os.getenv('TRADING_SERVER_API_KEY')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'discord_bot.log')

# Optional filters
ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS', '').split(',')
ALLOWED_USER_IDS = [int(uid) for uid in ALLOWED_USER_IDS if uid.strip()]
REQUIRED_ROLE_NAME = os.getenv('REQUIRED_ROLE_NAME')

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingBot(commands.Bot):
    """
    Discord bot that monitors channels for trade signals.
    """
    
    def __init__(self):
        """Initialize bot with intents and components."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize components
        self.parser = SignalParser()
        self.trading_client = TradingServerClient(
            base_url=TRADING_SERVER_URL,
            api_key=TRADING_SERVER_API_KEY
        )
        
        self.stats = {
            'messages_seen': 0,
            'signals_detected': 0,
            'signals_sent': 0,
            'signals_failed': 0
        }
    
    async def send_webhook_notification(self, title: str, description: str, color: int, fields: list = None):
        """Send notification to Discord webhook."""
        if not DISCORD_NOTIFICATION_WEBHOOK:
            return
        
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": discord.utils.utcnow().isoformat()
            }
            
            if fields:
                embed["fields"] = fields
            
            async with aiohttp.ClientSession() as session:
                await session.post(
                    DISCORD_NOTIFICATION_WEBHOOK,
                    json={"embeds": [embed]}
                )
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def setup_hook(self):
        """Called when bot is starting up."""
        logger.info("Bot is starting up...")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Bot logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Monitoring channel ID: {DISCORD_CHANNEL_ID}')
        logger.info(f'Trading Server: {TRADING_SERVER_URL}')
        
        # Check if bot can access the monitoring channel
        try:
            channel = self.get_channel(DISCORD_CHANNEL_ID)
            if channel is None:
                # Try fetching it
                channel = await self.fetch_channel(DISCORD_CHANNEL_ID)
            
            if channel:
                # Test if we can read messages
                try:
                    # Try to fetch recent messages to verify read permission
                    async for msg in channel.history(limit=1):
                        break
                    logger.info(f"✅ Successfully verified access to channel: {channel.name}")
                except discord.Forbidden:
                    logger.error(f"❌ CRITICAL: Bot cannot read messages from channel {DISCORD_CHANNEL_ID}")
                    logger.error(f"   Channel name: {channel.name}")
                    logger.error(f"   Missing permission: Read Message History")
                    logger.error(f"   ACTION REQUIRED: Add bot to channel or grant permissions")
                except Exception as e:
                    logger.error(f"❌ Error accessing channel {DISCORD_CHANNEL_ID}: {e}")
            else:
                logger.error(f"❌ CRITICAL: Cannot find channel {DISCORD_CHANNEL_ID}")
                logger.error(f"   Bot may not be in the server or channel doesn't exist")
                logger.error(f"   ACTION REQUIRED: Invite bot to server or verify channel ID")
                
        except discord.NotFound:
            logger.error(f"❌ CRITICAL: Channel {DISCORD_CHANNEL_ID} not found")
            logger.error(f"   Bot is not in the server or channel doesn't exist")
        except Exception as e:
            logger.error(f"❌ Error checking channel access: {e}")
        
        # Test connection to trading server
        health = self.trading_client.health_check()
        if health.get('status') == 'healthy':
            logger.info(f"✅ Trading Server is reachable")
        else:
            logger.warning(f"⚠️ Trading Server health check failed: {health}")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for trade signals"
            )
        )
    
    async def on_message(self, message: discord.Message):
        """
        Handle incoming messages.
        
        Args:
            message: Discord message object
        """
        # Ignore own messages
        if message.author == self.user:
            return
        
        # Ignore messages from other channels
        if message.channel.id != DISCORD_CHANNEL_ID:
            return
        
        self.stats['messages_seen'] += 1
        
        # Optional: Check user permissions
        if not self._is_authorized_user(message.author):
            logger.debug(f"Message from unauthorized user {message.author.name}")
            return
        
        # Try to parse signal
        try:
            signal = self.parser.parse(
                message.content,
                message_id=str(message.id)
            )
            
            if not signal:
                # Not a signal message, ignore
                return
            
            self.stats['signals_detected'] += 1
            logger.info(f"Signal detected from {message.author.name}: {signal.symbol} {signal.side}")
            
            # Send to trading server
            response = self.trading_client.send_signal(signal)
            
            if response.success:
                self.stats['signals_sent'] += 1
                logger.info(f"Signal executed successfully: {response.order_id}")
                
                # Send success notification
                await self.send_webhook_notification(
                    title="✅ Trade Executed",
                    description=f"Successfully entered {signal.side.upper()} position",
                    color=0x00ff00,  # Green
                    fields=[
                        {"name": "Symbol", "value": signal.symbol, "inline": True},
                        {"name": "Side", "value": signal.side.upper(), "inline": True},
                        {"name": "Entry", "value": f"${signal.entry_price:.6f}", "inline": True},
                        {"name": "Stop Loss", "value": f"${signal.stop_loss:.6f}", "inline": True},
                        {"name": "Take Profit", "value": f"${signal.take_profit_1:.6f}", "inline": True},
                        {"name": "Order ID", "value": response.order_id or "N/A", "inline": False}
                    ]
                )
                
            else:
                self.stats['signals_failed'] += 1
                logger.error(f"Signal execution failed: {response.message}")
                
                # Send failure notification
                await self.send_webhook_notification(
                    title="❌ Trade Failed",
                    description=f"Failed to execute {signal.side.upper()} {signal.symbol}",
                    color=0xff0000,  # Red
                    fields=[
                        {"name": "Symbol", "value": signal.symbol, "inline": True},
                        {"name": "Side", "value": signal.side.upper(), "inline": True},
                        {"name": "Error", "value": response.message[:1024], "inline": False}
                    ]
                )
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
        
        # Process commands (if any)
        await self.process_commands(message)
    
    def _is_authorized_user(self, user: discord.User | discord.Member) -> bool:
        """
        Check if user is authorized to post signals.
        
        Args:
            user: Discord user or member
            
        Returns:
            True if authorized
        """
        # If no filters configured, allow all
        if not ALLOWED_USER_IDS and not REQUIRED_ROLE_NAME:
            return True
        
        # Check user ID filter
        if ALLOWED_USER_IDS and user.id not in ALLOWED_USER_IDS:
            return False
        
        # Check role filter (only for guild members)
        if REQUIRED_ROLE_NAME and isinstance(user, discord.Member):
            has_role = any(role.name == REQUIRED_ROLE_NAME for role in user.roles)
            if not has_role:
                return False
        
        return True
    
    @commands.command(name='stats')
    async def stats_command(self, ctx):
        """Show bot statistics."""
        parser_stats = self.parser.get_stats()
        client_stats = self.trading_client.get_stats()
        
        stats_msg = (
            f"📊 **Bot Statistics**\n\n"
            f"**Messages:**\n"
            f"• Seen: {self.stats['messages_seen']}\n"
            f"• Signals Detected: {self.stats['signals_detected']}\n"
            f"• Signals Sent: {self.stats['signals_sent']}\n"
            f"• Failed: {self.stats['signals_failed']}\n\n"
            f"**Parser:**\n"
            f"• Total Parsed: {parser_stats['total_parsed']}\n"
            f"• Success Rate: {parser_stats['successful']}/{parser_stats['total_parsed']}\n\n"
            f"**Trading Server:**\n"
            f"• Requests: {client_stats['requests_sent']}\n"
            f"• Success: {client_stats['requests_succeeded']}\n"
            f"• Failed: {client_stats['requests_failed']}\n"
            f"• Retries: {client_stats['retries']}"
        )
        
        await ctx.send(stats_msg)
    
    @commands.command(name='health')
    async def health_command(self, ctx):
        """Check Trading Server health."""
        health = self.trading_client.health_check()
        
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'unreachable': '🔴'
        }
        
        emoji = status_emoji.get(health.get('status'), '❓')
        
        health_msg = (
            f"{emoji} **Trading Server Health**\n"
            f"Status: `{health.get('status', 'unknown')}`\n"
            f"URL: `{TRADING_SERVER_URL}`"
        )
        
        if 'error' in health:
            health_msg += f"\nError: `{health['error']}`"
        
        await ctx.send(health_msg)
    
    @commands.command(name='test')
    async def test_command(self, ctx, *, message: str):
        """Test parser with a message."""
        signal = self.parser.parse(message)
        
        if signal:
            await ctx.send(
                f"✅ **Parsed Successfully**\n"
                f"Symbol: `{signal.symbol}`\n"
                f"Side: `{signal.side}`\n"
                f"Entry: `{signal.entry_price or 'Market'}`\n"
                f"SL: `{signal.stop_loss or 'N/A'}`\n"
                f"TP: `{signal.take_profit or 'N/A'}`"
            )
        else:
            await ctx.send("❌ Could not parse message as a trade signal")


def main():
    """Main entry point."""
    # Validate configuration
    if not DISCORD_BOT_TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN not set in .env file")
        return
    
    if not DISCORD_CHANNEL_ID:
        logger.error("❌ DISCORD_CHANNEL_ID not set in .env file")
        return
    
    if not TRADING_SERVER_API_KEY:
        logger.error("❌ TRADING_SERVER_API_KEY not set in .env file")
        return
    
    # Create and run bot
    bot = TradingBot()
    
    try:
        logger.info("🚀 Starting Discord Bot...")
        bot.run(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
