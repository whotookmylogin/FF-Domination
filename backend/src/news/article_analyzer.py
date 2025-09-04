"""
Enhanced article analyzer for fetching and summarizing full article content.
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import re
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ArticleAnalyzer:
    """
    Fetches full article content and generates comprehensive summaries.
    """
    
    def __init__(self, perplexity_api_key: Optional[str] = None):
        """
        Initialize the article analyzer.
        
        Args:
            perplexity_api_key: Optional Perplexity API key for AI summarization
        """
        self.perplexity_api_key = perplexity_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_article_content(self, url: str) -> Optional[str]:
        """
        Fetch and extract the main content from an article URL.
        
        Args:
            url: The article URL to fetch
            
        Returns:
            The extracted article text or None if failed
        """
        try:
            # Skip if not a valid URL
            if not url or url == '#' or not url.startswith('http'):
                return None
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()
            
            # Try different content selectors based on common news sites
            content = None
            
            # ESPN specific selectors
            if 'espn.com' in url:
                article = soup.find('div', class_='article-body') or \
                         soup.find('div', class_='story-body') or \
                         soup.find('article')
                if article:
                    content = article.get_text()
            
            # NFL.com specific selectors
            elif 'nfl.com' in url:
                article = soup.find('div', class_='d3-l-col__col-8') or \
                         soup.find('div', class_='nfl-c-article__content') or \
                         soup.find('article')
                if article:
                    content = article.get_text()
            
            # CBS Sports specific selectors
            elif 'cbssports.com' in url:
                article = soup.find('div', class_='article-content') or \
                         soup.find('div', class_='article-body') or \
                         soup.find('article')
                if article:
                    content = article.get_text()
            
            # Generic article extraction
            if not content:
                # Try common article tags
                article = soup.find('article') or \
                         soup.find('main') or \
                         soup.find('div', {'role': 'main'})
                
                if article:
                    # Get all paragraphs
                    paragraphs = article.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text() for p in paragraphs])
                else:
                    # Fallback to all paragraphs
                    paragraphs = soup.find_all('p')
                    if len(paragraphs) > 3:  # Ensure we have substantial content
                        content = ' '.join([p.get_text() for p in paragraphs])
            
            if content:
                # Clean up the text
                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                content = content.strip()
                
                # Ensure we have substantial content
                if len(content) > 200:
                    return content
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching article from {url}: {e}")
            return None
    
    def generate_comprehensive_summary(self, 
                                      title: str, 
                                      content: str,
                                      original_tldr: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the article.
        
        Args:
            title: Article title
            content: Full article content
            original_tldr: Original TLDR if available
            
        Returns:
            Dictionary with enhanced summary information
        """
        if not content:
            return {
                'enhanced_tldr': original_tldr or 'Article content unavailable',
                'key_points': [],
                'fantasy_impact': 'Unable to analyze - content unavailable'
            }
        
        # Use AI if available
        if self.perplexity_api_key:
            return self._ai_summarize(title, content)
        
        # Fallback to rule-based summarization
        return self._rule_based_summarize(title, content, original_tldr)
    
    def _ai_summarize(self, title: str, content: str) -> Dict[str, Any]:
        """
        Use Perplexity AI to generate comprehensive summary.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            # Truncate content if too long
            max_content_length = 4000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt = f"""
            Create a concise TLDR summary of this NFL/Fantasy Football article.
            
            REQUIREMENTS:
            1. Start with a one-sentence executive summary (the most important takeaway)
            2. Follow with 3-4 bullet points with actionable fantasy football insights
            3. Each bullet should be SHORT and specific (max 15 words)
            4. Focus ONLY on fantasy-relevant info: injuries, status changes, performance, lineup impacts
            5. Omit filler content, quotes, and non-fantasy details
            
            Article Title: {title}
            Content: {content}
            
            FORMAT:
            TLDR: [One sentence summary]
            • [Key point 1]
            • [Key point 2] 
            • [Key point 3]
            • [Fantasy impact/recommendation if applicable]
            """
            
            data = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert fantasy football analyst. Create extremely concise TLDR summaries focusing only on fantasy-relevant information. Be direct and specific."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Return as executive summary
                return {
                    'enhanced_tldr': ai_response.strip(),
                    'key_points': [],
                    'fantasy_impact': None
                }
            
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
        
        # Fallback to rule-based
        return self._rule_based_summarize(title, content, None)
    
    def _rule_based_summarize(self, title: str, content: str, original_tldr: Optional[str]) -> Dict[str, Any]:
        """
        Rule-based summarization fallback.
        """
        # Extract key sentences
        sentences = content.split('. ')
        
        # Look for important keywords with priority
        injury_keywords = ['injury', 'injured', 'out', 'questionable', 'doubtful', 'return', 'miss', 'game-time decision']
        transaction_keywords = ['traded', 'trade', 'waiver', 'cut', 'released', 'signed', 'claimed']
        performance_keywords = ['touchdown', 'yards', 'catches', 'targets', 'carries', 'receptions', 'rushing']
        status_keywords = ['starting', 'benched', 'backup', 'starter', 'inactive', 'activated']
        
        # Categorize important info
        injury_info = []
        transaction_info = []
        performance_info = []
        status_info = []
        
        for sentence in sentences[:30]:  # Check first 30 sentences
            sentence_lower = sentence.lower()
            sentence_clean = sentence.strip()
            
            if any(keyword in sentence_lower for keyword in injury_keywords) and len(sentence_clean) < 150:
                injury_info.append(sentence_clean)
            elif any(keyword in sentence_lower for keyword in transaction_keywords) and len(sentence_clean) < 150:
                transaction_info.append(sentence_clean)
            elif any(keyword in sentence_lower for keyword in performance_keywords) and len(sentence_clean) < 150:
                performance_info.append(sentence_clean)
            elif any(keyword in sentence_lower for keyword in status_keywords) and len(sentence_clean) < 150:
                status_info.append(sentence_clean)
        
        # Build TLDR with structure
        tldr_parts = []
        
        # Main summary (combine title context with most important info)
        if injury_info:
            tldr_parts.append(f"TLDR: {injury_info[0][:100]}")
        elif transaction_info:
            tldr_parts.append(f"TLDR: {transaction_info[0][:100]}")
        elif status_info:
            tldr_parts.append(f"TLDR: {status_info[0][:100]}")
        else:
            tldr_parts.append(f"TLDR: {title}")
        
        # Add bullet points
        all_important = injury_info[:1] + status_info[:1] + performance_info[:1] + transaction_info[:1]
        for info in all_important[:3]:
            if info and len(info) < 100:
                # Truncate to key part
                info_short = info.split(',')[0] if ',' in info else info
                tldr_parts.append(f"• {info_short[:80]}")
        
        enhanced_tldr = '\n'.join(tldr_parts) if tldr_parts else original_tldr or sentences[0]
        
        # Extract key points
        key_points = []
        
        # Check for injury info
        injury_pattern = r'([\w\s]+)\s+(?:is|has been|will be)\s+(?:out|questionable|doubtful|injured)'
        injury_matches = re.findall(injury_pattern, content, re.IGNORECASE)
        for match in injury_matches[:2]:
            key_points.append(f"Injury update: {match.strip()}")
        
        # Check for performance stats
        stats_pattern = r'(\d+)\s+(?:yards|touchdowns?|catches|carries|targets|receptions)'
        stats_matches = re.findall(stats_pattern, content, re.IGNORECASE)
        for match in stats_matches[:2]:
            key_points.append(f"Key stat mentioned: {match}")
        
        # Check for roster moves
        roster_pattern = r'(?:traded|signed|released|cut|waived|claimed)'
        if re.search(roster_pattern, content, re.IGNORECASE):
            key_points.append("Roster move or transaction reported")
        
        # Determine fantasy impact
        fantasy_impact = "Monitor situation"
        if any(word in content.lower() for word in ['injury', 'injured', 'out']):
            fantasy_impact = "Potential lineup change needed - check injury status"
        elif any(word in content.lower() for word in ['breakout', 'career-high', 'leads league']):
            fantasy_impact = "Positive trend - consider for lineup"
        elif any(word in content.lower() for word in ['benched', 'struggling', 'dropped']):
            fantasy_impact = "Negative trend - consider alternatives"
        
        return {
            'enhanced_tldr': enhanced_tldr[:500],  # Limit length
            'key_points': key_points[:5],  # Max 5 points
            'fantasy_impact': fantasy_impact
        }
    
    def enhance_news_item(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a single news item with full article analysis.
        
        Args:
            news_item: Original news item dictionary
            
        Returns:
            Enhanced news item with comprehensive summary
        """
        url = news_item.get('url') or news_item.get('link')
        
        if url and url != '#':
            # Fetch full article content
            content = self.fetch_article_content(url)
            
            if content:
                # Generate comprehensive summary
                summary_data = self.generate_comprehensive_summary(
                    news_item.get('title', ''),
                    content,
                    news_item.get('tldr')
                )
                
                # Update news item with executive summary only
                news_item['enhanced_tldr'] = summary_data.get('enhanced_tldr', news_item.get('tldr', ''))
                # Don't include key_points or fantasy_impact to keep it clean
                news_item['full_content_analyzed'] = True
                
                logger.info(f"Enhanced article: {news_item.get('title', '')[:50]}...")
            else:
                logger.warning(f"Could not fetch content for: {url}")
                news_item['full_content_analyzed'] = False
        else:
            news_item['full_content_analyzed'] = False
        
        return news_item
    
    def enhance_news_batch(self, news_items: List[Dict[str, Any]], max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Enhance a batch of news items.
        
        Args:
            news_items: List of news items to enhance
            max_items: Maximum number of items to enhance (to avoid delays)
            
        Returns:
            List of enhanced news items
        """
        enhanced_items = []
        
        for i, item in enumerate(news_items):
            if i >= max_items:
                # Don't enhance remaining items to avoid delays
                item['full_content_analyzed'] = False
                enhanced_items.append(item)
            else:
                enhanced_items.append(self.enhance_news_item(item))
        
        return enhanced_items