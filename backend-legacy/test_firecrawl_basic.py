# Basic Firecrawl Test
import os
import logging
from dotenv import load_dotenv
from src.platforms.espn_firecrawl import ESPNFirecrawlIntegration

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

try:
    print("Basic Firecrawl Test")
    print("=" * 30)
    
    # Initialize Firecrawl integration
    firecrawl = ESPNFirecrawlIntegration()
    
    if firecrawl.enabled:
        print("✓ Firecrawl integration is enabled")
        print(f"  API Key: {os.getenv('FIRECRAWL_API_KEY')[:5]}... (truncated for security)")
        
        # Test basic data extraction
        print("\nTesting data extraction from sample content:")
        sample_content = """
        # Fantasy Football Team Roster
        
        ## Team Name: Test Team
        
        ### Players
        1. Player A - QB
        2. Player B - RB
        3. Player C - WR
        """
        
        extracted = firecrawl._extract_data_from_markdown(sample_content, "roster")
        if extracted:
            print("  ✓ Data extraction working")
            print(f"  Extracted data type: {extracted.get('status', 'N/A')}")
        else:
            print("  ✗ Data extraction failed")
            
        print("\nFirecrawl integration is ready for use as fallback")
        print("Note: Actual scraping may fail due to ESPN authentication requirements")
        
    else:
        print("⚠ Firecrawl integration is not enabled")
        print("  Please check your FIRECRAWL_API_KEY in .env")
    
    print("\n" + "=" * 30)
    print("Basic Firecrawl Test Complete")
    
except Exception as e:
    print(f"✗ Error testing Firecrawl integration: {e}")
    import traceback
    traceback.print_exc()
