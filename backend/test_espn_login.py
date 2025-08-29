#!/usr/bin/env python3
"""
ESPN Local Scraper with Manual Login
This script opens a browser window where you can log into ESPN manually
"""

import asyncio
import json
from src.platforms.espn_local_scraper import ESPNLocalScraper

async def manual_login_and_scrape():
    print("ESPN Transaction Scraper with Manual Login")
    print("=" * 50)
    
    scraper = ESPNLocalScraper()
    
    # Initialize with visible browser (headless=False)
    print("\n📱 Opening browser window...")
    await scraper.initialize(headless=False)
    
    # Navigate to ESPN login
    print("📝 Navigating to ESPN Fantasy...")
    await scraper.page.goto("https://fantasy.espn.com/football/")
    
    print("\n⏳ MANUAL STEP REQUIRED:")
    print("1. Log into ESPN in the browser window that just opened")
    print("2. Navigate to your league if needed")
    print("3. Press Enter here when you're logged in...")
    input()
    
    print("\n🔍 Attempting to fetch transactions...")
    
    # Now try to get transactions
    transactions = await scraper.get_transactions('83806', 2024)
    
    if transactions['status'] == 'success':
        print(f"\n✅ Successfully fetched {len(transactions['transactions'])} transactions!")
        
        # Show first few transactions
        for i, txn in enumerate(transactions['transactions'][:5]):
            print(f"\nTransaction {i+1}:")
            print(f"  Date: {txn.get('date', 'N/A')}")
            print(f"  Type: {txn.get('type', 'N/A')}")
            print(f"  Details: {txn.get('details', 'N/A')}")
        
        # Save all transactions to file
        with open('espn_transactions.json', 'w') as f:
            json.dump(transactions, f, indent=2)
        print(f"\n📁 All transactions saved to espn_transactions.json")
    else:
        print(f"\n❌ Failed to fetch transactions: {transactions.get('message', 'Unknown error')}")
    
    print("\n🧹 Closing browser in 5 seconds...")
    await asyncio.sleep(5)
    await scraper.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(manual_login_and_scrape())