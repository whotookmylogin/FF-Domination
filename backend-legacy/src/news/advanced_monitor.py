"""
Advanced News Monitoring System for Fantasy Football
Monitors training camps, signings, injuries, and provides strategic recommendations
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re
import json
from dataclasses import dataclass
from enum import Enum
import os
import openai
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsImpact(Enum):
    """Impact levels for fantasy football news"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Significant impact on roster decisions
    MEDIUM = "medium"  # Worth monitoring
    LOW = "low"  # Informational only

class RecommendationType(Enum):
    """Types of strategic recommendations"""
    PICKUP_IMMEDIATE = "pickup_immediate"  # Grab this player now
    PICKUP_STRATEGIC = "pickup_strategic"  # Pick up to block opponents
    TRADE_TARGET = "trade_target"  # Target for trades
    TRADE_AWAY = "trade_away"  # Trade away before value drops
    HOLD = "hold"  # Keep monitoring
    DROP_CANDIDATE = "drop_candidate"  # Consider dropping
    OPPONENT_RECOMMENDATION = "opponent_recommendation"  # Recommend to opponent for strategic benefit

@dataclass
class NewsItem:
    """Enhanced news item with fantasy impact analysis"""
    source: str
    title: str
    content: str
    url: str
    timestamp: datetime
    players_mentioned: List[str]
    teams_affected: List[str]
    impact_level: NewsImpact
    fantasy_relevance_score: float  # 0-10 scale
    recommendation: Optional[RecommendationType]
    strategic_analysis: str
    action_deadline: Optional[datetime]  # When action should be taken by

