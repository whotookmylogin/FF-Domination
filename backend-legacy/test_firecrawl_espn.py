# Firecrawl ESPN Data Extraction Test
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Try to import Firecrawl
    from firecrawl import FirecrawlApp
    print("✓ Firecrawl SDK imported successfully")
    
    # Get API key from environment
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("⚠ FIRECRAWL_API_KEY not found in environment variables")
        print("Please set FIRECRAWL_API_KEY in your .env file to test Firecrawl integration")
        exit(1)
    
    # Initialize Firecrawl app
    app = FirecrawlApp(api_key=api_key)
    print("✓ Firecrawl app initialized")
    
    # Test scraping an ESPN fantasy football page
    # Using a public ESPN page for testing
    test_url = "https://www.espn.com/fantasy/football/"
    print(f"\nTesting scrape of: {test_url}")
    
    # Scrape the page
    scrape_result = app.scrape_url(test_url, formats=['markdown', 'html'])
    
    if scrape_result:
        print("✓ Page scraped successfully")
        print(f"Content length: {len(str(scrape_result))} characters")
        
        # Show a preview of the markdown content
        if 'markdown' in scrape_result:
            markdown_content = scrape_result['markdown']
            print("\nMarkdown preview (first 500 chars):")
            print(markdown_content[:500] if len(markdown_content) > 500 else markdown_content)
        
        # Show metadata
        if 'metadata' in scrape_result:
            print("\nMetadata:")
            for key, value in scrape_result['metadata'].items():
                print(f"  {key}: {value}")
    else:
        print("✗ Failed to scrape page")
        
except ImportError as e:
    print("✗ Firecrawl SDK not installed")
    print("Please install it with: pip install firecrawl-py")
    
except Exception as e:
    print(f"✗ Error testing Firecrawl: {e}")
    print("This might be due to network issues or invalid API key")

print("\n" + "=" * 50)
print("Firecrawl ESPN Data Extraction Test Complete")
print("=" * 50)
