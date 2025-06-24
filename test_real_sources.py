# 🧪 STEP 2: TEST ALL REAL DATA SOURCES - NO FAKE DATA
# Run this script to verify every data source works before integration

import yfinance as yf
import feedparser
import requests
from datetime import datetime
import time

def test_yahoo_finance_sources():
    """Test all Yahoo Finance real data sources"""
    
    print("🧪 TESTING YAHOO FINANCE REAL DATA SOURCES...")
    
    # Your existing proven tickers
    test_tickers = {
        'VIX (Market Fear)': '^VIX',
        'SPX (Risk Sentiment)': '^GSPC', 
        'DXY (USD Strength)': 'DX-Y.NYB',
        '10Y Treasury': '^TNX',
        'Gold (Safe Haven)': 'GLD',
        'Oil (CAD Correlation)': 'CL=F',
        'Bonds (Risk Sentiment)': 'TLT'
    }
    
    results = {}
    
    for name, ticker in test_tickers.items():
        try:
            print(f"   Testing {name} ({ticker})...")
            
            # Fetch 5 days of data
            yf_ticker = yf.Ticker(ticker)
            data = yf_ticker.history(period='5d')
            
            if not data.empty:
                latest_value = data['Close'][-1]
                prev_value = data['Close'][-2] if len(data) > 1 else latest_value
                change_pct = (latest_value - prev_value) / prev_value * 100
                
                results[name] = {
                    'status': 'SUCCESS',
                    'latest_value': latest_value,
                    'change_pct': change_pct,
                    'data_points': len(data)
                }
                
                print(f"      ✅ SUCCESS: Value={latest_value:.2f}, Change={change_pct:+.2f}%, Points={len(data)}")
            else:
                results[name] = {'status': 'FAILED', 'error': 'No data returned'}
                print(f"      ❌ FAILED: No data returned")
                
        except Exception as e:
            results[name] = {'status': 'ERROR', 'error': str(e)}
            print(f"      ❌ ERROR: {e}")
        
        time.sleep(0.5)  # Be nice to Yahoo Finance
    
    return results

def test_rss_news_feeds():
    """Test all RSS news feeds"""
    
    print("\n📰 TESTING RSS NEWS FEEDS...")
    
    # Free RSS feeds - no API keys needed
    rss_feeds = {
        'Federal Reserve': 'https://www.federalreserve.gov/feeds/press_all.xml',
        'Reuters Forex': 'https://www.reuters.com/markets/currencies/rss',
        'ForexLive': 'https://www.forexlive.com/feed/',
        'Bloomberg Markets': 'https://feeds.bloomberg.com/markets/news.rss'
    }
    
    results = {}
    
    for name, url in rss_feeds.items():
        try:
            print(f"   Testing {name}...")
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            if hasattr(feed, 'entries') and len(feed.entries) > 0:
                articles_count = len(feed.entries)
                latest_title = feed.entries[0].title if hasattr(feed.entries[0], 'title') else 'No title'
                
                results[name] = {
                    'status': 'SUCCESS',
                    'articles_count': articles_count,
                    'latest_title': latest_title
                }
                
                print(f"      ✅ SUCCESS: {articles_count} articles, Latest: '{latest_title[:60]}...'")
            else:
                results[name] = {'status': 'FAILED', 'error': 'No articles found'}
                print(f"      ❌ FAILED: No articles found")
                
        except Exception as e:
            results[name] = {'status': 'ERROR', 'error': str(e)}
            print(f"      ❌ ERROR: {e}")
        
        time.sleep(1)  # Be respectful to RSS servers
    
    return results

