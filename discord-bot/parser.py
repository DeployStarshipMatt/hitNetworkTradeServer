"""
Signal Parser Module

Extracts trade signal information from Discord messages.
Self-contained - add new patterns without affecting other modules.
"""
import re
import json
from typing import Optional, Dict, Any
import logging
import os

# Add parent directory to path for shared imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.models import TradeSignal

logger = logging.getLogger(__name__)

# Optional: Try to import Claude API client
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logger.warning("Anthropic package not installed - Claude fallback unavailable")


class SignalParser:
    """
    Parses Discord messages for trade signals.
    
    Supports multiple signal formats and can be extended with new patterns.
    """
    
    # Pattern library - easily add new formats
    PATTERNS = {
        # Pattern 1: Trading Signal Alert format (YOUR FORMAT)
        # Example: "📝PAIR: SEI/USDT #1131 ... SIDE: __SHORT📉__ ... 📍ENTRY: `0.125294` ✖️SL: `0.127698` TP1: `0.123615` ... ⚖️LEVERAGE: 35x"
        'trading_signal_alert': re.compile(
            r'PAIR[:\s*]+(?P<symbol>[A-Z]+/USDT)(?:\s*#\d+)?.*?'
            r'SIDE[:\s*]+[_*]*(?P<side>LONG|SHORT)[📈📉_*]*.*?'
            r'ENTRY[:\s*]+`?(?P<entry>[\d.]+)`?.*?'
            r'SL[:\s*]+`?(?P<sl>[\d.]+)`?.*?'
            r'TP1[:\s*]+`?(?P<tp1>[\d.]+)`?(?:.*?TP2[:\s*]+`?(?P<tp2>[\d.]+)`?)?(?:.*?TP3[:\s*]+`?(?P<tp3>[\d.]+)`?)?'
            r'(?:.*?LEVERAGE[:\s*]+(?P<leverage>\d+)x)?',
            re.IGNORECASE | re.DOTALL
        ),
        
        # Pattern 2: Standard format
        # Example: "🚨 LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000 Size: 0.01"
        'standard': re.compile(
            r'(?P<side>long|short|buy|sell)\s+'
            r'(?P<symbol>[A-Z]+-[A-Z]+)\s+'
            r'(?:entry[:\s]+)?(?P<entry>[\d.]+)?\s*'
            r'(?:sl[:\s]+)?(?P<sl>[\d.]+)?\s*'
            r'(?:tp[:\s]+)?(?P<tp>[\d.]+)?\s*'
            r'(?:size[:\s]+)?(?P<size>[\d.]+)?',
            re.IGNORECASE
        ),
        
        # Pattern 3: Compact format
        # Example: "LONG BTCUSDT 60000/58000/65000"
        'compact': re.compile(
            r'(?P<side>long|short|buy|sell)\s+'
            r'(?P<symbol>[A-Z]+)\s+'
            r'(?P<entry>[\d.]+)/(?P<sl>[\d.]+)/(?P<tp>[\d.]+)',
            re.IGNORECASE
        ),
        
        # Pattern 4: Emoji-based
        # Example: "📈 BTC-USDT 💰 60000 🛑 58000 🎯 65000"
        'emoji': re.compile(
            r'(?P<emoji>📈|📉|🟢|🔴)\s+'
            r'(?P<symbol>[A-Z]+-[A-Z]+)\s+'
            r'(?:💰|entry)\s*(?P<entry>[\d.]+)?\s*'
            r'(?:🛑|sl)\s*(?P<sl>[\d.]+)?\s*'
            r'(?:🎯|tp)\s*(?P<tp>[\d.]+)?',
            re.IGNORECASE
        )
    }
    
    # Emoji to side mapping
    EMOJI_SIDES = {
        '📈': 'long',
        '🟢': 'long',
        '📉': 'short',
        '🔴': 'short'
    }
    
    # Signal indicators - messages containing these are likely signals
    SIGNAL_INDICATORS = [
        '🚨',
        'signal',
        'trade',
        'entry',
        'long',
        'short',
        '📈',
        '📉',
        'trading signal alert',
        'pair:',
        'side:'
    ]
    
    def __init__(self):
        """Initialize parser."""
        self.stats = {
            'total_parsed': 0,
            'successful': 0,
            'failed': 0,
            'by_pattern': {}
        }
    
    def is_signal_message(self, message: str) -> bool:
        """
        Quick check if message might contain a trade signal.
        
        Args:
            message: Discord message content
            
        Returns:
            True if message likely contains a signal
        """
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in self.SIGNAL_INDICATORS)
    
    def parse(self, message: str, message_id: Optional[str] = None) -> Optional[TradeSignal]:
        """
        Parse a Discord message for trade signal.
        
        Args:
            message: Discord message content
            message_id: Optional Discord message ID for tracking
            
        Returns:
            TradeSignal object if parsing successful, None otherwise
        """
        self.stats['total_parsed'] += 1
        
        # Quick filter
        if not self.is_signal_message(message):
            logger.debug(f"Message doesn't contain signal indicators: {message[:50]}...")
            return None
        
        # Try each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            try:
                signal = self._try_pattern(pattern, pattern_name, message, message_id)
                if signal:
                    self.stats['successful'] += 1
                    self.stats['by_pattern'][pattern_name] = self.stats['by_pattern'].get(pattern_name, 0) + 1
                    logger.info(f"Successfully parsed signal using pattern '{pattern_name}': {signal.symbol} {signal.side}")
                    return signal
            except Exception as e:
                logger.error(f"Error with pattern '{pattern_name}': {e}")
                continue
        
        self.stats['failed'] += 1
        logger.warning(f"Could not parse message: {message[:100]}...")
        
        # Try Claude fallback if available
        if CLAUDE_AVAILABLE and os.getenv('CLAUDE_API_KEY'):
            logger.info("Attempting Claude API fallback...")
            try:
                signal = self._parse_with_claude(message, message_id)
                if signal:
                    self.stats['successful'] += 1
                    self.stats['by_pattern']['claude_fallback'] = self.stats['by_pattern'].get('claude_fallback', 0) + 1
                    logger.info(f"✅ Claude fallback successful: {signal.symbol} {signal.side}")
                    return signal
            except Exception as e:
                logger.error(f"Claude fallback failed: {e}")
        
        return None
    
    def _try_pattern(self, pattern: re.Pattern, pattern_name: str, 
                     message: str, message_id: Optional[str]) -> Optional[TradeSignal]:
        """
        Try to match a specific pattern.
        
        Args:
            pattern: Compiled regex pattern
            pattern_name: Name of pattern for logging
            message: Message to parse
            message_id: Message ID for tracking
            
        Returns:
            TradeSignal if match found, None otherwise
        """
        match = pattern.search(message)
        if not match:
            return None
        
        data = match.groupdict()
        
        # Handle emoji-based side detection
        side = data.get('side')
        if not side and 'emoji' in data:
            side = self.EMOJI_SIDES.get(data['emoji'])
        
        if not side:
            return None
        
        # Normalize symbol (add hyphen if missing, handle / separator)
        symbol = data.get('symbol', '')
        if symbol:
            # Replace / with - (e.g., TIA/USDT -> TIA-USDT)
            if '/' in symbol:
                symbol = symbol.replace('/', '-')
            # Add hyphen if missing (e.g., BTCUSDT -> BTC-USDT)
            elif '-' not in symbol:
                if 'USDT' in symbol:
                    symbol = symbol.replace('USDT', '-USDT')
                elif 'USD' in symbol:
                    symbol = symbol.replace('USD', '-USD')
        
        # Convert strings to floats
        entry_price = self._to_float(data.get('entry'))
        stop_loss = self._to_float(data.get('sl'))
        # Handle multiple TP formats (tp1 or tp for backward compatibility)
        take_profit = self._to_float(data.get('tp1') or data.get('tp'))
        take_profit_2 = self._to_float(data.get('tp2'))
        take_profit_3 = self._to_float(data.get('tp3'))
        size = self._to_float(data.get('size'))
        leverage = self._to_int(data.get('leverage'))  # Extract leverage as integer
        
        # Create TradeSignal
        try:
            signal = TradeSignal(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                take_profit_2=take_profit_2,
                take_profit_3=take_profit_3,
                size=size,
                leverage=leverage,
                signal_id=message_id,
                raw_message=message[:500]  # Limit raw message length
            )
            
            # Validate
            is_valid, error = signal.validate()
            if not is_valid:
                logger.warning(f"Invalid signal: {error}")
                return None
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating TradeSignal: {e}")
            return None
    
    @staticmethod
    def _to_float(value: Optional[str]) -> Optional[float]:
        """
        Safely convert string to float.
        
        Args:
            value: String value
            
        Returns:
            Float value or None
        """
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _to_int(value: Optional[str]) -> Optional[int]:
        """
        Safely convert string to int.
        
        Args:
            value: String value
            
        Returns:
            Int value or None
        """
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get parser statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset parser statistics."""
        self.stats = {
            'total_parsed': 0,
            'successful': 0,
            'failed': 0,
            'by_pattern': {}
        }
    
    def _parse_with_claude(self, message: str, message_id: Optional[str] = None) -> Optional[TradeSignal]:
        """
        Parse signal using Claude API as fallback.
        
        Args:
            message: Discord message content
            message_id: Optional message ID for tracking
            
        Returns:
            TradeSignal if successfully parsed, None otherwise
        """
        if not CLAUDE_AVAILABLE:
            logger.warning("Claude API not available (anthropic package not installed)")
            return None
        
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            logger.warning("CLAUDE_API_KEY not set in environment")
            return None
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            prompt = f"""Parse this trading signal and extract the key information.
Return ONLY a JSON object with these exact fields (no markdown, no explanation):
{{
    "symbol": "SYMBOL-USDT" (e.g., "BTC-USDT"),
    "side": "long" or "short",
    "entry": decimal number or null,
    "stop_loss": decimal number or null,
    "take_profit": decimal number or null,
    "take_profit_2": decimal number or null,
    "take_profit_3": decimal number or null,
    "leverage": integer or null
}}

