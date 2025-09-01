#!/usr/bin/env python3
"""
Test script for the Fantasy Football News Aggregation Service.
This script tests all major components of the news service.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.news.service import NewsAggregationService
from src.news.sources import test_all_sources, get_all_sources
from src.cache.service import CacheService
import json

def test_cache_service():
    """Test the cache service."""
    print("🧪 Testing Cache Service...")
    
    try:
        cache_service = CacheService()
        
        # Test basic cache operations
        test_key = "test_news_key"
        test_data = {"title": "Test News", "urgency": 3}
        
        # Set cache
        result = cache_service.set(test_key, test_data, expiration_minutes=1)
        print(f"   ✅ Cache set: {result}")
        
        # Get from cache
        cached_data = cache_service.get(test_key)
        print(f"   ✅ Cache get: {cached_data == test_data}")
        
        # Delete from cache
        delete_result = cache_service.delete(test_key)
        print(f"   ✅ Cache delete: {delete_result}")
        
        return True
    except Exception as e:
        print(f"   ❌ Cache service test failed: {str(e)}")
        return False

def test_news_sources():
    """Test all news sources individually."""
    print("\n🧪 Testing News Sources...")
    
    try:
        test_results = test_all_sources()
        
        all_passed = True
        for source_name, result in test_results.items():
            if result['status'] == 'success':
                print(f"   ✅ {source_name}: {result['items_fetched']} items")
                if result.get('sample_title'):
                    print(f"      Sample: {result['sample_title'][:60]}...")
            else:
                print(f"   ❌ {source_name}: {result.get('error_message', 'Unknown error')}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"   ❌ News sources test failed: {str(e)}")
        return False

def test_news_aggregation():
    """Test the main news aggregation service."""
    print("\n🧪 Testing News Aggregation Service...")
    
    try:
        # Initialize service
        cache_service = CacheService()
        news_service = NewsAggregationService(cache_service=cache_service)
        
        # Test aggregation
        all_news = news_service.aggregate_news()
        print(f"   ✅ Aggregated {len(all_news)} news items")
        
        if all_news:
            # Test urgency distribution
            urgency_counts = {}
            for item in all_news:
                urgency = item.get('urgency_score', 1)
                urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            print(f"   ✅ Urgency distribution: {urgency_counts}")
            
            # Test deduplication
            titles = [item.get('title', '') for item in all_news]
            unique_titles = set(titles)
            print(f"   ✅ Deduplication: {len(titles)} -> {len(unique_titles)} unique items")
            
            # Test breaking news
            breaking_news = news_service.get_breaking_news(min_urgency=4)
            print(f"   ✅ Breaking news: {len(breaking_news)} high-urgency items")
            
            # Show sample news items
            print("\n   📰 Sample News Items:")
            for i, item in enumerate(all_news[:3]):
                print(f"      {i+1}. [{item.get('source', 'Unknown')}] {item.get('title', 'No title')}")
                print(f"         Urgency: {item.get('urgency_score', 1)}/5")
                print(f"         Content: {item.get('content', 'No content')[:80]}...")
                print()
        
        return True
    except Exception as e:
        print(f"   ❌ News aggregation test failed: {str(e)}")
        return False

def test_source_specific_queries():
    """Test source-specific news queries."""
    print("\n🧪 Testing Source-Specific Queries...")
    
    try:
        cache_service = CacheService()
        news_service = NewsAggregationService(cache_service=cache_service)
        
        sources = ['espn', 'nfl', 'fantasypros']
        all_passed = True
        
        for source in sources:
            try:
                source_news = news_service.get_news_by_source(source)
                print(f"   ✅ {source.upper()}: {len(source_news)} items")
                
                if source_news:
                    sample = source_news[0]
                    print(f"      Sample: {sample.get('title', 'No title')[:60]}...")
                    
            except Exception as e:
                print(f"   ❌ {source.upper()}: {str(e)}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"   ❌ Source-specific queries test failed: {str(e)}")
        return False

def test_cache_functionality():
    """Test caching functionality of the news service."""
    print("\n🧪 Testing Cache Functionality...")
    
    try:
        cache_service = CacheService()
        news_service = NewsAggregationService(cache_service=cache_service)
        
        # First call (should fetch from sources)
        print("   📥 First call (no cache)...")
        news1 = news_service.aggregate_news(use_cache=False)
        
        # Second call (should use cache)
        print("   💾 Second call (with cache)...")
        news2 = news_service.aggregate_news(use_cache=True)
        
        print(f"   ✅ Cache working: {len(news1)} items, cache returned {len(news2)} items")
        
        # Test cache refresh
        print("   🔄 Testing cache refresh...")
        refresh_result = news_service.refresh_cache()
        print(f"   ✅ Cache refresh: {refresh_result.get('status', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"   ❌ Cache functionality test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Fantasy Football News Service Test Suite")
    print("=" * 50)
    
    tests = [
        ("Cache Service", test_cache_service),
        ("News Sources", test_news_sources),
        ("News Aggregation", test_news_aggregation),
        ("Source-Specific Queries", test_source_specific_queries),
        ("Cache Functionality", test_cache_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {str(e)}")
        
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! News service is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)