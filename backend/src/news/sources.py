import requests
import time
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import feedparser
import html
import re

class NewsSource(ABC):
    """Abstract base class for news sources."""
    
    def __init__(self, name: str, base_url: str, rate_limit: int = 60):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit  # requests per minute
        self.requests_made = 0
        self.last_reset = time.time()
        
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        if current_time - self.last_reset > 60:
            self.requests_made = 0
            self.last_reset = current_time
        
        if self.requests_made >= self.rate_limit:
            sleep_time = 60 - (current_time - self.last_reset)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.requests_made = 0
                self.last_reset = time.time()
    
    @abstractmethod
    def get_news(self) -> List[Dict[str, Any]]:
        """Fetch news from the source."""
        pass
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML entities and formatting from text."""
        if not text:
            return ""
        # Decode HTML entities
        text = html.unescape(text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    def _generate_tldr(self, title: str, content: str) -> str:
        """Generate a TLDR summary from title and content."""
        if not content or content == "No summary available.":
            # Extract key info from title
            if "injury" in title.lower():
                return "Injury update affecting fantasy value"
            elif "trade" in title.lower():
                return "Trade news impacting team dynamics"
            elif "waiver" in title.lower():
                return "Waiver wire opportunity"
            elif any(word in title.lower() for word in ["questionable", "doubtful", "out"]):
                return "Player availability update for upcoming game"
            elif "practice" in title.lower():
                return "Practice participation update"
            else:
                # Extract first meaningful part of title
                clean_title = self._clean_text(title)
                if len(clean_title) > 60:
                    return clean_title[:60] + "..."
                return clean_title
        
        # Clean and truncate content for TLDR
        clean_content = self._clean_text(content)
        if len(clean_content) > 100:
            # Find first sentence or 100 chars
            first_sentence = clean_content.split('.')[0]
            if len(first_sentence) < 100:
                return first_sentence + "."
            return clean_content[:100] + "..."
        return clean_content

class ESPNNewsSource(NewsSource):
    """ESPN NFL News integration using both API and RSS feeds."""
    
    def __init__(self):
        super().__init__("ESPN", "https://www.espn.com", rate_limit=100)
        self.rss_url = "https://www.espn.com/espn/rss/nfl/news"
        self.api_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/news"
        
    def get_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from ESPN using both API and RSS feeds.
        
        Returns:
            list: List of news items with title, content, timestamp, and url
        """
        self._check_rate_limit()
        
        news_items = []
        
        # Try API first
        try:
            api_news = self._fetch_from_api()
            news_items.extend(api_news)
            logging.info(f"Fetched {len(api_news)} items from ESPN API")
        except Exception as e:
            logging.warning(f"ESPN API failed, trying RSS: {str(e)}")
        
        # Try RSS if API fails or returns limited results
        if len(news_items) < 5:
            try:
                rss_news = self._fetch_from_rss()
                news_items.extend(rss_news)
                logging.info(f"Fetched {len(rss_news)} items from ESPN RSS")
            except Exception as e:
                logging.error(f"ESPN RSS also failed: {str(e)}")
        
        # If both fail, return empty list (no mock data)
        if not news_items:
            logging.warning("No ESPN news available from API or RSS")
            return []
        
        return news_items
    
    def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """
        Fetch news from ESPN API.
        
        Returns:
            list: List of news items from API
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(self.api_url, headers=headers, timeout=10)
        self.requests_made += 1
        
        if response.status_code == 200:
            data = response.json()
            news_items = []
            
            for article in data.get('articles', []):
                title = self._clean_text(article.get('headline', ''))
                content = self._clean_text(article.get('description', ''))
                news_items.append({
                    'title': title,
                    'content': content,
                    'tldr': self._generate_tldr(title, content),
                    'timestamp': article.get('published', datetime.now().isoformat()),
                    'url': article.get('links', {}).get('web', {}).get('href', ''),
                    'source': self.name,
                    'urgency_score': self._calculate_urgency(article)
                })
            
            return news_items
        else:
            raise Exception(f"API request failed with status {response.status_code}")
    
    def _fetch_from_rss(self) -> List[Dict[str, Any]]:
        """
        Fetch news from ESPN RSS feed.
        
        Returns:
            list: List of news items from RSS
        """
        feed = feedparser.parse(self.rss_url)
        news_items = []
        
        for entry in feed.entries[:20]:  # Limit to 20 items
            title = self._clean_text(entry.get('title', ''))
            content = self._clean_text(entry.get('summary', ''))
            news_items.append({
                'title': title,
                'content': content,
                'tldr': self._generate_tldr(title, content),
                'timestamp': entry.get('published', datetime.now().isoformat()),
                'url': entry.get('link', ''),
                'source': self.name,
                'urgency_score': self._calculate_urgency({'title': title, 'description': content})
            })
        
        return news_items
    
    def _get_mock_espn_data(self) -> List[Dict[str, Any]]:
        """
        Return mock ESPN data for development/testing.
        
        Returns:
            list: Mock news items
        """
        mock_data = [
            {
                'title': 'NFL Injury Report: Key Players Questionable for Week 10',
                'content': 'Several star players are listed on injury reports ahead of this week\'s games...',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'url': 'https://www.espn.com/nfl/story/_/mock-injury-report',
                'source': self.name,
                'urgency_score': 4
            },
            {
                'title': 'Trade Deadline Approaches: Teams Making Final Moves',
                'content': 'With the NFL trade deadline looming, teams are finalizing roster moves...',
                'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                'url': 'https://www.espn.com/nfl/story/_/mock-trade-deadline',
                'source': self.name,
                'urgency_score': 3
            },
            {
                'title': 'Fantasy Football Week 10 Start/Sit Recommendations',
                'content': 'Our experts weigh in on which players to start and sit this week...',
                'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
                'url': 'https://www.espn.com/fantasy/football/story/_/mock-start-sit',
                'source': self.name,
                'urgency_score': 2
            }
        ]
        
        logging.info("Using mock ESPN data for development")
        return mock_data
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate urgency score for a news item (1-5).
        
        Args:
            item (dict): News item from ESPN
            
        Returns:
            int: Urgency score (1-5)
        """
        title = item.get('title', '').lower()
        content = item.get('description', '').lower()
        text = f"{title} {content}"
        
        # High urgency keywords
        if any(word in text for word in ['breaking', 'injured', 'out for season', 'suspended']):
            return 5
        elif any(word in text for word in ['injury', 'questionable', 'doubtful', 'traded']):
            return 4
        elif any(word in text for word in ['probable', 'limited', 'starting']):
            return 3
        elif any(word in text for word in ['practice', 'coach', 'update']):
            return 2
        else:
            return 1

