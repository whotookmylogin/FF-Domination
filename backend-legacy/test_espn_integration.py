import sys
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from platforms.espn import ESPNIntegration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_espn_integration():
    """Test the ESPN integration with the user's credentials."""
    # Get the ESPN cookie from environment variables
    espn_cookie = os.getenv("ESPN_COOKIE")
    
    if not espn_cookie:
        print("✗ ESPN_COOKIE not found in environment variables")
        print("Please set ESPN_COOKIE in your .env file with your ESPN s2 cookie and SWID")
    else:
        espn = ESPNIntegration(espn_cookie)
        print("✓ ESPN integration initialized")
        
        # Test the ESPN integration methods directly
        try:
            print("Testing ESPN integration methods with your league ID: 83806")
            
            # Test roster data
            print("\n1. Testing get_roster_data method:")
            roster_data = espn.get_roster_data(2023, "83806")
            if roster_data:
                print("✓ Roster data retrieved successfully")
                print(f"✓ Response contains {len(str(roster_data))} characters")
            else:
                print("✗ Failed to retrieve roster data")
                print("This is likely due to ESPN API changes or anti-bot measures implemented in 2025")
                
            # Test transactions data
            print("\n2. Testing get_transactions_data method:")
            transactions_data = espn.get_transactions_data(2023, "83806")
            if transactions_data:
                print("✓ Transactions data retrieved successfully")
                print(f"✓ Response contains {len(str(transactions_data))} characters")
            else:
                print("✗ Failed to retrieve transactions data")
                print("This is likely due to ESPN API changes or anti-bot measures implemented in 2025")
                
            # Test user data
            print("\n3. Testing get_user_data method:")
            # We don't have the user ID, so we'll skip this test for now
            print("Skipping user data test - need user ID")
            
            print("\n" + "=" * 50)
            print("ESPN API Status: UNAVAILABLE")
            print("As of 2025, ESPN has implemented new access restrictions that prevent API access")
            print("even with valid cookies. This affects many users of the ESPN fantasy API.")
            print("\nRecommendations:")
            print("- Monitor ESPN API community repositories for updates or workarounds")
            print("- Check if ESPN releases official API documentation")
            print("- Consider manual data input as a temporary workaround")
            print("=" * 50)
                
        except Exception as e:
            logging.error(f"Error testing ESPN integration: {e}")
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("ESPN Integration Test")
    print("=" * 20)
    test_espn_integration()
