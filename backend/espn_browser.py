#!/usr/bin/env python3
"""
Opens ESPN in a browser with your cookies for manual interaction
After logging in, it will attempt to scrape transactions
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os

async def open_espn_browser():
    print("Opening ESPN Fantasy in browser...")
    print("=" * 50)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # Visible browser
    context = await browser.new_context()
    
    # Add ESPN cookies from .env if available
    espn_cookie = os.getenv("ESPN_COOKIE", "")
    if espn_cookie:
        cookies = []
        for cookie_pair in espn_cookie.split(';'):
            if '=' in cookie_pair:
                name, value = cookie_pair.strip().split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.espn.com',
                    'path': '/'
                })
        await context.add_cookies(cookies)
        print("✓ Added ESPN cookies from .env")
    
    page = await context.new_page()
    
    # Go directly to your league's transaction page
    league_id = "83806"
    year = 2024
    url = f"https://fantasy.espn.com/football/league/transactions?leagueId={league_id}&seasonId={year}"
    
    print(f"\nNavigating to: {url}")
    await page.goto(url)
    
    print("\nBrowser opened! Please:")
    print("1. Log in if needed")
    print("2. The script will wait 30 seconds then try to scrape")
    
    # Wait for user to log in
    await asyncio.sleep(30)
    
    print("\nAttempting to scrape transactions...")
    
    try:
        # Wait for transaction table
        await page.wait_for_selector('.Table', timeout=5000)
        
        # Extract transactions
        transactions = await page.evaluate('''
            () => {
                const transactions = [];
                const rows = document.querySelectorAll('.Table__TBODY tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const text = row.innerText;
                        if (text && text.trim()) {
                            transactions.push({
                                raw_text: text.trim()
                            });
                        }
                    }
                });
                
                return transactions;
            }
        ''')
        
        if transactions:
            print(f"\n✅ Found {len(transactions)} transactions!")
            
            # Save to file
            with open('scraped_transactions.json', 'w') as f:
                json.dump({'transactions': transactions}, f, indent=2)
            print("📁 Saved to scraped_transactions.json")
            
            # Show first few
            for i, txn in enumerate(transactions[:3]):
                print(f"\nTransaction {i+1}: {txn['raw_text'][:100]}...")
        else:
            print("❌ No transactions found")
            
    except Exception as e:
        print(f"❌ Error scraping: {e}")
        print("\nTry logging in manually in the browser window")
    
    print("\n⏰ Browser will stay open for 2 minutes for you to explore...")
    await asyncio.sleep(120)
    
    await browser.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(open_espn_browser())