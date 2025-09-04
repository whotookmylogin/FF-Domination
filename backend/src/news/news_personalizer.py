"""
News Personalization Service
Analyzes news relevance to user's team and generates personalized summaries
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class NewsPersonalizer:
    def __init__(self):
        self.injury_keywords = ['injured', 'injury', 'questionable', 'doubtful', 'out', 'IR', 'inactive', 'limited practice']
        self.opportunity_keywords = ['breakout', 'waiver', 'pickup', 'add', 'stash', 'sleeper', 'target', 'must-add']
        self.trade_keywords = ['trade', 'traded', 'deal', 'acquire', 'acquired', 'move', 'swap']
        
    def analyze_news_relevance(self, news_item: Dict[str, Any], user_roster: List[Dict[str, Any]], league_teams: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze how a news item relates to a user's team
        
        Args:
            news_item: News article with title, description, etc.
            user_roster: User's current roster
            league_teams: Other teams in the league for competitive analysis
            
        Returns:
            Enhanced news item with personalized summary and relevance score
        """
        enhanced_item = news_item.copy()
        relevance_factors = []
        relevance_score = 0
        personalized_summary = ""
        
        # Extract player names from news
        mentioned_players = self._extract_player_names(news_item)
        
        # Check if news affects user's players
        user_players = {player['name'].lower(): player for player in user_roster}
        affected_user_players = []
        
        for player_name in mentioned_players:
            if player_name.lower() in user_players:
                affected_user_players.append(user_players[player_name.lower()])
                relevance_score += 10
                relevance_factors.append(f"affects_your_player:{player_name}")
        
        # Analyze news type and impact
        title_lower = news_item.get('title', '').lower()
        description_lower = news_item.get('description', '').lower()
        content = f"{title_lower} {description_lower}"
        
        # Check for injury news
        if any(keyword in content for keyword in self.injury_keywords):
            if affected_user_players:
                relevance_score += 5
                player_names = ', '.join([p['name'] for p in affected_user_players])
                personalized_summary = f"⚠️ Injury Alert: {player_names} on your roster may be affected. "
                
                # Suggest backup options
                if 'out' in content or 'doubtful' in content:
                    personalized_summary += "Consider picking up a replacement from waivers. "
                elif 'questionable' in content:
                    personalized_summary += "Monitor status before game time and have a backup ready. "
            else:
                # Injury to non-roster player could be opportunity
                relevance_score += 2
                personalized_summary = "💡 Opportunity: Injury creates potential waiver pickup opportunity. "
        
        # Check for waiver/pickup opportunities
        elif any(keyword in content for keyword in self.opportunity_keywords):
            relevance_score += 3
            
            # Check positions mentioned
            positions = self._extract_positions(content)
            weak_positions = self._identify_weak_positions(user_roster)
            
            matching_positions = set(positions) & set(weak_positions)
            if matching_positions:
                relevance_score += 4
                pos_str = ', '.join(matching_positions)
                personalized_summary = f"🎯 Upgrade Opportunity: Potential improvement at {pos_str} - a position of need for your team. "
            else:
                personalized_summary = "📈 Waiver Alert: Trending player available - consider for depth or trade value. "
        
        # Check for trade news
        elif any(keyword in content for keyword in self.trade_keywords):
            if affected_user_players:
                relevance_score += 8
                player_names = ', '.join([p['name'] for p in affected_user_players])
                personalized_summary = f"🔄 Trade Impact: {player_names} on your roster affected by trade. "
                
                # Analyze if trade helps or hurts
                if any(word in content for word in ['upgrade', 'better', 'improved', 'starting']):
                    personalized_summary += "This could boost their fantasy value! "
                elif any(word in content for word in ['backup', 'behind', 'reduced', 'fewer']):
                    personalized_summary += "Monitor for potential reduced role. Consider selling high. "
            else:
                relevance_score += 1
                personalized_summary = "📊 League News: Trade activity could shift player values across the league. "
        
        # General news about user's players
        elif affected_user_players:
            relevance_score += 5
            player_names = ', '.join([p['name'] for p in affected_user_players])
            
            # Check for positive news
            if any(word in content for word in ['career', 'record', 'best', 'leading', 'hot', 'streak']):
                personalized_summary = f"🔥 Good News: {player_names} performing well. Consider in all lineups. "
            # Check for negative news
            elif any(word in content for word in ['struggling', 'benched', 'poor', 'worst', 'slump']):
                personalized_summary = f"📉 Concern: {player_names} struggling. Monitor situation or consider benching. "
            else:
                personalized_summary = f"📰 Team Update: News about {player_names} on your roster. "
        
        # If no direct relevance, check for competitive advantage
        if relevance_score < 3 and league_teams:
            for team in league_teams:
                team_players = {p['name'].lower() for p in team.get('roster', [])}
                if any(player.lower() in team_players for player in mentioned_players):
                    relevance_score += 1
                    personalized_summary = "🎲 Competitive Intel: Affects your league opponents' rosters. "
                    break
        
        # Set final personalized summary
        if not personalized_summary:
            personalized_summary = "📌 General NFL news that may affect league dynamics. "
        
        # Add actionable recommendations
        recommendations = self._generate_recommendations(news_item, affected_user_players, user_roster)
        if recommendations:
            personalized_summary += recommendations
        
        enhanced_item['personalized_summary'] = personalized_summary
        enhanced_item['relevance_score'] = min(relevance_score, 10)  # Cap at 10
        enhanced_item['affected_players'] = [p['name'] for p in affected_user_players]
        enhanced_item['relevance_factors'] = relevance_factors
        
        return enhanced_item
    
    def _extract_player_names(self, news_item: Dict[str, Any]) -> List[str]:
        """Extract player names from news content"""
        players = []
        
        # Get all text content
        text = f"{news_item.get('title', '')} {news_item.get('description', '')} {news_item.get('content', '')}"
        
        # Look for patterns like "FirstName LastName" (capitalized words)
        # This is simplified - in production you'd use NER or a player database
        pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+(?:Jr\.|Sr\.|III?|IV))?)\b'
        matches = re.findall(pattern, text)
        
        # Filter out common non-player phrases
        non_players = ['National Football', 'Fantasy Football', 'Pro Bowl', 'Super Bowl', 
                       'Monday Night', 'Sunday Night', 'Thursday Night', 'Red Zone']
        
        for match in matches:
            if match not in non_players and len(match.split()) >= 2:
                players.append(match)
        
        # Also check for player tags if available
        if 'player_tags' in news_item:
            players.extend(news_item['player_tags'])
        
        return list(set(players))  # Remove duplicates
    
    def _extract_positions(self, text: str) -> List[str]:
        """Extract position mentions from text"""
        positions = []
        position_keywords = {
            'QB': ['quarterback', 'qb'],
            'RB': ['running back', 'rb', 'halfback'],
            'WR': ['wide receiver', 'wr', 'receiver'],
            'TE': ['tight end', 'te'],
            'K': ['kicker', 'k'],
            'DST': ['defense', 'dst', 'd/st']
        }
        
        text_lower = text.lower()
        for position, keywords in position_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                positions.append(position)
        
        return positions
    
    def _identify_weak_positions(self, roster: List[Dict[str, Any]]) -> List[str]:
        """Identify positions that need improvement on roster"""
        weak_positions = []
        
        # Count players by position
        position_counts = {}
        position_scores = {}
        
        for player in roster:
            pos = player.get('position', '')
            if pos:
                position_counts[pos] = position_counts.get(pos, 0) + 1
                # Accumulate projected points to assess position strength
                score = player.get('projected_points', 0) or player.get('avg_points', 0) or 0
                if pos not in position_scores:
                    position_scores[pos] = []
                position_scores[pos].append(score)
        
        # Check for positions with low depth or low scoring
        ideal_counts = {'QB': 2, 'RB': 4, 'WR': 4, 'TE': 2, 'K': 1, 'DST': 1}
        
        for pos, ideal in ideal_counts.items():
            current = position_counts.get(pos, 0)
            if current < ideal:
                weak_positions.append(pos)
            elif pos in position_scores:
                # Check if average score is low (simplified logic)
                avg_score = sum(position_scores[pos]) / len(position_scores[pos])
                if avg_score < 10:  # Threshold would be position-specific in production
                    weak_positions.append(pos)
        
        return weak_positions
    
    def _generate_recommendations(self, news_item: Dict[str, Any], affected_players: List[Dict[str, Any]], roster: List[Dict[str, Any]]) -> str:
        """Generate actionable recommendations based on news"""
        recommendations = []
        
        content = f"{news_item.get('title', '')} {news_item.get('description', '')}".lower()
        
        # Injury recommendations
        if any(keyword in content for keyword in self.injury_keywords):
            if affected_players:
                for player in affected_players:
                    if 'out' in content or 'ir' in content:
                        recommendations.append(f"Action: Drop {player['name']} if IR slots are full")
                    elif 'questionable' in content:
                        recommendations.append(f"Action: Prepare backup for {player['name']}")
        
        # Breakout recommendations
        if any(keyword in content for keyword in ['breakout', 'hot', 'streak', 'career']):
            if affected_players:
                recommendations.append("Action: Start with confidence")
            else:
                recommendations.append("Action: Add to watchlist or claim off waivers")
        
        # Trade recommendations
        if 'trade' in content:
            if affected_players:
                if any(word in content for word in ['upgrade', 'starter']):
                    recommendations.append("Action: Hold or package in trades while value is high")
                elif any(word in content for word in ['backup', 'reduced']):
                    recommendations.append("Action: Try to trade before value drops further")
        
        if recommendations:
            return " | ".join(recommendations[:2])  # Limit to 2 recommendations
        return ""
    
    def personalize_news_feed(self, news_items: List[Dict[str, Any]], user_roster: List[Dict[str, Any]], league_teams: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Personalize an entire news feed for a user
        
        Args:
            news_items: List of news articles
            user_roster: User's current roster
            league_teams: Other teams in the league
            
        Returns:
            List of enhanced news items sorted by relevance
        """
        personalized_items = []
        
        for item in news_items:
            enhanced = self.analyze_news_relevance(item, user_roster, league_teams)
            personalized_items.append(enhanced)
        
        # Sort by relevance score (highest first)
        personalized_items.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return personalized_items

# Create singleton instance
news_personalizer = NewsPersonalizer()