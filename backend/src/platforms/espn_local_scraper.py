"""
ESPN Local Browser Scraper using Playwright
Runs locally with your actual ESPN session
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright
import json
import os

class ESPNLocalScraper:
    def __init__(self):
        """Initialize local ESPN scraper with Playwright"""
        self.browser = None
        self.context = None
        self.page = None
        self.espn_cookie = os.getenv("ESPN_COOKIE", "")
        
    async def initialize(self, headless: bool = True):
        """
        Initialize browser with ESPN cookies
        Args:
            headless: Run browser in headless mode (False to see what's happening)
        """
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        
        # Add ESPN cookies if available
        if self.espn_cookie:
            cookies = self._parse_cookie_string(self.espn_cookie)
            await self.context.add_cookies(cookies)
            logging.info("Added ESPN authentication cookies to browser")
        
        self.page = await self.context.new_page()
        
    def _parse_cookie_string(self, cookie_string: str) -> list:
        """Parse ESPN cookie string into Playwright format"""
        cookies = []
        for cookie_pair in cookie_string.split(';'):
            if '=' in cookie_pair:
                name, value = cookie_pair.strip().split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.espn.com',
                    'path': '/'
                })
        return cookies
    
    async def get_transactions(self, league_id: str, year: int = 2024) -> Dict[str, Any]:
        """
        Scrape transactions from ESPN using local browser
        
        Args:
            league_id: ESPN league ID
            year: Season year
            
        Returns:
            Dictionary containing transaction data
        """
        if not self.page:
            await self.initialize()
        
        url = f"https://fantasy.espn.com/football/league/transactions?leagueId={league_id}&seasonId={year}"
        logging.info(f"Navigating to: {url}")
        
        try:
            # Navigate to transactions page
            await self.page.goto(url, wait_until='networkidle')
            
            # Wait for content to load
            await self.page.wait_for_selector('.Table', timeout=10000)
            
            # Extract transaction data
            transactions = await self.page.evaluate('''
                () => {
                    const transactions = [];
                    const rows = document.querySelectorAll('.Table__TBODY tr');
                    
                    rows.forEach(row => {
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 3) {
                            const date = cells[0]?.innerText?.trim();
                            const type = cells[1]?.innerText?.trim();
                            const details = cells[2]?.innerText?.trim();
                            
                            if (date && details) {
                                transactions.push({
                                    date: date,
                                    type: type || 'Transaction',
                                    details: details
                                });
                            }
                        }
                    });
                    
                    return transactions;
                }
            ''')
            
            logging.info(f"Successfully scraped {len(transactions)} transactions")
            
            return {
                'status': 'success',
                'source': 'local_browser',
                'league_id': league_id,
                'year': year,
                'transactions': transactions
            }
            
        except Exception as e:
            logging.error(f"Error scraping transactions: {e}")
            
            # Check if we're on a login page
            current_url = self.page.url
            if 'login' in current_url.lower():
                return {
                    'status': 'error',
                    'message': 'Not authenticated - please log into ESPN in your browser first',
                    'current_url': current_url
                }
            
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def get_roster(self, league_id: str, team_id: str, year: int = 2024) -> Dict[str, Any]:
        """
        Scrape roster data from ESPN using local browser
        """
        if not self.page:
            await self.initialize()
        
        url = f"https://fantasy.espn.com/football/team?leagueId={league_id}&teamId={team_id}&seasonId={year}"
        logging.info(f"Navigating to: {url}")
        
        try:
            await self.page.goto(url, wait_until='networkidle')
            await self.page.wait_for_selector('.Table', timeout=10000)
            
            # Extract roster data
            roster = await self.page.evaluate('''
                () => {
                    const players = [];
                    const rows = document.querySelectorAll('.Table__TBODY tr');
                    
                    rows.forEach(row => {
                        const nameElement = row.querySelector('.player-column__athlete');
                        const posElement = row.querySelector('.playerinfo__playerpos');
                        const teamElement = row.querySelector('.playerinfo__playerteam');
                        
                        if (nameElement) {
                            players.push({
                                name: nameElement.innerText.trim(),
                                position: posElement?.innerText?.trim() || 'Unknown',
                                team: teamElement?.innerText?.trim() || 'FA'
                            });
                        }
                    });
                    
                    return players;
                }
            ''')
            
            return {
                'status': 'success',
                'source': 'local_browser',
                'players': roster
            }
            
        except Exception as e:
            logging.error(f"Error scraping roster: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()

# Example usage
async def test_local_scraper():
    scraper = ESPNLocalScraper()
    
    # Run with headless=False to see the browser
    await scraper.initialize(headless=False)
    
    # Get transactions
    transactions = await scraper.get_transactions('83806', 2024)
    print(json.dumps(transactions, indent=2))
    
    # Clean up
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_local_scraper())