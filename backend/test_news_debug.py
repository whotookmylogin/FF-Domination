#!/usr/bin/env python3
"""
Debug script for news service issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(level=logging.DEBUG)

from src.news.service import NewsAggregationService
from src.news.sources import ESPNNewsSource, NFLNewsSource, RotowireNewsSource
import json

def test_individual_sources():
    """Test each news source individually"""
    print("Testing News Sources Individually...")
    print("=" * 50)
    
    # Test ESPN News
    print("\n1. Testing ESPN News Source...")
    try:
        espn = ESPNNewsSource()
        espn_news = espn.get_news()
        print(f"   ✅ ESPN returned {len(espn_news)} items")
        if espn_news:
            print(f"   Sample: {espn_news[0].get('title', 'No title')[:60]}...")
    except Exception as e:
        print(f"   ❌ ESPN Error: {e}")
    
    # Test NFL News
    print("\n2. Testing NFL News Source...")
    try:
        nfl = NFLNewsSource()
        nfl_news = nfl.get_news()
        print(f"   ✅ NFL returned {len(nfl_news)} items")
        if nfl_news:
            print(f"   Sample: {nfl_news[0].get('title', 'No title')[:60]}...")
    except Exception as e:
        print(f"   ❌ NFL Error: {e}")
    
    # Test Rotowire News
    print("\n3. Testing Rotowire News Source...")
    try:
        roto = RotowireNewsSource()
        roto_news = roto.get_news()
        print(f"   ✅ Rotowire returned {len(roto_news)} items")
        if roto_news:
            print(f"   Sample: {roto_news[0].get('title', 'No title')[:60]}...")
    except Exception as e:
        print(f"   ❌ Rotowire Error: {e}")

def test_aggregation_service():
    """Test the aggregation service"""
    print("\n" + "=" * 50)
    print("Testing News Aggregation Service...")
    print("=" * 50)
    
    try:
        # Initialize service with Perplexity API key if available
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        if perplexity_key:
            print("Perplexity API key found, initializing with AI news...")
        else:
            print("No Perplexity API key found, using basic sources only")
        
        service = NewsAggregationService(perplexity_api_key=perplexity_key)
        
        # Test aggregate_news
        print("\nCalling aggregate_news()...")
        all_news = service.aggregate_news()
        
        print(f"\n✅ Total news items: {len(all_news)}")
        
        # Count by source
        sources_count = {}
        for item in all_news:
            source = item.get('source', 'Unknown')
            sources_count[source] = sources_count.get(source, 0) + 1
        
        print("\nNews by source:")
        for source, count in sources_count.items():
            print(f"   {source}: {count} items")
        
        # Sample output
        if all_news:
            print("\nSample news items:")
            for item in all_news[:3]:
                print(f"\n   Title: {item.get('title', 'No title')[:80]}")
                print(f"   Source: {item.get('source', 'Unknown')}")
                print(f"   TLDR: {item.get('tldr', 'No summary')[:80]}")
                print(f"   Urgency: {item.get('urgency', 0)}")
        
    except Exception as e:
        print(f"\n❌ Aggregation Error: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("\n" + "=" * 50)
    print("Testing API Endpoint...")
    print("=" * 50)
    
    import requests
    try:
        response = requests.get("http://localhost:8000/news/aggregated", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API returned: {data.get('status', 'Unknown status')}")
            print(f"   Items count: {data.get('count', 0)}")
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.Timeout:
        print("❌ API request timed out after 5 seconds")
    except requests.ConnectionError:
        print("❌ Could not connect to API (is server running?)")
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    test_individual_sources()
    test_aggregation_service()
    test_api_endpoint()