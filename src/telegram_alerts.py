#!/usr/bin/env python3
"""
Telegram Alert System (UNLIMITED FREE)
Real-time trading alerts
"""

from telegram import Bot
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)

class TelegramAlerter:
    """Send alerts via Telegram (100% FREE)"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        logger.info("🔔 Telegram Alerter initialized")
    
    def send_alert(self, symbol: str, sentiment: Dict, confidence: float, 
                   time_str: str, message: str = None):
        """Send trading alert"""
        
        if not message:
            if abs(sentiment.get('aggregated', 0)) < 0.3:
                return  # Skip neutral
            
            direction = "🟢 BUY" if sentiment['aggregated'] > 0 else "🔴 SELL"
            message = f"""
{direction} Signal - {symbol}

📊 Score: {sentiment['aggregated']:.2f}
💪 Strength: {sentiment.get('strength', 'NEUTRAL')}
📰 Articles: {sentiment.get('count', 0)}
📈 Confidence: {confidence:.0%}

⏰ {time_str}
            """
        
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Alert sent for {symbol}")
        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")
