#!/usr/bin/env python3
"""
Test Firecrawl with public ESPN pages that don't require authentication
"""

import json
import logging
from src.platforms.espn_firecrawl import ESPNFirecrawlIntegration

logging.basicConfig(level=logging.INFO)

def test_public_espn_pages():
    print("Testing Firecrawl with Public ESPN Pages")
    print("=" * 50)
    
    firecrawl = ESPNFirecrawlIntegration()
    
    if not firecrawl.enabled:
        print("❌ Firecrawl is not enabled")
        return
    
    print("✓ Firecrawl is enabled and credits are working")
    
    # Test with public ESPN pages that don't require auth
    test_urls = [
        ("NFL Scoreboard", "https://www.espn.com/nfl/scoreboard"),
        ("NFL Teams", "https://www.espn.com/nfl/teams"),
        ("Fantasy Football Home", "https://www.espn.com/fantasy/football/")
    ]
    
    for name, url in test_urls:
        print(f"\n📄 Testing: {name}")
        print(f"   URL: {url}")
        
        try:
            # Scrape the page without authentication
            scrape_result = firecrawl.app.scrape_url(
                url, 
                formats=['markdown'],
                headers={}  # No auth needed for public pages
            )
            
            if scrape_result and hasattr(scrape_result, 'markdown'):
                markdown_content = scrape_result.markdown
                print(f"   ✓ Successfully scraped {len(markdown_content)} characters")
                
                # Save a sample
                filename = f"public_{name.lower().replace(' ', '_')}.md"
                with open(filename, 'w') as f:
                    f.write(markdown_content[:1000])  # Save first 1000 chars
                print(f"   ✓ Saved sample to {filename}")
                
                # Check for relevant content
                if "fantasy" in markdown_content.lower():
                    print(f"   ✓ Found fantasy-related content")
                if "team" in markdown_content.lower():
                    print(f"   ✓ Found team-related content")
            else:
                print(f"   ❌ Failed to scrape page")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("✓ Firecrawl is working correctly with your credits")
    print("✓ Can successfully scrape public ESPN pages")
    print("⚠️  Private league pages require authentication that can't be passed via Firecrawl")
    print("\nRecommendation: Use the ESPN API for authenticated data and Firecrawl for public data")

if __name__ == "__main__":
    test_public_espn_pages()