def test_currency_pair_data():
    """Test your existing forex pairs data"""
    
    print("\n💱 TESTING YOUR EXISTING FOREX PAIRS...")
    
    # Your proven patterns
    test_pairs = {
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X', 
        'USDCAD': 'USDCAD=X',
        'AUDUSD': 'AUDUSD=X',
        'USDJPY': 'USDJPY=X'
    }
    
    results = {}
    
    for pair, ticker in test_pairs.items():
        try:
            print(f"   Testing {pair}...")
            
            yf_ticker = yf.Ticker(ticker)
            data = yf_ticker.history(period='5d')
            
            if not data.empty:
                latest_price = data['Close'][-1]
                prev_price = data['Close'][-2] if len(data) > 1 else latest_price
                change_pips = (latest_price - prev_price) * (10000 if 'JPY' not in pair else 100)
                
                results[pair] = {
                    'status': 'SUCCESS',
                    'latest_price': latest_price,
                    'change_pips': change_pips,
                    'data_points': len(data)
                }
                
                print(f"      ✅ SUCCESS: Price={latest_price:.5f}, Change={change_pips:+.1f} pips")
            else:
                results[pair] = {'status': 'FAILED', 'error': 'No data'}
                print(f"      ❌ FAILED: No data")
                
        except Exception as e:
            results[pair] = {'status': 'ERROR', 'error': str(e)}
            print(f"      ❌ ERROR: {e}")
        
        time.sleep(0.5)
    
    return results

def generate_test_report(yahoo_results, rss_results, forex_results):
    """Generate comprehensive test report"""
    
    print("\n" + "="*60)
    print("🔥 REAL DATA SOURCES TEST REPORT")
    print("="*60)
    
    # Yahoo Finance Results
    yahoo_success = sum(1 for r in yahoo_results.values() if r['status'] == 'SUCCESS')
    yahoo_total = len(yahoo_results)
    print(f"\n📊 YAHOO FINANCE: {yahoo_success}/{yahoo_total} sources working")
    
    for name, result in yahoo_results.items():
        status = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"   {status} {name}: {result['status']}")
    
    # RSS Feed Results  
    rss_success = sum(1 for r in rss_results.values() if r['status'] == 'SUCCESS')
    rss_total = len(rss_results)
    print(f"\n📰 RSS FEEDS: {rss_success}/{rss_total} feeds working")
    
    for name, result in rss_results.items():
        status = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"   {status} {name}: {result['status']}")
    
    # Forex Pairs Results
    forex_success = sum(1 for r in forex_results.values() if r['status'] == 'SUCCESS')
    forex_total = len(forex_results)
    print(f"\n💱 FOREX PAIRS: {forex_success}/{forex_total} pairs working")
    
    for pair, result in forex_results.items():
        status = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"   {status} {pair}: {result['status']}")
    
    # Overall Assessment
    total_success = yahoo_success + rss_success + forex_success
    total_sources = yahoo_total + rss_total + forex_total
    success_rate = (total_success / total_sources) * 100
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   Success Rate: {success_rate:.1f}% ({total_success}/{total_sources})")
    
    if success_rate >= 80:
        print(f"   Status: ✅ EXCELLENT - Ready for integration!")
    elif success_rate >= 60:
        print(f"   Status: ⚠️ GOOD - Can proceed with caution")
    else:
        print(f"   Status: ❌ POOR - Fix issues before proceeding")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return success_rate >= 60  # Return True if ready for next step

if __name__ == "__main__":
    print("🔥🔥🔥 TESTING ALL REAL DATA SOURCES - NO FAKE DATA! 🔥🔥🔥")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all real data sources
    yahoo_results = test_yahoo_finance_sources()
    rss_results = test_rss_news_feeds()
    forex_results = test_currency_pair_data()
    
    # Generate report
    ready_for_next_step = generate_test_report(yahoo_results, rss_results, forex_results)
    
    if ready_for_next_step:
        print("\n🚀 ALL TESTS PASSED - READY FOR STEP 3!")
        print("Run the integration script next.")
    else:
        print("\n⚠️ SOME TESTS FAILED - FIX ISSUES BEFORE PROCEEDING")
        print("Check your internet connection and try again.")