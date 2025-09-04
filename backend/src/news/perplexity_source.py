"""
Perplexity API integration for real-time NFL fantasy football news research.
"""

import os
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import html

logger = logging.getLogger(__name__)

class PerplexityNewsSource:
    """
    Fetch real-time NFL fantasy news using Perplexity API for research.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Perplexity news source.
        
        Args:
            api_key: Perplexity API key
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.name = "Perplexity"
        
    def get_news(self, query: str = None, focus_players: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch real-time news using Perplexity search.
        
        Args:
            query: Custom search query
            focus_players: List of player names to focus on
            
        Returns:
            List of news items with real-time information
        """
        if not self.api_key:
            logger.warning("Perplexity API key not configured, skipping")
            return []
            
        try:
            # Build search query
            if not query:
                query = self._build_default_query(focus_players)
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a fantasy football news aggregator. List the latest NFL news items with clear titles and descriptions."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.2,
                "top_p": 0.9
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_perplexity_response(data)
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Perplexity news: {e}")
            return []
    
    def _build_default_query(self, focus_players: List[str] = None) -> str:
        """
        Build a default search query for NFL fantasy news.
        
        Args:
            focus_players: Optional list of players to focus on
            
        Returns:
            Search query string
        """
        base_query = "Latest NFL fantasy football news today including injuries, roster changes, trades, and player updates"
        
        if focus_players:
            players_str = ", ".join(focus_players[:5])  # Limit to 5 players
            base_query += f" especially for {players_str}"
            
        base_query += ". Return the 10 most important news items from the last 24 hours."
        
        return base_query
    
    def _parse_perplexity_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Perplexity API response into news items.
        
        Args:
            data: API response data
            
        Returns:
            List of formatted news items
        """
        news_items = []
        
        try:
            # Extract content from response
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse as JSON
            try:
                news_data = json.loads(content)
                if isinstance(news_data, list):
                    for item in news_data:
                        news_items.append(self._format_news_item(item))
                elif isinstance(news_data, dict) and "news" in news_data:
                    for item in news_data["news"]:
                        news_items.append(self._format_news_item(item))
            except json.JSONDecodeError:
                # If not JSON, parse as text
                news_items = self._parse_text_response(content)
            
            # Add citations if available
            citations = data.get("citations", [])
            if citations and news_items:
                for i, item in enumerate(news_items[:len(citations)]):
                    if i < len(citations):
                        item["url"] = citations[i]
            
        except Exception as e:
            logger.error(f"Error parsing Perplexity response: {e}")
        
        return news_items
    
    def _format_news_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a news item to standard structure.
        
        Args:
            item: Raw news item
            
        Returns:
            Formatted news item
        """
        return {
            "title": item.get("title", ""),
            "content": item.get("content", item.get("description", "")),
            "timestamp": item.get("timestamp", datetime.now().isoformat()),
            "url": item.get("url", ""),
            "source": self.name,
            "urgency_score": item.get("importance", item.get("urgency_score", 3))
        }
    
    def _parse_text_response(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse text response into news items.
        
        Args:
            content: Text content from API
            
        Returns:
            List of news items
        """
        news_items = []
        
        # Parse numbered list items (e.g., "1. **Title** content")
        import re
        pattern = r'\d+\.\s+\*\*(.*?)\*\*(.*?)(?=\d+\.|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for title, content_text in matches:
            clean_title = html.unescape(title.strip())
            clean_content = html.unescape(content_text.strip())
            tldr = clean_content[:100] + "..." if len(clean_content) > 100 else clean_content
            news_items.append({
                "title": clean_title,
                "content": clean_content,
                "tldr": tldr,
                "timestamp": datetime.now().isoformat(),
                "url": "",
                "source": self.name,
                "urgency_score": self._calculate_urgency_from_text(clean_title + " " + clean_content)
            })
        
        # If no numbered format, try bullet points
        if not news_items:
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("• "):
                    # Extract player name and details
                    match = re.match(r'[-•]\s+\*\*(.*?)\*\*(.*)', line)
                    if match:
                        news_items.append({
                            "title": match.group(1).strip(),
                            "content": match.group(2).strip(),
                            "timestamp": datetime.now().isoformat(),
                            "url": "",
                            "source": self.name,
                            "urgency_score": self._calculate_urgency_from_text(line)
                        })
                    else:
                        # Plain bullet point
                        news_items.append({
                            "title": line[2:].strip()[:100],  # First 100 chars as title
                            "content": line[2:].strip(),
                            "timestamp": datetime.now().isoformat(),
                            "url": "",
                            "source": self.name,
                            "urgency_score": 3
                        })
        
        return news_items[:10]  # Limit to 10 items
    
    def _calculate_urgency_from_text(self, text: str) -> int:
        """
        Calculate urgency based on text content.
        
        Args:
            text: News text
            
        Returns:
            Urgency score (1-5)
        """
        text_lower = text.lower()
        
        # High urgency keywords
        if any(word in text_lower for word in ["breaking", "injury", "out", "doubtful", "surgery", "ir", "injured reserve"]):
            return 5
        elif any(word in text_lower for word in ["questionable", "limited", "trade", "waiver"]):
            return 4
        elif any(word in text_lower for word in ["expected", "probable", "update", "report"]):
            return 3
        elif any(word in text_lower for word in ["practice", "returning", "cleared"]):
            return 2
        else:
            return 1
    
    def get_player_specific_news(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Get news specific to a player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            List of news items about the player
        """
        query = f"Latest NFL news and updates about {player_name} including injury status, performance, fantasy outlook"
        return self.get_news(query=query)
    
    def get_breaking_news(self) -> List[Dict[str, Any]]:
        """
        Get breaking NFL news from the last few hours.
        
        Returns:
            List of breaking news items
        """
        query = "Breaking NFL news from the last 3 hours including injuries, trades, roster moves, and lineup changes that impact fantasy football"
        news = self.get_news(query=query)
        
        # Mark all as high urgency since they're breaking
        for item in news:
            item["urgency_score"] = 5
            
        return news