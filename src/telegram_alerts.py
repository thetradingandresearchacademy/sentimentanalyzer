#!/usr/bin/env python3
"""
Telegram Alerts - Fixed for GitHub Actions
python-telegram-bot v13.15
"""

import logging
import requests
from typing import Dict

logger = logging.getLogger(__name__)

class TelegramAlerter:
    """Simple HTTP Telegram sender"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        logger.info("🔔 Telegram Alerter ready")
    
    def send_alert(self, symbol: str, sentiment: Dict, confidence: float, 
                   time_str: str, message: str = None):
        """Send via HTTP (no library issues)"""
        
        if not message:
            score = sentiment.get('aggregated', 0)
            if abs(score) < 0.3:
                return
            
            direction = "🟢 BUY" if score > 0 else "🔴 SELL"
            message = f"{direction} {symbol}\nScore: {score:.2f}\n{time_str}"
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Alert sent: {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
