#!/usr/bin/env python3
"""
Test script for Sleeper integration
Tests the updated Sleeper API service and platform integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.platforms.sleeper import SleeperIntegration
from src.platforms.service import PlatformIntegrationService

def test_sleeper_basic():
    """Test basic Sleeper integration without authentication"""
    print("Testing Sleeper Integration...")
    
    # Test initialization without token (public API)
    sleeper = SleeperIntegration()
    print("✓ Sleeper integration initialized successfully")
    
    # Test getting a public user (using a known Sleeper user)
    test_username = "josh"  # Known Sleeper user
    print(f"\nTesting user lookup for: {test_username}")
    
    user_data = sleeper.get_user_data(test_username)
    if user_data:
        print(f"✓ User found: {user_data.get('display_name', 'Unknown')}")
        print(f"  User ID: {user_data.get('user_id', 'Unknown')}")
        
        # Test getting user's leagues
        print(f"\nTesting leagues for user: {user_data.get('user_id')}")
        leagues = sleeper.get_user_leagues(user_data.get('user_id'), '2024')
        if leagues:
            print(f"✓ Found {len(leagues)} leagues")
            if leagues:
                print(f"  Sample league: {leagues[0].get('name', 'Unknown')}")
        else:
            print("! No leagues found for user")
    else:
        print(f"✗ Failed to find user: {test_username}")
    
    print("\n" + "="*50)

def test_platform_service():
    """Test the platform service with Sleeper"""
    print("Testing Platform Service with Sleeper...")
    
    # Initialize platform service
    platform_service = PlatformIntegrationService()
    print("✓ Platform service initialized")
    
    # Test Sleeper user lookup through platform service
    test_username = "josh"
    print(f"\nTesting platform service user lookup: {test_username}")
    
    user_data = platform_service.get_user_data("sleeper", test_username)
    if user_data:
        print(f"✓ User found via platform service: {user_data.get('display_name', 'Unknown')}")
        
        # Test getting leagues through platform service
        user_id = user_data.get('user_id')
        if user_id:
            print(f"\nTesting platform service leagues lookup for: {user_id}")
            leagues = platform_service.get_sleeper_user_leagues(user_id, '2024')
            if leagues:
                print(f"✓ Found {len(leagues)} leagues via platform service")
            else:
                print("! No leagues found via platform service")
    else:
        print(f"✗ Failed to find user via platform service: {test_username}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    print("Sleeper Integration Test Suite")
    print("="*50)
    
    try:
        test_sleeper_basic()
        test_platform_service()
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()