class NFLNewsSource(NewsSource):
    """NFL.com News integration using web scraping and RSS feeds."""
    
    def __init__(self):
        super().__init__("NFL.com", "https://www.nfl.com", rate_limit=50)
        self.rss_url = "https://www.nfl.com/feeds/rss/news.xml"
        self.news_url = "https://www.nfl.com/news/"
        
    def get_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from NFL.com using RSS feeds and fallback mock data.
        
        Returns:
            list: List of news items with title, content, timestamp, and url
        """
        self._check_rate_limit()
        
        try:
            # Try RSS feed first
            return self._fetch_from_rss()
        except Exception as e:
            logging.error(f"NFL.com RSS failed: {str(e)}")
            return []  # Return empty list instead of mock data
    
    def _fetch_from_rss(self) -> List[Dict[str, Any]]:
        """
        Fetch news from NFL.com RSS feed.
        
        Returns:
            list: List of news items from RSS
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            feed = feedparser.parse(self.rss_url)
            news_items = []
            
            for entry in feed.entries[:20]:  # Limit to 20 items
                title = self._clean_text(entry.get('title', ''))
                content = self._clean_text(entry.get('summary', ''))
                news_items.append({
                    'title': title,
                    'content': content,
                    'tldr': self._generate_tldr(title, content),
                    'timestamp': entry.get('published', datetime.now().isoformat()),
                    'url': entry.get('link', ''),
                    'source': self.name,
                    'urgency_score': self._calculate_urgency({
                        'title': title,
                        'description': content
                    })
                })
            
            self.requests_made += 1
            return news_items
        except Exception as e:
            logging.error(f"RSS parsing failed: {str(e)}")
            raise
    
    def _get_mock_nfl_data(self) -> List[Dict[str, Any]]:
        """
        Return mock NFL data for development/testing.
        
        Returns:
            list: Mock news items
        """
        mock_data = [
            {
                'title': 'NFL Announces Schedule Changes Due to Weather',
                'content': 'The NFL has announced several schedule changes for Week 10 due to severe weather conditions...',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'url': 'https://www.nfl.com/news/mock-schedule-changes',
                'source': self.name,
                'urgency_score': 4
            },
            {
                'title': 'Rookie Quarterback Makes History in Monday Night Debut',
                'content': 'First-year signal caller sets multiple records in primetime victory...',
                'timestamp': (datetime.now() - timedelta(hours=8)).isoformat(),
                'url': 'https://www.nfl.com/news/mock-rookie-record',
                'source': self.name,
                'urgency_score': 3
            },
            {
                'title': 'NFL Network Announces New Fantasy Show',
                'content': 'Network executives unveil plans for comprehensive fantasy football coverage...',
                'timestamp': (datetime.now() - timedelta(hours=12)).isoformat(),
                'url': 'https://www.nfl.com/news/mock-fantasy-show',
                'source': self.name,
                'urgency_score': 2
            }
        ]
        
        logging.info("Using mock NFL data for development")
        return mock_data
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate urgency score for a news item (1-5).
        
        Args:
            item (dict): News item from NFL.com
            
        Returns:
            int: Urgency score (1-5)
        """
        title = item.get('title', '').lower()
        content = item.get('description', '').lower()
        text = f"{title} {content}"
        
        # High urgency keywords
        if any(word in text for word in ['breaking', 'breaking news', 'urgent', 'suspended']):
            return 5
        elif any(word in text for word in ['injury report', 'injured', 'out', 'trade']):
            return 4
        elif any(word in text for word in ['questionable', 'probable', 'coach decision']):
            return 3
        elif any(word in text for word in ['fantasy', 'start', 'sit', 'waiver']):
            return 3
        elif any(word in text for word in ['practice', 'team news', 'announcement']):
            return 2
        else:
            return 1

class RotowireNewsSource(NewsSource):
    """Rotowire/FantasyPros News integration with comprehensive mock data."""
    
    def __init__(self, api_key: str = None):
        super().__init__("FantasyPros", "https://api.fantasypros.com", rate_limit=100)
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}
        # Note: Using FantasyPros as they have more accessible APIs
        
    def get_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from FantasyPros RSS feeds and other free sources.
        
        Returns:
            list: List of news items with title, content, timestamp, and url
        """
        self._check_rate_limit()
        
        news_items = []
        
        # Try FantasyPros RSS feed
        try:
            fantasypros_rss = self._fetch_fantasypros_rss()
            news_items.extend(fantasypros_rss)
            logging.info(f"Fetched {len(fantasypros_rss)} items from FantasyPros RSS")
        except Exception as e:
            logging.warning(f"FantasyPros RSS failed: {e}")
        
        # Try CBS Sports RSS feed as backup
        if len(news_items) < 5:
            try:
                cbs_rss = self._fetch_cbs_sports_rss()
                news_items.extend(cbs_rss)
                logging.info(f"Fetched {len(cbs_rss)} items from CBS Sports RSS")
            except Exception as e:
                logging.warning(f"CBS Sports RSS failed: {e}")
        
        # Try Yahoo Sports RSS feed
        if len(news_items) < 10:
            try:
                yahoo_rss = self._fetch_yahoo_sports_rss()
                news_items.extend(yahoo_rss)
                logging.info(f"Fetched {len(yahoo_rss)} items from Yahoo Sports RSS")
            except Exception as e:
                logging.warning(f"Yahoo Sports RSS failed: {e}")
        
        # Remove duplicates and sort by timestamp
        seen_titles = set()
        unique_items = []
        for item in news_items:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_items.append(item)
        
        return unique_items[:20]  # Return top 20 items
    
    def _fetch_fantasypros_rss(self) -> List[Dict[str, Any]]:
        """
        Fetch news from FantasyPros RSS feed.
        
        Returns:
            list: News items from FantasyPros
        """
        rss_url = "https://www.fantasypros.com/nfl/player-news.php?format=rss"
        feed = feedparser.parse(rss_url)
        news_items = []
        
        for entry in feed.entries[:15]:
            title = self._clean_text(entry.get('title', ''))
            content = self._clean_text(entry.get('summary', ''))
            news_items.append({
                'title': title,
                'content': content,
                'tldr': self._generate_tldr(title, content),
                'timestamp': entry.get('published', datetime.now().isoformat()),
                'url': entry.get('link', ''),
                'source': 'FantasyPros',
                'urgency_score': self._calculate_urgency({'title': title, 'description': content})
            })
        
        return news_items
    
    def _fetch_cbs_sports_rss(self) -> List[Dict[str, Any]]:
        """
        Fetch news from CBS Sports RSS feed.
        
        Returns:
            list: News items from CBS Sports
        """
        rss_url = "https://www.cbssports.com/rss/headlines/nfl/"
        feed = feedparser.parse(rss_url)
        news_items = []
        
        for entry in feed.entries[:10]:
            title = self._clean_text(entry.get('title', ''))
            content = self._clean_text(entry.get('summary', ''))
            news_items.append({
                'title': title,
                'content': content,
                'tldr': self._generate_tldr(title, content),
                'timestamp': entry.get('published', datetime.now().isoformat()),
                'url': entry.get('link', ''),
                'source': 'CBS Sports',
                'urgency_score': self._calculate_urgency({'title': title, 'description': content})
            })
        
        return news_items
    
    def _fetch_yahoo_sports_rss(self) -> List[Dict[str, Any]]:
        """
        Fetch news from Yahoo Sports RSS feed.
        
        Returns:
            list: News items from Yahoo Sports
        """
        rss_url = "https://sports.yahoo.com/nfl/rss/"
        feed = feedparser.parse(rss_url)
        news_items = []
        
        for entry in feed.entries[:10]:
            title = self._clean_text(entry.get('title', ''))
            content = self._clean_text(entry.get('summary', ''))
            news_items.append({
                'title': title,
                'content': content,
                'tldr': self._generate_tldr(title, content),
                'timestamp': entry.get('published', datetime.now().isoformat()),
                'url': entry.get('link', ''),
                'source': 'Yahoo Sports',
                'urgency_score': self._calculate_urgency({'title': title, 'description': content})
            })
        
        return news_items
    
    def _get_comprehensive_fantasy_news(self) -> List[Dict[str, Any]]:
        """
        Return comprehensive fantasy football news mock data.
        
        Returns:
            list: Comprehensive mock news items with realistic fantasy content
        """
        mock_news = [
            {
                'title': 'BREAKING: Star RB Suffers Knee Injury in Practice',
                'content': 'Fantasy implications are significant as the workhorse back is expected to miss 4-6 weeks with a sprained MCL...',
                'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-rb-injury',
                'source': self.name,
                'urgency_score': 5
            },
            {
                'title': 'WR1 Officially Questionable for Sunday\'s Game',
                'content': 'The elite receiver has been dealing with a hamstring issue but practiced in a limited capacity on Friday...',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-wr-questionable',
                'source': self.name,
                'urgency_score': 4
            },
            {
                'title': 'Backup QB Named Starter for This Week',
                'content': 'With the starting quarterback in concussion protocol, fantasy managers need to adjust their expectations...',
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-qb-change',
                'source': self.name,
                'urgency_score': 4
            },
            {
                'title': 'Rookie TE Emerging as Red Zone Target',
                'content': 'The first-year tight end has seen increased usage in goal-line packages, making him a sneaky start this week...',
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-te-emerging',
                'source': self.name,
                'urgency_score': 3
            },
            {
                'title': 'Defense/ST Ranks Among Top Plays This Week',
                'content': 'Facing a turnover-prone quarterback and weak offensive line, this unit should produce fantasy points...',
                'timestamp': (datetime.now() - timedelta(hours=8)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-dst-play',
                'source': self.name,
                'urgency_score': 3
            },
            {
                'title': 'Kicker Added to Injury Report with Groin Issue',
                'content': 'The typically reliable kicker is questionable for Sunday, potentially affecting a high-scoring offense...',
                'timestamp': (datetime.now() - timedelta(hours=10)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-k-injury',
                'source': self.name,
                'urgency_score': 2
            },
            {
                'title': 'Week 10 Waiver Wire Priorities: RB Handcuffs',
                'content': 'With several running backs dealing with injuries, these backup options could provide league-winning value...',
                'timestamp': (datetime.now() - timedelta(hours=12)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-waiver-wire',
                'source': self.name,
                'urgency_score': 3
            },
            {
                'title': 'Trade Deadline Fantasy Impact: Buy Low Candidates',
                'content': 'Several underperforming players could see increased opportunity following recent NFL trades...',
                'timestamp': (datetime.now() - timedelta(hours=16)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-trade-impact',
                'source': self.name,
                'urgency_score': 2
            },
            {
                'title': 'Weather Alert: Wind Concerns for Sunday\'s Games',
                'content': 'High winds expected in three stadiums could significantly impact passing games and kicking...',
                'timestamp': (datetime.now() - timedelta(hours=18)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-weather-alert',
                'source': self.name,
                'urgency_score': 4
            },
            {
                'title': 'DFS Chalk Plays and Contrarian Options for Week 10',
                'content': 'Identify the most popular plays and find leverage with lower-owned alternatives in tournament formats...',
                'timestamp': (datetime.now() - timedelta(hours=20)).isoformat(),
                'url': 'https://www.fantasypros.com/nfl/news/mock-dfs-plays',
                'source': self.name,
                'urgency_score': 2
            }
        ]
        
        logging.info("Using comprehensive fantasy mock data for development")
        return mock_news
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate urgency score for a news item (1-5).
        
        Args:
            item (dict): News item from FantasyPros/Rotowire
            
        Returns:
            int: Urgency score (1-5)
        """
        title = item.get('title', '').lower()
        content = item.get('content', '').lower()
        text = f"{title} {content}"
        
        # Fantasy-focused urgency scoring
        if any(word in text for word in ['breaking', 'injured', 'out', 'season-ending']):
            return 5
        elif any(word in text for word in ['questionable', 'doubtful', 'limited', 'weather']):
            return 4
        elif any(word in text for word in ['probable', 'emerging', 'waiver', 'start']):
            return 3
        elif any(word in text for word in ['trade deadline', 'buy low', 'dfs']):
            return 2
        else:
            return 1

# Additional utility functions for news sources
def get_all_sources(rotowire_api_key: str = None) -> List[NewsSource]:
    """
    Get all configured news sources.
    
    Args:
        rotowire_api_key (str, optional): API key for Rotowire/FantasyPros
        
    Returns:
        list: List of configured news sources
    """
    return [
        ESPNNewsSource(),
        NFLNewsSource(),
        RotowireNewsSource(rotowire_api_key)
    ]

def test_all_sources(rotowire_api_key: str = None) -> Dict[str, Any]:
    """
    Test all news sources and return status information.
    
    Args:
        rotowire_api_key (str, optional): API key for testing
        
    Returns:
        dict: Status information for all sources
    """
    sources = get_all_sources(rotowire_api_key)
    results = {}
    
    for source in sources:
        try:
            news_items = source.get_news()
            results[source.name] = {
                'status': 'success',
                'items_fetched': len(news_items),
                'sample_title': news_items[0]['title'] if news_items else None
            }
        except Exception as e:
            results[source.name] = {
                'status': 'error',
                'error_message': str(e)
            }
    
    return results

# Example usage:
# sources = get_all_sources("your_api_key_here")
# test_results = test_all_sources("your_api_key_here")
# 
# all_news = []
# for source in sources:
#     try:
#         news_items = source.get_news()
#         all_news.extend(news_items)
#     except Exception as e:
#         logging.error(f"Failed to fetch from {source.name}: {str(e)}")