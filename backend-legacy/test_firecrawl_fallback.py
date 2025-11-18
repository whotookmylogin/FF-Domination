# Firecrawl Fallback Test
import os
import sys
import logging
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.platforms.service import PlatformIntegrationService

def test_firecrawl_fallback():
    """Test the Firecrawl fallback functionality."""
    print("=" * 50)
    print("Firecrawl Fallback Test")
    print("=" * 50)
    
    # Get credentials from environment
    espn_cookie = os.getenv("ESPN_COOKIE")
    sleeper_token = os.getenv("SLEEPER_TOKEN")
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not espn_cookie:
        print("⚠ ESPN_COOKIE not found in environment variables")
        print("Please set ESPN_COOKIE in your .env file")
        return
    
    # Initialize the platform service
    platform_service = PlatformIntegrationService(espn_cookie=espn_cookie, sleeper_token=sleeper_token)
    
    # Test ESPN roster data with fallback
    print("\n1. Testing ESPN roster data with Firecrawl fallback:")
    print("   (This will fail with ESPN API but may work with Firecrawl)")
    
    roster_data = platform_service.get_league_data("espn", "83806", 2023)
    
    if roster_data:
        print("✓ Data retrieved successfully")
        print(f"  Source: {roster_data.get('source', 'espn_api')}")
        print(f"  Status: {roster_data.get('status', 'unknown')}")
    else:
        print("✗ Failed to retrieve roster data")
        print("  Both ESPN API and Firecrawl fallback failed")
    
    # Test ESPN transactions data with fallback
    print("\n2. Testing ESPN transactions data with Firecrawl fallback:")
    print("   (This will fail with ESPN API but may work with Firecrawl)")
    
    transactions_data = platform_service.get_transactions_data("espn", "83806", 2023, 1)
    
    if transactions_data:
        print("✓ Data retrieved successfully")
        print(f"  Source: {transactions_data.get('source', 'espn_api')}")
        print(f"  Status: {transactions_data.get('status', 'unknown')}")
    else:
        print("✗ Failed to retrieve transactions data")
        print("  Both ESPN API and Firecrawl fallback failed")
    
    # Test ESPN user data with fallback
    print("\n3. Testing ESPN user data with Firecrawl fallback:")
    print("   (This will fail with ESPN API but may work with Firecrawl)")
    print("   (Skipping user data test - need user ID)")
    
    print("\n" + "=" * 50)
    print("Firecrawl Fallback Test Complete")
    print("=" * 50)
    
    # Show Firecrawl status
    if platform_service.espn_firecrawl_integration:
        if platform_service.espn_firecrawl_integration.enabled:
            print("✓ Firecrawl integration is enabled and ready")
        else:
            print("⚠ Firecrawl integration is disabled")
            if not firecrawl_api_key or firecrawl_api_key == "your_firecrawl_api_key_here":
                print("  Reason: FIRECRAWL_API_KEY not set or invalid in .env file")
                print("  To enable Firecrawl, get an API key from firecrawl.dev and set it in .env")
    else:
        print("✗ Firecrawl integration not available")
        print("  Reason: Firecrawl SDK not installed")
        print("  To enable Firecrawl, install it with: pip install firecrawl-py")

if __name__ == "__main__":
    test_firecrawl_fallback()
