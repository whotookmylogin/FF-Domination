#!/usr/bin/env python3
"""
Debug Firecrawl to see what content is actually being scraped
"""

import json
import logging
from src.platforms.espn_firecrawl import ESPNFirecrawlIntegration

logging.basicConfig(level=logging.INFO)

def test_firecrawl_scraping():
    print("Testing Firecrawl Transaction Scraping")
    print("=" * 50)
    
    firecrawl = ESPNFirecrawlIntegration()
    
    if not firecrawl.enabled:
        print("❌ Firecrawl is not enabled")
        return
    
    print("✓ Firecrawl is enabled")
    
    # Test with your league ID
    league_id = "83806"
    year = 2024
    
    # Directly test scraping to see what we get
    url = f"https://fantasy.espn.com/football/league/transactions?leagueId={league_id}&seasonId={year}"
    print(f"\nScraping URL: {url}")
    
    try:
        # Scrape the page
        scrape_result = firecrawl.app.scrape_url(url, formats=['markdown', 'html'])
        
        if scrape_result:
            print(f"\n✓ Scraping successful!")
            print(f"Response type: {type(scrape_result)}")
            print(f"Response attributes: {dir(scrape_result)}")
            
            # Try to access markdown content
            markdown_content = None
            if hasattr(scrape_result, 'markdown'):
                markdown_content = scrape_result.markdown
            elif hasattr(scrape_result, 'content'):
                markdown_content = scrape_result.content
            elif isinstance(scrape_result, dict) and 'markdown' in scrape_result:
                markdown_content = scrape_result['markdown']
            
            if markdown_content:
                print(f"\nMarkdown content length: {len(markdown_content)} characters")
                
                # Save to file
                with open('firecrawl_output.md', 'w') as f:
                    f.write(markdown_content)
                print("✓ Saved markdown content to firecrawl_output.md")
                
                # Show first 500 characters
                print("\nFirst 500 characters of scraped content:")
                print("-" * 40)
                print(markdown_content[:500])
                print("-" * 40)
                
                # Look for transaction keywords
                keywords = ['trade', 'drop', 'add', 'waiver', 'transaction', 'move']
                for keyword in keywords:
                    count = markdown_content.lower().count(keyword)
                    if count > 0:
                        print(f"Found '{keyword}': {count} times")
            
            # Also check HTML if available
            html_content = None
            if hasattr(scrape_result, 'html'):
                html_content = scrape_result.html
            elif isinstance(scrape_result, dict) and 'html' in scrape_result:
                html_content = scrape_result['html']
            
            if html_content:
                print(f"\nHTML content length: {len(html_content)} characters")
                
                # Save to file
                with open('firecrawl_output.html', 'w') as f:
                    f.write(html_content)
                print("✓ Saved HTML content to firecrawl_output.html")
        else:
            print("❌ Scraping returned no result")
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")

if __name__ == "__main__":
    test_firecrawl_scraping()