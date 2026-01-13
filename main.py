#!/usr/bin/env python3
"""
Zero-Cost Sentiment Trading Bot - 200 F&O Stocks
"""

import os
import logging
import time
from datetime import datetime
import pytz
from typing import List, Dict

from src.sentiment_analyzer import ZeroCostSentimentEngine
from src.news_fetcher import FreeNewsFetcher
from src.telegram_alerts import TelegramAlerter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionSentimentBot:
    """Production bot for 200+ F&O stocks"""
    
    def __init__(self):
        logger.info("🚀 Starting Sentiment Trading Bot")
        
        self.sentiment_engine = ZeroCostSentimentEngine()
        self.news_fetcher = FreeNewsFetcher(os.getenv('MARKETAUX_API_KEY'))
        self.telegram = TelegramAlerter(
            os.getenv('TELEGRAM_BOT_TOKEN'),
            os.getenv('TELEGRAM_CHAT_ID')
        )
        
        self.watch_list = self._get_fo_stocks()
        logger.info(f"📊 Monitoring {len(self.watch_list)} F&O stocks")
    
    def _get_fo_stocks(self) -> List[str]:
        """200+ NSE F&O stocks"""
        return [
            'NIFTY', 'FINNIFTY', 'BANKNIFTY', 'INFY', 'TCS', 'RELIANCE',
            'HDFCBANK', 'HDFC', 'ICICIBANK', 'KOTAKBANK', 'SBIN', 'AXISBANK',
            'BAJFINANCE', 'MARUTI', 'LT', 'BHARTIARTL', 'SUNPHARMA', 'ITC',
            'TITAN', 'ADANIPORTS', 'ASIANPAINT', 'NESTLEIND', 'ULTRACEMCO',
            'ONGC', 'TATAMOTORS', 'POWERGRID', 'JSWSTEEL', 'TATACONSUM',
            'HCLTECH', 'WIPRO', 'TECHM', 'LTIM', 'BAJAJFINSV', 'APOLLOHOSP',
            'DRREDDY', 'HEROMOTOCO', 'COALINDIA', 'NTPC', 'BAJAJ-AUTO',
            'TATASTEEL', 'GRASIM', 'EICHERMOT', 'SHRIRAMFIN', 'HINDALCO',
            'BPCL', 'CIPLA', 'DIVISLAB', 'M&M', 'BRITANNIA', 'UPL', 'PIDILITIND'
        ]
    
    def run_full_analysis(self):
        """Main analysis"""
        logger.info("=" * 70)
        logger.info("🚀 FULL F&O SENTIMENT ANALYSIS START")
        logger.info("=" * 70)
        
        ist = pytz.timezone('Asia/Kolkata')
        analysis_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
        
        strong_signals = []
        batch_size = 50
        
        for batch_num in range(0, len(self.watch_list), batch_size):
            batch = self.watch_list[batch_num:batch_num+batch_size]
            logger.info(f"📦 Processing {len(batch)} stocks")
            
            for symbol in batch:
                try:
                    articles = self.news_fetcher.fetch_latest_news(symbol, limit=8)
                    if articles and len(articles) >= 3:
                        sentiment = self.sentiment_engine.analyze_batch(articles)
                        if abs(sentiment['aggregated']) > 0.45:
                            strong_signals.append({
                                'symbol': symbol,
                                'score': sentiment['aggregated'],
                                'strength': sentiment['strength'],
                                'count': sentiment['count']
                            })
                except Exception as e:
                    logger.error(f"Error {symbol}: {e}")
            
            time.sleep(1)
        
        # Send summary
        self._send_summary(strong_signals, analysis_time)
        logger.info("✅ Analysis complete")
        
        return strong_signals
    
    def _send_summary(self, signals: List[Dict], time_str: str):
        """Send Telegram summary"""
        if not signals:
            self.telegram.send_alert(
                "SUMMARY", {'aggregated': 0, 'count': 0},
                0.5, time_str, "📊 No strong signals today"
            )
            return
        
        signals.sort(key=lambda x: abs(x['score']), reverse=True)
        top = signals[:10]
        
        msg = f"📊 F&O SENTIMENT SUMMARY\n🔥 {len(signals)} SIGNALS\n\n"
        for i, s in enumerate(top, 1):
            direction = "🟢 BUY" if s['score'] > 0 else "🔴 SELL"
            msg += f"{i}. {direction} {s['symbol']} ({s['score']:.2f})\n"
        
        self.telegram.send_alert(
            "SUMMARY", {'aggregated': 0, 'count': len(signals)},
            1.0, time_str, msg
        )

def main():
    bot = ProductionSentimentBot()
    bot.run_full_analysis()

if __name__ == "__main__":
    main()
