#!/usr/bin/env python3
"""
News Fetcher - marketaux API (UNLIMITED FREE)
Covers 200,000+ entities, 5,000+ sources
"""

import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class FreeNewsFetcher:
    """Fetch news from marketaux (unlimited free tier)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.marketaux.com/v1/news/all"
        logger.info("🔗 News Fetcher initialized (marketaux)")
    
    def fetch_latest_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Fetch latest news for stock"""
        try:
            params = {
                'symbols': symbol,
                'limit': limit,
                'api_token': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('data', [])
            
            normalized = []
            for article in articles:
                normalized.append({
                    'headline': article.get('title', ''),
                    'text': article.get('description', ''),
                    'source': article.get('source', 'marketaux'),
                    'published': article.get('published_at', ''),
                    'url': article.get('url', '')
                })
            
            logger.info(f"📰 {symbol}: {len(normalized)} articles fetched")
            return normalized[:limit]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ News API error for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error processing news for {symbol}: {e}")
            return []
