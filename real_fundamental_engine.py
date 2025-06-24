# 🔥 STEP 3: REAL FUNDAMENTAL ANALYSIS ENGINE - NO FAKE DATA
# File: real_fundamental_engine.py

import yfinance as yf
import xml.etree.ElementTree as ET
import urllib.request
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from textblob import TextBlob
import json
import time
import logging

class RealFundamentalEngine:
    """🏦 REAL FUNDAMENTAL ANALYSIS ENGINE - VERIFIED DATA SOURCES ONLY"""
    
    def __init__(self):
        print("🔥 INITIALIZING REAL FUNDAMENTAL ENGINE...")
        self.setup_verified_sources()
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_verified_sources(self):
        """📡 Setup VERIFIED working data sources from Step 2 tests"""
        
        # ✅ VERIFIED: All tested successfully in Step 2
        self.yahoo_tickers = {
            'VIX': '^VIX',           # Market fear - TESTED ✅
            'SPX': '^GSPC',          # Risk sentiment - TESTED ✅
            'DXY': 'DX-Y.NYB',       # USD strength - TESTED ✅
            'TNX': '^TNX',           # 10Y Treasury - TESTED ✅
            'GLD': 'GLD',            # Gold safe haven - TESTED ✅
            'OIL': 'CL=F',           # Oil CAD correlation - TESTED ✅
            'TLT': 'TLT',            # Bonds risk sentiment - TESTED ✅
        }
        
        # ✅ VERIFIED: 3/4 feeds working from Step 2
        self.working_rss_feeds = {
            'fed_news': 'https://www.federalreserve.gov/feeds/press_all.xml',
            'forexlive': 'https://www.forexlive.com/feed/',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss'
            # Reuters removed - failed in testing
        }
        
        print("✅ VERIFIED DATA SOURCES CONFIGURED")
    
    def get_cached_or_fetch(self, cache_key, fetch_function, *args):
        """💾 Smart caching to avoid hitting APIs too frequently"""
        
        now = datetime.now()
        
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (now - cached_time).total_seconds() < self.cache_duration:
                return cached_data
        
        # Fetch new data
        try:
            fresh_data = fetch_function(*args)
            self.cache[cache_key] = (fresh_data, now)
            return fresh_data
        except Exception as e:
            self.logger.error(f"Error fetching {cache_key}: {e}")
            # Return cached data if available, even if expired
            if cache_key in self.cache:
                return self.cache[cache_key][0]
            return {}
    
    def fetch_real_market_data(self):
        """📊 Fetch REAL market sentiment data from Yahoo Finance"""
        
        try:
            market_data = {}
            
            for name, ticker in self.yahoo_tickers.items():
                try:
                    yf_ticker = yf.Ticker(ticker)
                    data = yf_ticker.history(period='5d')
                    
                    if not data.empty:
                        # Fix the pandas FutureWarning by using .iloc
                        latest_value = data['Close'].iloc[-1]
                        prev_value = data['Close'].iloc[-2] if len(data) > 1 else latest_value
                        change_pct = (latest_value - prev_value) / prev_value * 100
                        
                        market_data[name] = {
                            'value': float(latest_value),
                            'change_pct': float(change_pct),
                            'data_points': len(data),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    self.logger.warning(f"Failed to fetch {name}: {e}")
                    continue
                
                time.sleep(0.2)  # Be respectful to Yahoo Finance
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Market data fetch error: {e}")
            return {}
    
    def fetch_real_news_sentiment(self, currency_pair, hours_back=24):
        """📰 Fetch REAL news sentiment from RSS feeds - NO FEEDPARSER"""
        
        try:
            base_curr = currency_pair[:3]
            quote_curr = currency_pair[3:]
            all_articles = []
            sentiment_scores = []
            
            # Simple RSS parser without feedparser
            for feed_name, feed_url in self.working_rss_feeds.items():
                try:
                    print(f"📡 Fetching {feed_name}...")
                    
                    # Use urllib to fetch RSS
                    with urllib.request.urlopen(feed_url, timeout=10) as response:
                        xml_data = response.read().decode('utf-8')
                    
                    # Parse XML manually
                    try:
                        root = ET.fromstring(xml_data)
                    except ET.ParseError:
                        # Handle malformed XML
                        xml_data = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', xml_data)
                        root = ET.fromstring(xml_data)
                    
                    # Find RSS items
                    items = root.findall('.//item')[:5]  # Get first 5 items
                    
                    for item in items:
                        try:
                            # Extract title and description
                            title_elem = item.find('title')
                            desc_elem = item.find('description')
                            
                            title = title_elem.text if title_elem is not None else ''
                            description = desc_elem.text if desc_elem is not None else ''
                            
                            # Clean HTML tags from description
                            description = re.sub(r'<[^>]+>', '', description)
                            
                            text = f"{title} {description}".upper()
                            
                            # Check if relevant to forex/currencies
                            currency_keywords = [base_curr, quote_curr, 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'NZD', 'CHF']
                            forex_keywords = ['FED', 'ECB', 'BOE', 'BOJ', 'RATE', 'CURRENCY', 'DOLLAR', 'FOREX', 'CENTRAL BANK']
                            
                            relevant = any(keyword in text for keyword in currency_keywords + forex_keywords)
                            
                            if relevant and len(text.strip()) > 10:
                                # Real sentiment analysis
                                blob = TextBlob(text)
                                sentiment = blob.sentiment.polarity
                                
                                all_articles.append({
                                    'title': title[:100],  # Truncate for logging
                                    'sentiment': sentiment,
                                    'source': feed_name,
                                    'relevant_keywords': [kw for kw in currency_keywords + forex_keywords if kw in text][:3]
                                })
                                sentiment_scores.append(sentiment)
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"RSS feed {feed_name} error: {e}")
                    continue
                
                time.sleep(0.5)  # Be respectful to RSS servers
            
            # Calculate sentiment metrics
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                
                return {
                    'sentiment_score': avg_sentiment,
                    'classification': self.classify_sentiment(avg_sentiment),
                    'articles_analyzed': len(sentiment_scores),
                    'confidence': min(0.8, len(sentiment_scores) / 15),  # Max confidence at 15+ articles
                    'articles': all_articles[-10:],  # Keep last 10 articles
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'sentiment_score': 0,
                    'classification': 'NEUTRAL',
                    'articles_analyzed': 0,
                    'confidence': 0,
                    'articles': [],
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"News sentiment error: {e}")
            return {
                'sentiment_score': 0,
                'classification': 'NEUTRAL', 
                'articles_analyzed': 0,
                'confidence': 0,
                'articles': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def classify_sentiment(self, score):
        """📊 Classify sentiment score into categories"""
        if score > 0.15:
            return 'BULLISH'
        elif score < -0.15:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def calculate_risk_sentiment(self, market_data):
        """🎯 Calculate overall risk sentiment from REAL market data"""
        
        try:
            risk_factors = []
            
            # VIX factor (fear gauge)
            if 'VIX' in market_data:
                vix_value = market_data['VIX']['value']
                if vix_value > 25:
                    risk_factors.append(-1)  # High fear = risk off
                elif vix_value < 15:
                    risk_factors.append(1)   # Low fear = risk on
                else:
                    risk_factors.append(0)   # Neutral
            
            # SPX factor (equity performance)
            if 'SPX' in market_data:
                spx_change = market_data['SPX']['change_pct']
                if spx_change > 1:
                    risk_factors.append(1)   # Strong gains = risk on
                elif spx_change < -1:
                    risk_factors.append(-1)  # Losses = risk off
                else:
                    risk_factors.append(0)
            
            # Treasury factor (yield movements)
            if 'TNX' in market_data:
                tnx_change = market_data['TNX']['change_pct']
                if tnx_change > 2:
                    risk_factors.append(1)   # Rising yields = risk on
                elif tnx_change < -2:
                    risk_factors.append(-1)  # Falling yields = risk off
                else:
                    risk_factors.append(0)
            
            # Calculate overall risk sentiment
            if risk_factors:
                avg_risk = sum(risk_factors) / len(risk_factors)
                if avg_risk > 0.3:
                    return 'RISK_ON'
                elif avg_risk < -0.3:
                    return 'RISK_OFF'
                else:
                    return 'NEUTRAL'
            else:
                return 'UNKNOWN'
                
        except Exception as e:
            self.logger.error(f"Risk sentiment calculation error: {e}")
            return 'UNKNOWN'
    
    def calculate_currency_specific_factors(self, currency_pair, market_data):
        """💱 Calculate currency-specific fundamental factors"""
        
        try:
            base_curr = currency_pair[:3]
            quote_curr = currency_pair[3:]
            factors = {'base_factors': [], 'quote_factors': []}
            
            # USD factors
            if base_curr == 'USD' or quote_curr == 'USD':
                usd_factors = []
                
                # DXY strength
                if 'DXY' in market_data:
                    dxy_change = market_data['DXY']['change_pct']
                    if abs(dxy_change) > 0.3:
                        usd_strength = 1 if dxy_change > 0 else -1
                        if base_curr == 'USD':
                            factors['base_factors'].append(usd_strength)
                        else:
                            factors['quote_factors'].append(-usd_strength)  # Inverse for quote
                
                # Treasury yields (USD strength indicator)
                if 'TNX' in market_data:
                    tnx_change = market_data['TNX']['change_pct']
                    if abs(tnx_change) > 1:
                        yield_factor = 1 if tnx_change > 0 else -1
                        if base_curr == 'USD':
                            factors['base_factors'].append(yield_factor * 0.5)
                        else:
                            factors['quote_factors'].append(-yield_factor * 0.5)
            
            # CAD factors (oil correlation)
            if base_curr == 'CAD' or quote_curr == 'CAD':
                if 'OIL' in market_data:
                    oil_change = market_data['OIL']['change_pct']
                    if abs(oil_change) > 1:
                        oil_factor = 1 if oil_change > 0 else -1
                        if base_curr == 'CAD':
                            factors['base_factors'].append(oil_factor * 0.7)  # Strong correlation
                        else:
                            factors['quote_factors'].append(-oil_factor * 0.7)
            
            # JPY/CHF factors (safe haven)
            for curr in ['JPY', 'CHF']:
                if base_curr == curr or quote_curr == curr:
                    safe_haven_factor = 0
                    
                    # VIX factor
                    if 'VIX' in market_data:
                        vix_change = market_data['VIX']['change_pct']
                        if vix_change > 5:  # Rising fear
                            safe_haven_factor += 1
                        elif vix_change < -5:  # Falling fear
                            safe_haven_factor -= 1
                    
                    # Gold factor
                    if 'GLD' in market_data:
                        gold_change = market_data['GLD']['change_pct']
                        if gold_change > 1:  # Gold rising
                            safe_haven_factor += 0.5
                        elif gold_change < -1:  # Gold falling
                            safe_haven_factor -= 0.5
                    
                    if safe_haven_factor != 0:
                        if base_curr == curr:
                            factors['base_factors'].append(safe_haven_factor)
                        else:
                            factors['quote_factors'].append(-safe_haven_factor)
            
            # AUD/NZD factors (risk sentiment)
            for curr in ['AUD', 'NZD']:
                if base_curr == curr or quote_curr == curr:
                    # These currencies benefit from risk-on sentiment
                    risk_factor = 0
                    
                    if 'SPX' in market_data:
                        spx_change = market_data['SPX']['change_pct']
                        if spx_change > 1:
                            risk_factor += 1
                        elif spx_change < -1:
                            risk_factor -= 1
                    
                    if risk_factor != 0:
                        if base_curr == curr:
                            factors['base_factors'].append(risk_factor * 0.6)
                        else:
                            factors['quote_factors'].append(-risk_factor * 0.6)
            
            return factors
            
        except Exception as e:
            self.logger.error(f"Currency factors calculation error: {e}")
            return {'base_factors': [], 'quote_factors': []}
    
    def enhance_signal_with_real_fundamentals(self, signal_data):
        """🚀 MAIN FUNCTION: Enhance trading signal with REAL fundamental data"""
        
        try:
            currency_pair = signal_data.get('ticker', 'EURUSD')
            original_confidence = float(signal_data.get('confidence', 0.7))
            
            self.logger.info(f"🔍 Enhancing {currency_pair} signal with real fundamental data...")
            
            # Fetch real market data (cached)
            market_data = self.get_cached_or_fetch(
                'market_data', 
                self.fetch_real_market_data
            )
            
            # Fetch real news sentiment (cached)
            news_sentiment = self.get_cached_or_fetch(
                f'news_{currency_pair}',
                self.fetch_real_news_sentiment,
                currency_pair
            )
            
            # Calculate enhancement factor
            enhancement_factor = self.calculate_enhancement_factor(
                currency_pair, market_data, news_sentiment
            )
            
            # Apply enhancement
            enhanced_confidence = self.apply_enhancement(original_confidence, enhancement_factor)
            
            # Build enhanced signal
            enhanced_signal = signal_data.copy()
            enhanced_signal.update({
                'original_confidence': original_confidence,
                'enhanced_confidence': enhanced_confidence,
                'enhancement_factor': enhancement_factor,
                'fundamental_data': {
                    'market_data': market_data,
                    'news_sentiment': news_sentiment,
                    'risk_sentiment': self.calculate_risk_sentiment(market_data),
                    'currency_factors': self.calculate_currency_specific_factors(currency_pair, market_data)
                },
                'enhancement_timestamp': datetime.now().isoformat(),
                'data_sources': 'REAL_YAHOO_RSS_ONLY'
            })
            
            self.logger.info(f"✅ Enhanced: {original_confidence:.3f} → {enhanced_confidence:.3f} (×{enhancement_factor:.3f})")
            
            return enhanced_signal
            
        except Exception as e:
            self.logger.error(f"Signal enhancement error: {e}")
            # Return original signal if enhancement fails
            return signal_data
    
    def calculate_enhancement_factor(self, currency_pair, market_data, news_sentiment):
        """🧮 Calculate enhancement factor from REAL data"""
        
        try:
            factor = 1.0
            
            # News sentiment impact (10-15% max impact)
            if news_sentiment and news_sentiment.get('articles_analyzed', 0) > 0:
                sentiment_score = news_sentiment.get('sentiment_score', 0)
                confidence = news_sentiment.get('confidence', 0)
                
                if confidence > 0.2:  # Only apply if sufficient news data
                    sentiment_impact = sentiment_score * confidence * 0.15
                    factor *= (1.0 + sentiment_impact)
            
            # Market risk sentiment impact
            risk_sentiment = self.calculate_risk_sentiment(market_data)
            currency_factors = self.calculate_currency_specific_factors(currency_pair, market_data)
            
            # Apply currency-specific factors
            base_factor = sum(currency_factors['base_factors']) if currency_factors['base_factors'] else 0
            quote_factor = sum(currency_factors['quote_factors']) if currency_factors['quote_factors'] else 0
            
            # Combine base and quote factors
            total_currency_factor = base_factor + quote_factor
            
            # Apply currency factor (max 20% impact)
            if abs(total_currency_factor) > 0.1:
                currency_impact = max(-0.2, min(0.2, total_currency_factor * 0.1))
                factor *= (1.0 + currency_impact)
            
            # Constrain factor to reasonable range
            factor = max(0.7, min(1.4, factor))
            
            return factor
            
        except Exception as e:
            self.logger.error(f"Enhancement factor calculation error: {e}")
            return 1.0
    
    def apply_enhancement(self, original_confidence, enhancement_factor):
        """⚡ Apply enhancement factor to original confidence"""
        
        enhanced = original_confidence * enhancement_factor
        
        # Ensure enhanced confidence stays within bounds
        enhanced = max(0.1, min(0.95, enhanced))
        
        return enhanced
    
    def get_fundamental_summary(self, currency_pair):
        """📊 Get summary of fundamental factors for dashboard"""
        
        try:
            market_data = self.get_cached_or_fetch('market_data', self.fetch_real_market_data)
            news_sentiment = self.get_cached_or_fetch(f'news_{currency_pair}', self.fetch_real_news_sentiment, currency_pair)
            
            summary = {
                'currency_pair': currency_pair,
                'risk_sentiment': self.calculate_risk_sentiment(market_data),
                'news_sentiment': news_sentiment.get('classification', 'NEUTRAL'),
                'news_confidence': news_sentiment.get('confidence', 0),
                'articles_analyzed': news_sentiment.get('articles_analyzed', 0),
                'market_indicators': {
                    name: {
                        'value': data['value'],
                        'change_pct': data['change_pct']
                    } for name, data in market_data.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Fundamental summary error: {e}")
            return {}


# Integration helper function
def create_enhanced_webhook_handler():
    """🔗 Create enhanced webhook handler for integration"""
    
    # Initialize the real fundamental engine
    fundamental_engine = RealFundamentalEngine()
    
    def enhanced_handler(signal_data):
        """Enhanced webhook handler with real fundamental analysis"""
        return fundamental_engine.enhance_signal_with_real_fundamentals(signal_data)
    
    return enhanced_handler, fundamental_engine


if __name__ == "__main__":
    # Test the real fundamental engine
    print("🔥 TESTING REAL FUNDAMENTAL ENGINE...")
    
    engine = RealFundamentalEngine()
    
    # Test signal enhancement
    test_signal = {
        'ticker': 'EURUSD',
        'action': 'BUY',
        'confidence': 0.72,
        'price': 1.1584,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"🧪 Testing enhancement on: {test_signal}")
    
    enhanced = engine.enhance_signal_with_real_fundamentals(test_signal)
    
    print(f"✅ Enhancement complete!")
    print(f"   Original confidence: {enhanced.get('original_confidence', 0):.3f}")
    print(f"   Enhanced confidence: {enhanced.get('enhanced_confidence', 0):.3f}")
    print(f"   Enhancement factor: {enhanced.get('enhancement_factor', 1):.3f}")
    
    # Test fundamental summary
    summary = engine.get_fundamental_summary('EURUSD')
    print(f"📊 Fundamental summary: {summary.get('risk_sentiment', 'UNKNOWN')} risk sentiment")
    
    print("🚀 REAL FUNDAMENTAL ENGINE READY!")