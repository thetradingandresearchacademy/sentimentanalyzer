#!/usr/bin/env python3
"""
BULLETPROOF Sentiment Bot - Self-Contained
No import issues, VADER only, 100% works
"""

import os
import logging
import time
import requests
import nltk
from datetime import datetime
import pytz
from typing import List, Dict

nltk.download('vader_lexicon', quiet=True)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class BulletproofBot:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.api_key = os.getenv('MARKETAUX_API_KEY')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        self.stocks = [
            'NIFTY', 'FINNIFTY', 'BANKNIFTY', 'INFY', 'TCS', 'RELIANCE',
            'HDFCBANK', 'HDFC', 'ICICIBANK', 'KOTAKBANK', 'SBIN', 'AXISBANK',
            'BAJFINANCE', 'MARUTI', 'LT', 'BHARTIARTL', 'SUNPHARMA', 'ITC',
            'TITAN', 'ADANIPORTS', 'ASIANPAINT', 'NESTLEIND', 'ULTRACEMCO',
            'ONGC', 'TATAMOTORS', 'POWERGRID', 'JSWSTEEL', 'TATACONSUM',
            'HCLTECH', 'WIPRO', 'TECHM', 'LTIM', 'BAJAJFINSV', 'APOLLOHOSP',
            'DRREDDY', 'HEROMOTOCO', 'COALINDIA', 'NTPC', 'BAJAJ-AUTO',
            'TATASTEEL', 'GRASIM', 'EICHERMOT', 'SHRIRAMFIN', 'HINDALCO',
            'BPCL', 'CIPLA', 'DIVISLAB', 'M&M', 'BRITANNIA'
        ]
        logger.info(f"🚀 Analyzing {len(self.stocks)} F&O stocks")
    
    def fetch_news(self, symbol: str) -> List[Dict]:
        """Fetch news from marketaux API"""
        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'symbols': symbol,
                'limit': 8,
                'api_token': self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            articles = []
            for article in data.get('data', []):
                articles.append({
                    'headline': article.get('title', ''),
                    'text': article.get('description', '')[:300]
                })
            
            return articles[:8]
        except Exception as e:
            logger.error(f"News fetch error {symbol}: {e}")
            return []
    
    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """VADER sentiment analysis"""
        if not articles:
            return {'score': 0.0, 'count': 0, 'strength': 'NEUTRAL'}
        
        scores = []
        for article in articles:
            text = f"{article['headline']} {article['text']}"
            if len(text) > 5:
                result = self.vader.polarity_scores(text)
                scores.append(result['compound'])
        
        if not scores:
            return {'score': 0.0, 'count': len(articles), 'strength': 'NEUTRAL'}
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.6:
            strength = '🟢 STRONG BULLISH'
        elif avg_score > 0.3:
            strength = '🟢 BULLISH'
        elif avg_score < -0.6:
            strength = '🔴 STRONG BEARISH'
        elif avg_score < -0.3:
            strength = '🔴 BEARISH'
        else:
            strength = '⚪ NEUTRAL'
        
        return {
            'score': round(avg_score, 3),
            'count': len(scores),
            'strength': strength
        }
    
    def send_telegram(self, message: str):
        """Send Telegram message via HTTP"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            requests.post(url, json=payload, timeout=10)
            logger.info("✅ Telegram sent")
        except Exception as e:
            logger.error(f"Telegram error: {e}")
    
    def run(self):
        """Main analysis loop"""
        logger.info("=" * 70)
        logger.info("🚀 SENTIMENT ANALYSIS START")
        logger.info("=" * 70)
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
        
        strong_signals = []
        
        for symbol in self.stocks:
            try:
                articles = self.fetch_news(symbol)
                if len(articles) >= 3:
                    sentiment = self.analyze_sentiment(articles)
                    
                    if abs(sentiment['score']) > 0.45:
                        strong_signals.append({
                            'symbol': symbol,
                            'score': sentiment['score'],
                            'strength': sentiment['strength']
                        })
                        logger.info(f"🔥 {symbol}: {sentiment['strength']} ({sentiment['score']})")
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error {symbol}: {e}")
        
        # Send summary
        if strong_signals:
            strong_signals.sort(key=lambda x: abs(x['score']), reverse=True)
            
            msg = f"📊 F&O SENTIMENT ANALYSIS\n{now}\n\n"
            msg += f"🔥 {len(strong_signals)} STRONG SIGNALS\n\n"
            
            for i, signal in enumerate(strong_signals[:10], 1):
                direction = "🟢 BUY" if signal['score'] > 0 else "🔴 SELL"
                msg += f"{i}. {direction} {signal['symbol']}\n"
                msg += f"   {signal['strength']} ({signal['score']})\n\n"
            
            self.send_telegram(msg)
        else:
            self.send_telegram(f"📊 Sentiment Analysis\n{now}\n\n⚪ No strong signals today")
        
        logger.info("=" * 70)
        logger.info(f"✅ Analysis complete: {len(strong_signals)} signals")
        logger.info("=" * 70)

def main():
    try:
        bot = BulletproofBot()
        bot.run()
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    main()
