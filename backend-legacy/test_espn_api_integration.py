# Test ESPN API Integration
import os
import sys
from dotenv import load_dotenv
from src.platforms.service import PlatformIntegrationService

# Load environment variables
load_dotenv()

try:
    # Get ESPN credentials from environment
    espn_cookie = os.getenv("ESPN_COOKIE")
    if not espn_cookie:
        print("⚠ ESPN_COOKIE not found in environment variables")
        print("Please set ESPN_COOKIE in your .env file with your ESPN s2 cookie and SWID")
        exit(1)
    
    print("Testing ESPN API Integration with PlatformIntegrationService")
    print("=" * 60)
    
    # Initialize the platform service
    platform_service = PlatformIntegrationService(espn_cookie=espn_cookie)
    
    # Test 1: Check if ESPN API integration is initialized
    if platform_service.espn_api_integration:
        print("✓ ESPN API integration (community library) is initialized")
    else:
        print("⚠ ESPN API integration (community library) is not initialized")
    
    # Test 2: Test user data fetching
    print("\n1. Testing user data fetching:")
    user_id = "1"  # Test with first team ID from our previous test
    user_data = platform_service.get_user_data("espn", user_id)
    if user_data:
        print(f"  ✓ Successfully fetched user data for team ID {user_id}")
        print(f"  Team Name: {user_data.get('team_name', 'N/A')}")
        print(f"  Record: {user_data.get('wins', 0)}-{user_data.get('losses', 0)}-{user_data.get('ties', 0)}")
    else:
        print(f"  ✗ Failed to fetch user data for team ID {user_id}")
    
    # Test 3: Test roster data fetching
    print("\n2. Testing roster data fetching:")
    roster_data = platform_service.get_league_data("espn", user_id)  # Using user_id as league_id parameter
    if roster_data is not None:
        print(f"  ✓ Successfully fetched roster data")
        print(f"  Number of players: {len(roster_data) if isinstance(roster_data, list) else 'N/A'}")
    else:
        print(f"  ✗ Failed to fetch roster data")
    
    # Test 4: Test transactions data fetching
    print("\n3. Testing transactions data fetching:")
    transactions_data = platform_service.get_transactions_data("espn", user_id)  # Using user_id as league_id parameter
    if transactions_data is not None:
        print(f"  ✓ Successfully fetched transactions data")
        print(f"  Number of transactions: {len(transactions_data) if isinstance(transactions_data, list) else 'N/A'}")
    else:
        print(f"  ✗ Failed to fetch transactions data")
    
    print("\n" + "=" * 60)
    print("ESPN API Integration Test Complete")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Error testing ESPN API integration: {e}")
    import traceback
    traceback.print_exc()
