#!/usr/bin/env python3
"""
Quick ESPN scraper - checks if you're logged in and scrapes immediately
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os

async def quick_scrape():
    print("Quick ESPN Transaction Scraper")
    print("=" * 50)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # Visible browser
    context = await browser.new_context()
    page = await context.new_page()
    
    # Navigate directly to transactions
    league_id = "83806"
    year = 2024
    url = f"https://fantasy.espn.com/football/league/transactions?leagueId={league_id}&seasonId={year}"
    
    print(f"\nOpening: {url}")
    await page.goto(url)
    
    # Check every 2 seconds if we're logged in
    for i in range(30):  # Try for 60 seconds
        print(f"\rChecking login status... {i*2}/60 seconds", end="")
        
        # Check if we're on a login page or the actual transactions page
        current_url = page.url
        page_content = await page.content()
        
        # If we see transaction-related elements, we're logged in
        if "Transaction" in page_content or "Trade" in page_content or "Add" in page_content:
            print("\n\n✅ Logged in! Scraping transactions...")
            
            try:
                # Try multiple selectors
                selectors = [
                    '.Table__TBODY tr',
                    '.transactions-table tr',
                    'tr[class*="Table"]',
                    '.table-row',
                    'div[class*="transaction"]'
                ]
                
                transactions = []
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        for element in elements[:10]:  # Get first 10
                            text = await element.inner_text()
                            if text.strip():
                                transactions.append({
                                    'selector': selector,
                                    'text': text.strip()
                                })
                        break
                
                if not transactions:
                    # Fallback: get all text content
                    print("Using fallback: getting all text content")
                    all_text = await page.inner_text('body')
                    lines = all_text.split('\n')
                    
                    # Look for transaction-like patterns
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['traded', 'dropped', 'added', 'waiver', 'transaction']):
                            transactions.append({
                                'type': 'text_match',
                                'text': line.strip()
                            })
                
                if transactions:
                    print(f"\n✅ Found {len(transactions)} transactions!")
                    
                    # Save to file
                    with open('scraped_transactions.json', 'w') as f:
                        json.dump({
                            'status': 'success',
                            'league_id': league_id,
                            'year': year,
                            'url': url,
                            'transaction_count': len(transactions),
                            'transactions': transactions
                        }, f, indent=2)
                    
                    print("📁 Saved to scraped_transactions.json")
                    
                    # Show first few
                    for i, txn in enumerate(transactions[:3]):
                        print(f"\nTransaction {i+1}:")
                        print(f"  {txn.get('text', txn)[:150]}...")
                else:
                    print("⚠️ Logged in but no transactions found")
                    
                    # Save page for debugging
                    with open('page_content.html', 'w') as f:
                        f.write(page_content)
                    print("📁 Saved page content to page_content.html for debugging")
                
                break
            except Exception as e:
                print(f"\n❌ Error during scraping: {e}")
                
        elif "login" in current_url.lower() or "signin" in current_url.lower():
            if i == 0:
                print("\n📝 Please log in...")
        
        await asyncio.sleep(2)
    else:
        print("\n\n⏰ Timeout - couldn't detect login")
        print("Current URL:", page.url)
    
    print("\n\nKeeping browser open for 30 more seconds...")
    await asyncio.sleep(30)
    
    await browser.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(quick_scrape())