class AdvancedNewsMonitor:
    """
    Advanced news monitoring system that checks multiple sources 4x daily
    and provides strategic fantasy football recommendations
    """
    
    # Top Twitter/X accounts to monitor (fantasy experts and NFL insiders)
    TOP_X_ACCOUNTS = [
        "@AdamSchefter",  # ESPN NFL Insider
        "@RapSheet",  # NFL Network Insider
        "@FieldYates",  # ESPN Fantasy Expert
        "@MatthewBerryTMR",  # NBC Fantasy Expert
        "@ScottBarrettDFB",  # Fantasy analyst
        "@JamesPalmerTV",  # NFL Network
        "@TomPelissero",  # NFL Network
        "@MikeClayNFL",  # ESPN Analytics
        "@Connor_J_Hughes",  # SNY Jets reporter
        "@AaronWilson_NFL",  # NFL reporter
        "@JosinaAnderson",  # NFL Insider
        "@DiannaNFL",  # ESPN NFL reporter
        "@AlbertBreer",  # MMQB Senior Reporter
        "@JayGlazer",  # FOX NFL Insider
        "@PFF_Fantasy",  # Pro Football Focus Fantasy
    ]
    
    # Primary news sources to monitor
    NEWS_SOURCES = {
        "espn": "https://www.espn.com/nfl/",
        "nfl": "https://www.nfl.com/news/",
        "rotoworld": "https://www.nbcsportsedge.com/football/nfl",
        "fantasy_pros": "https://www.fantasypros.com/nfl/news/",
        "sleeper": "https://sleeper.app/news/nfl",
        "the_athletic": "https://theathletic.com/nfl/",
        "pro_football_talk": "https://profootballtalk.nbcsports.com/",
        "bleacher_report": "https://bleacherreport.com/nfl",
        "yahoo_fantasy": "https://sports.yahoo.com/fantasy/football/news/",
    }
    
    # Training camp specific sources
    TRAINING_CAMP_SOURCES = {
        "training_camp_reports": "https://www.nfl.com/news/training-camp",
        "beat_reporters": "https://www.espn.com/nfl/team/_/name/{team}/",
    }
    
    def __init__(self, 
                 openai_key: Optional[str] = None,
                 x_bearer_token: Optional[str] = None,
                 check_frequency_hours: int = 6):  # 4 times per day
        """
        Initialize the advanced news monitor
        
        Args:
            openai_key: OpenAI API key for intelligent analysis
            x_bearer_token: Twitter/X API bearer token
            check_frequency_hours: How often to check news (default 6 hours = 4x daily)
        """
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self.x_bearer_token = x_bearer_token or os.getenv("X_BEARER_TOKEN")
        self.check_frequency = check_frequency_hours
        self.last_check = datetime.now() - timedelta(hours=24)
        self.news_cache = []
        
        if self.openai_key:
            openai.api_key = self.openai_key
    
    async def monitor_all_sources(self) -> List[NewsItem]:
        """
        Monitor all configured news sources and return analyzed news items
        """
        all_news = []
        
        # Gather news from all sources concurrently
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Monitor traditional news sources
            for source_name, url in self.NEWS_SOURCES.items():
                tasks.append(self._fetch_news_source(session, source_name, url))
            
            # Monitor X/Twitter if token available
            if self.x_bearer_token:
                tasks.append(self._monitor_x_accounts(session))
            
            # Monitor training camp sources
            tasks.append(self._monitor_training_camps(session))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error fetching news: {result}")
        
        # Analyze and deduplicate news
        analyzed_news = await self._analyze_news_items(all_news)
        deduped_news = self._deduplicate_news(analyzed_news)
        
        # Generate strategic recommendations
        final_news = await self._generate_recommendations(deduped_news)
        
        # Cache results
        self.news_cache = final_news
        self.last_check = datetime.now()
        
        return final_news
    
    async def _fetch_news_source(self, session: aiohttp.ClientSession, 
                                 source_name: str, url: str) -> List[Dict]:
        """Fetch news from a specific source"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_news_content(source_name, content, url)
        except Exception as e:
            logger.error(f"Error fetching {source_name}: {e}")
        return []
    
    async def _monitor_x_accounts(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Monitor X/Twitter accounts for breaking news"""
        news_items = []
        
        # Note: This would require Twitter API v2 implementation
        # For now, returning placeholder structure
        headers = {
            "Authorization": f"Bearer {self.x_bearer_token}"
        }
        
        for account in self.TOP_X_ACCOUNTS:
            try:
                # Twitter API v2 endpoint for user tweets
                user_handle = account.replace("@", "")
                url = f"https://api.twitter.com/2/tweets/search/recent?query=from:{user_handle}&max_results=10"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for tweet in data.get("data", []):
                            news_items.append({
                                "source": f"X/{account}",
                                "content": tweet.get("text", ""),
                                "timestamp": datetime.now(),
                                "url": f"https://twitter.com/{user_handle}/status/{tweet.get('id')}"
                            })
            except Exception as e:
                logger.debug(f"Error monitoring {account}: {e}")
        
        return news_items
    
    async def _monitor_training_camps(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Monitor training camp specific news"""
        news_items = []
        
        # NFL teams for beat reporter monitoring
        nfl_teams = [
            "buf", "mia", "ne", "nyj",  # AFC East
            "bal", "cin", "cle", "pit",  # AFC North
            "hou", "ind", "jax", "ten",  # AFC South
            "den", "kc", "lv", "lac",  # AFC West
            "dal", "nyg", "phi", "wsh",  # NFC East
            "chi", "det", "gb", "min",  # NFC North
            "atl", "car", "no", "tb",  # NFC South
            "ari", "lar", "sf", "sea"  # NFC West
        ]
        
        for team in nfl_teams:
            url = f"https://www.espn.com/nfl/team/_/name/{team}/"
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        team_news = self._parse_team_news(team, content)
                        news_items.extend(team_news)
            except Exception as e:
                logger.debug(f"Error fetching {team} news: {e}")
        
        return news_items
    
    def _parse_news_content(self, source: str, html_content: str, base_url: str) -> List[Dict]:
        """Parse HTML content to extract news items"""
        news_items = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Different parsing strategies for different sources
            if "espn" in source:
                articles = soup.find_all('article', limit=10)
                for article in articles:
                    title_elem = article.find('h1') or article.find('h2') or article.find('h3')
                    if title_elem:
                        news_items.append({
                            "source": source,
                            "title": title_elem.text.strip(),
                            "content": article.text.strip()[:500],
                            "timestamp": datetime.now(),
                            "url": base_url
                        })
            
            elif "nfl" in source:
                # NFL.com specific parsing
                articles = soup.find_all('div', class_='nfl-c-headline', limit=10)
                for article in articles:
                    title = article.find('h3')
                    if title:
                        news_items.append({
                            "source": source,
                            "title": title.text.strip(),
                            "content": "",
                            "timestamp": datetime.now(),
                            "url": base_url
                        })
            
            # Generic fallback parser
            if not news_items:
                # Look for common article patterns
                for tag in ['article', 'div']:
                    articles = soup.find_all(tag, class_=re.compile('article|news|story'), limit=10)
                    for article in articles[:5]:
                        title = article.find(['h1', 'h2', 'h3', 'h4'])
                        if title:
                            news_items.append({
                                "source": source,
                                "title": title.text.strip(),
                                "content": article.text.strip()[:500],
                                "timestamp": datetime.now(),
                                "url": base_url
                            })
                            
        except Exception as e:
            logger.error(f"Error parsing {source} content: {e}")
        
        return news_items
    
    def _parse_team_news(self, team: str, html_content: str) -> List[Dict]:
        """Parse team-specific news from beat reporters"""
        news_items = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for training camp reports
            camp_keywords = ['practice', 'training camp', 'injury', 'depth chart', 
                           'starter', 'backup', 'competition', 'impressive', 'struggling']
            
            articles = soup.find_all(['article', 'div'], limit=5)
            for article in articles:
                text = article.text.lower()
                if any(keyword in text for keyword in camp_keywords):
                    title = article.find(['h1', 'h2', 'h3'])
                    if title:
                        news_items.append({
                            "source": f"beat_reporter_{team}",
                            "title": title.text.strip(),
                            "content": article.text.strip()[:500],
                            "timestamp": datetime.now(),
                            "url": f"https://www.espn.com/nfl/team/_/name/{team}/",
                            "team": team.upper()
                        })
        
        except Exception as e:
            logger.debug(f"Error parsing {team} news: {e}")
        
        return news_items
    
    async def _analyze_news_items(self, raw_news: List[Dict]) -> List[NewsItem]:
        """Analyze news items for fantasy relevance using AI"""
        analyzed_items = []
        
        for item in raw_news:
            try:
                # Extract players and teams mentioned
                players = self._extract_players(item.get("content", "") + " " + item.get("title", ""))
                teams = self._extract_teams(item.get("content", "") + " " + item.get("title", ""))
                
                # Determine impact level
                impact = self._assess_impact(item)
                
                # Calculate fantasy relevance
                relevance = self._calculate_relevance(item, players, teams)
                
                # Use AI for deeper analysis if available
                if self.openai_key and relevance > 5:
                    strategic_analysis = await self._ai_analyze(item, players, teams)
                else:
                    strategic_analysis = self._basic_analysis(item, players, teams)
                
                analyzed_items.append(NewsItem(
                    source=item.get("source", "unknown"),
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    url=item.get("url", ""),
                    timestamp=item.get("timestamp", datetime.now()),
                    players_mentioned=players,
                    teams_affected=teams,
                    impact_level=impact,
                    fantasy_relevance_score=relevance,
                    recommendation=None,  # Will be set in recommendation phase
                    strategic_analysis=strategic_analysis,
                    action_deadline=self._determine_deadline(impact)
                ))
                
            except Exception as e:
                logger.error(f"Error analyzing news item: {e}")
        
        return analyzed_items
    
    def _extract_players(self, text: str) -> List[str]:
        """Extract player names from text"""
        players = []
        
        # Common player name patterns
        # This would ideally use a player database
        player_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s(?:Jr\.|Sr\.|III?))?\b',  # FirstName LastName
            r'\b[A-Z]\.\s?[A-Z][a-z]+\b',  # F. LastName
        ]
        
        for pattern in player_patterns:
            matches = re.findall(pattern, text)
            players.extend(matches)
        
        # Filter out common non-player names
        filtered = [p for p in players if not any(
            skip in p for skip in ['NFL', 'ESPN', 'Coach', 'Mr.', 'Ms.', 'Dr.']
        )]
        
        return list(set(filtered))[:5]  # Return top 5 unique players
    
    def _extract_teams(self, text: str) -> List[str]:
        """Extract team names from text"""
        nfl_teams = {
            'Cardinals', 'Falcons', 'Ravens', 'Bills', 'Panthers', 'Bears',
            'Bengals', 'Browns', 'Cowboys', 'Broncos', 'Lions', 'Packers',
            'Texans', 'Colts', 'Jaguars', 'Chiefs', 'Raiders', 'Chargers',
            'Rams', 'Dolphins', 'Vikings', 'Patriots', 'Saints', 'Giants',
            'Jets', 'Eagles', 'Steelers', '49ers', 'Seahawks', 'Buccaneers',
            'Titans', 'Commanders', 'Washington'
        }
        
        found_teams = []
        text_lower = text.lower()
        
        for team in nfl_teams:
            if team.lower() in text_lower:
                found_teams.append(team)
        
        return list(set(found_teams))
    
    def _assess_impact(self, news_item: Dict) -> NewsImpact:
        """Assess the impact level of a news item"""
        content = (news_item.get("title", "") + " " + news_item.get("content", "")).lower()
        
        # Critical keywords
        if any(word in content for word in ['torn acl', 'season-ending', 'suspended', 
                                            'traded to', 'signed with', 'cut', 'released']):
            return NewsImpact.CRITICAL
        
        # High impact keywords
        elif any(word in content for word in ['injury', 'questionable', 'doubtful', 
                                              'starting', 'benched', 'practice squad']):
            return NewsImpact.HIGH
        
        # Medium impact keywords
        elif any(word in content for word in ['limited', 'competition', 'depth chart', 
                                              'impressive', 'struggling']):
            return NewsImpact.MEDIUM
        
        return NewsImpact.LOW
    
    def _calculate_relevance(self, news_item: Dict, players: List[str], teams: List[str]) -> float:
        """Calculate fantasy relevance score (0-10)"""
        score = 0.0
        content = (news_item.get("title", "") + " " + news_item.get("content", "")).lower()
        
        # Player mentions add relevance
        score += min(len(players) * 1.5, 3.0)
        
        # Team mentions add relevance
        score += min(len(teams) * 0.5, 1.0)
        
        # Fantasy keywords
        fantasy_keywords = ['fantasy', 'waiver', 'start', 'sit', 'pickup', 'drop', 
                           'trade', 'value', 'points', 'touchdown', 'yards']
        keyword_count = sum(1 for kw in fantasy_keywords if kw in content)
        score += min(keyword_count * 0.8, 3.0)
        
        # Recency bonus
        if news_item.get("timestamp"):
            hours_old = (datetime.now() - news_item["timestamp"]).total_seconds() / 3600
            if hours_old < 1:
                score += 2.0
            elif hours_old < 6:
                score += 1.0
            elif hours_old < 24:
                score += 0.5
        
        # Source credibility
        if any(source in news_item.get("source", "").lower() 
               for source in ['schefter', 'rapsheet', 'pelissero']):
            score += 1.0
        
        return min(score, 10.0)
    
    async def _ai_analyze(self, news_item: Dict, players: List[str], teams: List[str]) -> str:
        """Use AI to provide strategic analysis"""
        if not self.openai_key:
            return self._basic_analysis(news_item, players, teams)
        
        try:
            prompt = f"""
            Analyze this NFL news for fantasy football impact:
            
            Title: {news_item.get('title', '')}
            Content: {news_item.get('content', '')}
            Players: {', '.join(players)}
            Teams: {', '.join(teams)}
            
            Provide a brief strategic analysis (2-3 sentences) focusing on:
            1. Immediate fantasy impact
            2. Who benefits/loses value
            3. Recommended action for fantasy managers
            
            Be specific and actionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert fantasy football analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._basic_analysis(news_item, players, teams)
    
    def _basic_analysis(self, news_item: Dict, players: List[str], teams: List[str]) -> str:
        """Provide basic strategic analysis without AI"""
        content = news_item.get("content", "").lower()
        analysis = []
        
        if "injury" in content or "injured" in content:
            analysis.append("Monitor injury status closely. Consider handcuff if available.")
        
        if "signed" in content or "traded" in content:
            analysis.append("New opportunity could mean increased fantasy value.")
        
        if "practice" in content or "training camp" in content:
            analysis.append("Training camp performance may impact depth chart position.")
        
        if "suspended" in content or "violation" in content:
            analysis.append("Immediate replacement needed. Check waiver wire for alternatives.")
        
        if not analysis:
            analysis.append("Continue monitoring for fantasy impact developments.")
        
        return " ".join(analysis)
    
    def _determine_deadline(self, impact: NewsImpact) -> Optional[datetime]:
        """Determine when action should be taken"""
        if impact == NewsImpact.CRITICAL:
            return datetime.now() + timedelta(hours=1)
        elif impact == NewsImpact.HIGH:
            return datetime.now() + timedelta(hours=6)
        elif impact == NewsImpact.MEDIUM:
            return datetime.now() + timedelta(days=1)
        return None
    
    def _deduplicate_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate news items"""
        seen = set()
        unique_items = []
        
        for item in news_items:
            # Create a hash of title + first 100 chars of content
            item_hash = hash(item.title + item.content[:100])
            if item_hash not in seen:
                seen.add(item_hash)
                unique_items.append(item)
        
        return unique_items
    
    async def _generate_recommendations(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Generate strategic recommendations for each news item"""
        for item in news_items:
            item.recommendation = self._determine_recommendation(item)
        
        return news_items
    
    def _determine_recommendation(self, item: NewsItem) -> RecommendationType:
        """Determine the appropriate recommendation type"""
        content = (item.title + " " + item.content).lower()
        
        # Immediate pickup scenarios
        if any(phrase in content for phrase in ['breakout', 'starting job', 'promoted to starter']):
            return RecommendationType.PICKUP_IMMEDIATE
        
        # Strategic pickup (block opponents)
        if item.impact_level == NewsImpact.HIGH and 'backup' in content:
            return RecommendationType.PICKUP_STRATEGIC
        
        # Trade targets
        if any(phrase in content for phrase in ['buy low', 'struggling', 'slow start']):
            return RecommendationType.TRADE_TARGET
        
        # Trade away
        if any(phrase in content for phrase in ['injury concern', 'losing snaps', 'benched']):
            return RecommendationType.TRADE_AWAY
        
        # Drop candidate
        if any(phrase in content for phrase in ['season-ending', 'cut', 'released', 'practice squad']):
            return RecommendationType.DROP_CANDIDATE
        
        # Strategic opponent recommendation
        if item.fantasy_relevance_score < 5 and 'decent matchup' in content:
            return RecommendationType.OPPONENT_RECOMMENDATION
        
        return RecommendationType.HOLD
    
    def get_actionable_notifications(self, 
                                    user_roster: List[str],
                                    league_standings: Dict,
                                    upcoming_opponent: str) -> List[Dict]:
        """
        Get personalized actionable notifications based on user's team context
        
        Args:
            user_roster: List of players on user's roster
            league_standings: Current league standings
            upcoming_opponent: Next opponent's team name
            
        Returns:
            List of actionable notifications
        """
        notifications = []
        
        for item in self.news_cache:
            # Check if news affects user's players
            roster_affected = any(player in user_roster for player in item.players_mentioned)
            
            if roster_affected and item.impact_level in [NewsImpact.CRITICAL, NewsImpact.HIGH]:
                notifications.append({
                    "type": "roster_alert",
                    "urgency": "high",
                    "title": f"Your player affected: {item.title}",
                    "message": item.strategic_analysis,
                    "action_required": item.recommendation.value,
                    "deadline": item.action_deadline
                })
            
            # Strategic recommendations for blocking opponents
            elif item.recommendation == RecommendationType.PICKUP_STRATEGIC:
                notifications.append({
                    "type": "strategic_block",
                    "urgency": "medium",
                    "title": f"Block your opponents: {item.title}",
                    "message": f"Pick up this player to prevent {upcoming_opponent} from getting them. {item.strategic_analysis}",
                    "action_required": "pickup_strategic",
                    "deadline": item.action_deadline
                })
            
            # Opponent recommendations for long-term benefit
            elif item.recommendation == RecommendationType.OPPONENT_RECOMMENDATION:
                notifications.append({
                    "type": "strategic_recommendation",
                    "urgency": "low",
                    "title": f"Strategic play: {item.title}",
                    "message": f"Consider suggesting this to a league rival to improve your playoff positioning. {item.strategic_analysis}",
                    "action_required": "opponent_recommendation",
                    "deadline": None
                })
        
        return sorted(notifications, key=lambda x: x["urgency"] == "high", reverse=True)


class NewsScheduler:
    """Scheduler for running news monitoring at regular intervals"""
    
    def __init__(self, monitor: AdvancedNewsMonitor):
        self.monitor = monitor
        self.running = False
        
    async def start(self):
        """Start the scheduled monitoring"""
        self.running = True
        
        while self.running:
            try:
                # Run monitoring
                logger.info("Starting scheduled news monitoring...")
                news_items = await self.monitor.monitor_all_sources()
                logger.info(f"Found {len(news_items)} news items")
                
                # Store results in database or cache
                await self._store_news_items(news_items)
                
                # Wait for next check interval
                await asyncio.sleep(self.monitor.check_frequency * 3600)
                
            except Exception as e:
                logger.error(f"Error in news scheduler: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _store_news_items(self, news_items: List[NewsItem]):
        """Store news items in database"""
        # Implementation would store in database
        pass
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False