Trading Signal:
{message}

Remember: Return ONLY the JSON object, nothing else."""
            
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",  # Best model for coding and complex parsing
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON response
            import json
            data = json.loads(response_text)
            
            # Validate required fields
            if not data.get('symbol') or not data.get('side'):
                logger.warning("Claude response missing required fields")
                return None
            
            # Create TradeSignal
            signal = TradeSignal(
                symbol=data['symbol'],
                side=data['side'],
                entry_price=data.get('entry'),
                stop_loss=data.get('stop_loss'),
                take_profit=data.get('take_profit'),
                take_profit_2=data.get('take_profit_2'),
                take_profit_3=data.get('take_profit_3'),
                leverage=data.get('leverage'),
                signal_id=message_id,
                raw_message=message
            )
            
            return signal
            
        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}")
            logger.debug(f"Response was: {response_text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None


# Convenience function for simple parsing
def parse_signal(message: str, message_id: Optional[str] = None) -> Optional[TradeSignal]:
    """
    Quick parse function.
    
    Args:
        message: Discord message content
        message_id: Optional message ID
        
    Returns:
        TradeSignal or None
    """
    parser = SignalParser()
    return parser.parse(message, message_id)


if __name__ == "__main__":
    # Test the parser with sample messages
    logging.basicConfig(level=logging.INFO)
    
    test_messages = [
        "🚨 LONG BTC-USDT Entry: 60000 SL: 58000 TP: 65000 Size: 0.01",
        "SHORT ETH-USDT 3500/3600/3200",
        "📈 BTC-USDT 💰 60000 🛑 58000 🎯 65000",
        "LONG BTCUSDT Entry: 60000 SL: 58000 TP: 65000",
        "Just a regular message without signals"
    ]
    
    parser = SignalParser()
    for msg in test_messages:
        print(f"\nTesting: {msg}")
        signal = parser.parse(msg)
        if signal:
            print(f"  ✅ Parsed: {signal.symbol} {signal.side} @ {signal.entry_price}")
        else:
            print(f"  ❌ Failed to parse")
    
    print(f"\nStats: {parser.get_stats()}")
