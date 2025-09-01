"""
Intelligent Notification System for Fantasy Football
Provides smart, actionable notifications based on news and team context
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications"""
    INJURY_ALERT = "injury_alert"
    WAIVER_OPPORTUNITY = "waiver_opportunity"  
    TRADE_DEADLINE = "trade_deadline"
    LINEUP_CHANGE = "lineup_change"
    STRATEGIC_BLOCK = "strategic_block"
    OPPONENT_WEAKNESS = "opponent_weakness"
    BREAKOUT_ALERT = "breakout_alert"
    VALUE_CHANGE = "value_change"
    WEATHER_ALERT = "weather_alert"
    INSIDER_TIP = "insider_tip"

class NotificationPriority(Enum):
    """Priority levels for notifications"""
    URGENT = 1  # Immediate action required
    HIGH = 2    # Action needed within hours
    MEDIUM = 3  # Action needed within a day
    LOW = 4     # Informational

@dataclass
class SmartNotification:
    """Enhanced notification with context and recommendations"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    affected_players: List[str]
    recommended_actions: List[Dict[str, Any]]
    context: Dict[str, Any]  # League-specific context
    expires_at: Optional[datetime]
    created_at: datetime
    source: str
    confidence_score: float  # 0-1 confidence in recommendation

class IntelligentNotificationEngine:
    """
    Engine for generating intelligent, actionable fantasy football notifications
    """
    
    def __init__(self, user_team_id: str, league_id: str):
        self.user_team_id = user_team_id
        self.league_id = league_id
        self.notification_history = []
        
    def generate_notifications(self,
                              news_items: List[Any],
                              user_roster: List[Dict],
                              league_context: Dict,
                              upcoming_matchups: List[Dict]) -> List[SmartNotification]:
        """
        Generate smart notifications based on news and context
        
        Args:
            news_items: Recent news items from monitoring
            user_roster: User's current roster
            league_context: League standings, settings, etc.
            upcoming_matchups: Upcoming matchups for user's team
            
        Returns:
            List of smart notifications
        """
        notifications = []
        
        # Process each news item for potential notifications
        for news in news_items:
            # Check for injury impacts
            injury_notif = self._check_injury_impact(news, user_roster)
            if injury_notif:
                notifications.append(injury_notif)
            
            # Check for waiver opportunities
            waiver_notif = self._check_waiver_opportunity(news, user_roster, league_context)
            if waiver_notif:
                notifications.append(waiver_notif)
            
            # Check for strategic blocking opportunities
            block_notif = self._check_strategic_block(news, league_context, upcoming_matchups)
            if block_notif:
                notifications.append(block_notif)
            
            # Check for value changes
            value_notif = self._check_value_change(news, user_roster)
            if value_notif:
                notifications.append(value_notif)
        
        # Add matchup-based notifications
        matchup_notifs = self._generate_matchup_notifications(upcoming_matchups, user_roster)
        notifications.extend(matchup_notifs)
        
        # Sort by priority and deduplicate
        notifications = self._prioritize_and_dedupe(notifications)
        
        return notifications
    
    def _check_injury_impact(self, news: Any, user_roster: List[Dict]) -> Optional[SmartNotification]:
        """Check if news impacts user's players via injury"""
        affected_players = []
        
        for player in user_roster:
            if player['name'] in news.players_mentioned:
                if any(word in news.content.lower() for word in ['injury', 'injured', 'questionable', 'doubtful', 'out']):
                    affected_players.append(player['name'])
        
        if affected_players:
            # Determine severity
            if 'out' in news.content.lower() or 'doubtful' in news.content.lower():
                priority = NotificationPriority.URGENT
                message = f"URGENT: {affected_players[0]} is likely OUT. You need an immediate replacement."
            elif 'questionable' in news.content.lower():
                priority = NotificationPriority.HIGH
                message = f"{affected_players[0]} is questionable. Monitor closely and have a backup ready."
            else:
                priority = NotificationPriority.MEDIUM
                message = f"{affected_players[0]} has an injury update. Check status before lineup lock."
            
            return SmartNotification(
                id=f"injury_{news.timestamp}_{affected_players[0]}",
                type=NotificationType.INJURY_ALERT,
                priority=priority,
                title=f"Injury Alert: {affected_players[0]}",
                message=message,
                affected_players=affected_players,
                recommended_actions=[
                    {
                        "action": "check_waiver",
                        "description": "Check waiver wire for replacement",
                        "suggested_players": self._get_replacement_suggestions(affected_players[0])
                    },
                    {
                        "action": "set_lineup",
                        "description": "Update your lineup before game time"
                    }
                ],
                context={"injury_details": news.content[:200]},
                expires_at=self._get_next_game_time(affected_players[0]),
                created_at=datetime.now(),
                source=news.source,
                confidence_score=0.9 if 'confirmed' in news.content.lower() else 0.7
            )
        
        return None
    
    def _check_waiver_opportunity(self, news: Any, user_roster: List[Dict], 
                                  league_context: Dict) -> Optional[SmartNotification]:
        """Check for waiver wire opportunities"""
        
        # Keywords indicating opportunity
        opportunity_keywords = ['breakout', 'starting', 'promoted', 'impressive', 
                              'taking over', 'lead back', 'wr1', 'increased snaps']
        
        if any(keyword in news.content.lower() for keyword in opportunity_keywords):
            players_to_add = []
            
            for player in news.players_mentioned:
                # Check if player is not on user roster
                if not any(p['name'] == player for p in user_roster):
                    players_to_add.append(player)
            
            if players_to_add:
                return SmartNotification(
                    id=f"waiver_{news.timestamp}_{players_to_add[0]}",
                    type=NotificationType.WAIVER_OPPORTUNITY,
                    priority=NotificationPriority.HIGH,
                    title=f"Hot Waiver Add: {players_to_add[0]}",
                    message=f"{players_to_add[0]} is emerging as a must-add. {news.strategic_analysis}",
                    affected_players=players_to_add,
                    recommended_actions=[
                        {
                            "action": "add_player",
                            "player": players_to_add[0],
                            "drop_candidates": self._get_drop_candidates(user_roster),
                            "faab_recommendation": self._calculate_faab_bid(players_to_add[0], league_context)
                        }
                    ],
                    context={
                        "news_summary": news.content[:200],
                        "ownership_percentage": self._get_ownership_percentage(players_to_add[0])
                    },
                    expires_at=self._get_next_waiver_deadline(),
                    created_at=datetime.now(),
                    source=news.source,
                    confidence_score=self._calculate_opportunity_confidence(news)
                )
        
        return None
    
    def _check_strategic_block(self, news: Any, league_context: Dict, 
                               upcoming_matchups: List[Dict]) -> Optional[SmartNotification]:
        """Check for strategic blocking opportunities"""
        
        # Identify if news benefits upcoming opponents
        for matchup in upcoming_matchups[:3]:  # Next 3 matchups
            opponent = matchup.get('opponent')
            opponent_needs = self._analyze_opponent_needs(opponent, league_context)
            
            for player in news.players_mentioned:
                if self._player_fills_need(player, opponent_needs):
                    return SmartNotification(
                        id=f"block_{news.timestamp}_{player}_{opponent}",
                        type=NotificationType.STRATEGIC_BLOCK,
                        priority=NotificationPriority.MEDIUM,
                        title=f"Block {opponent}: Add {player}",
                        message=f"Your upcoming opponent {opponent} needs a {opponent_needs[0]}. "
                               f"Adding {player} would block them and could swing your matchup.",
                        affected_players=[player],
                        recommended_actions=[
                            {
                                "action": "strategic_add",
                                "player": player,
                                "reason": f"Block {opponent} who needs {opponent_needs[0]}",
                                "impact": "Could swing 5-10 points in your favor"
                            }
                        ],
                        context={
                            "opponent": opponent,
                            "opponent_needs": opponent_needs,
                            "matchup_week": matchup.get('week')
                        },
                        expires_at=self._get_next_waiver_deadline(),
                        created_at=datetime.now(),
                        source="strategic_analysis",
                        confidence_score=0.75
                    )
        
        return None
    
    def _check_value_change(self, news: Any, user_roster: List[Dict]) -> Optional[SmartNotification]:
        """Check for player value changes"""
        
        value_keywords = {
            'increase': ['promoted', 'starting', 'breakout', 'impressive'],
            'decrease': ['benched', 'demoted', 'struggling', 'losing snaps']
        }
        
        for player in user_roster:
            if player['name'] in news.players_mentioned:
                # Check for value increase
                if any(keyword in news.content.lower() for keyword in value_keywords['increase']):
                    return SmartNotification(
                        id=f"value_up_{news.timestamp}_{player['name']}",
                        type=NotificationType.VALUE_CHANGE,
                        priority=NotificationPriority.MEDIUM,
                        title=f"📈 {player['name']} Value Rising",
                        message=f"Good news! {player['name']}'s value is increasing. "
                               f"Consider this for trade negotiations or hold tight.",
                        affected_players=[player['name']],
                        recommended_actions=[
                            {
                                "action": "hold",
                                "reason": "Value trending up - don't sell low"
                            },
                            {
                                "action": "shop_trades",
                                "reason": "Use increased value to upgrade at weak positions"
                            }
                        ],
                        context={"value_trend": "increasing"},
                        expires_at=None,
                        created_at=datetime.now(),
                        source=news.source,
                        confidence_score=0.8
                    )
                
                # Check for value decrease
                elif any(keyword in news.content.lower() for keyword in value_keywords['decrease']):
                    return SmartNotification(
                        id=f"value_down_{news.timestamp}_{player['name']}",
                        type=NotificationType.VALUE_CHANGE,
                        priority=NotificationPriority.HIGH,
                        title=f"📉 {player['name']} Value Declining",
                        message=f"Warning: {player['name']}'s value is dropping. "
                               f"Consider trading now before it drops further.",
                        affected_players=[player['name']],
                        recommended_actions=[
                            {
                                "action": "trade_away",
                                "urgency": "high",
                                "reason": "Sell before value drops further"
                            },
                            {
                                "action": "find_replacement",
                                "suggested_targets": self._get_replacement_suggestions(player['name'])
                            }
                        ],
                        context={"value_trend": "decreasing"},
                        expires_at=datetime.now() + timedelta(days=2),
                        created_at=datetime.now(),
                        source=news.source,
                        confidence_score=0.85
                    )
        
        return None
    
    def _generate_matchup_notifications(self, upcoming_matchups: List[Dict], 
                                       user_roster: List[Dict]) -> List[SmartNotification]:
        """Generate notifications based on upcoming matchups"""
        notifications = []
        
        for matchup in upcoming_matchups[:2]:  # Next 2 matchups
            # Check for favorable matchups
            for player in user_roster:
                matchup_rating = self._analyze_matchup(player, matchup)
                
                if matchup_rating > 8:  # Excellent matchup
                    notifications.append(SmartNotification(
                        id=f"matchup_{matchup['week']}_{player['name']}",
                        type=NotificationType.LINEUP_CHANGE,
                        priority=NotificationPriority.MEDIUM,
                        title=f"Start {player['name']} - Elite Matchup",
                        message=f"{player['name']} has an elite matchup against {matchup['opponent']}. "
                               f"Must-start this week!",
                        affected_players=[player['name']],
                        recommended_actions=[
                            {
                                "action": "set_lineup",
                                "player": player['name'],
                                "position": "FLEX/START",
                                "confidence": "very_high"
                            }
                        ],
                        context={
                            "matchup_rating": matchup_rating,
                            "opponent_weakness": self._get_opponent_weakness(matchup['opponent'])
                        },
                        expires_at=matchup['game_time'],
                        created_at=datetime.now(),
                        source="matchup_analysis",
                        confidence_score=0.9
                    ))
        
        return notifications
    
    def _prioritize_and_dedupe(self, notifications: List[SmartNotification]) -> List[SmartNotification]:
        """Prioritize and remove duplicate notifications"""
        # Remove duplicates based on affected players and type
        seen = set()
        unique_notifications = []
        
        for notif in notifications:
            key = (notif.type, tuple(notif.affected_players))
            if key not in seen:
                seen.add(key)
                unique_notifications.append(notif)
        
        # Sort by priority
        return sorted(unique_notifications, key=lambda x: (x.priority.value, -x.confidence_score))
    
    # Helper methods
    def _get_replacement_suggestions(self, player_name: str) -> List[str]:
        """Get suggested replacement players"""
        # This would query available players based on position
        return ["Backup Player 1", "Waiver Target 1", "Free Agent 1"]
    
    def _calculate_faab_bid(self, player: str, league_context: Dict) -> int:
        """Calculate recommended FAAB bid"""
        # Complex logic based on player value, league competitiveness, budget remaining
        return 15  # Placeholder
    
    def _get_ownership_percentage(self, player: str) -> float:
        """Get player ownership percentage"""
        # Would query from database
        return 12.5  # Placeholder
    
    def _calculate_opportunity_confidence(self, news: Any) -> float:
        """Calculate confidence in opportunity"""
        confidence = 0.5
        
        # Source credibility
        if news.source in ["Schefter", "Rapoport"]:
            confidence += 0.3
        
        # Recency
        hours_old = (datetime.now() - news.timestamp).total_seconds() / 3600
        if hours_old < 1:
            confidence += 0.2
        elif hours_old < 6:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_next_waiver_deadline(self) -> datetime:
        """Get next waiver deadline"""
        # Typically Tuesday night/Wednesday morning
        days_ahead = 2 - datetime.now().weekday()  # Tuesday is 1
        if days_ahead <= 0:
            days_ahead += 7
        return datetime.now() + timedelta(days=days_ahead)
    
    def _get_next_game_time(self, player: str) -> datetime:
        """Get next game time for player"""
        # Would query from schedule
        return datetime.now() + timedelta(days=3)  # Placeholder
    
    def _analyze_opponent_needs(self, opponent: str, league_context: Dict) -> List[str]:
        """Analyze what positions opponent needs"""
        # Would analyze opponent's roster
        return ["RB", "WR"]  # Placeholder
    
    def _player_fills_need(self, player: str, needs: List[str]) -> bool:
        """Check if player fills opponent's need"""
        # Would check player position against needs
        return True  # Placeholder
    
    def _analyze_matchup(self, player: Dict, matchup: Dict) -> float:
        """Analyze matchup favorability (0-10)"""
        # Would analyze defensive rankings, historical performance
        return 7.5  # Placeholder
    
    def _get_opponent_weakness(self, opponent: str) -> str:
        """Get opponent's defensive weakness"""
        # Would query defensive stats
        return "Weak against pass-catching RBs"  # Placeholder
    
    def _get_drop_candidates(self, roster: List[Dict]) -> List[str]:
        """Get players that could be dropped"""
        # Would analyze roster for weakest players
        return ["Bench Player 1", "Bench Player 2"]  # Placeholder


class NotificationFormatter:
    """Format notifications for display"""
    
    @staticmethod
    def format_for_ui(notification: SmartNotification) -> Dict:
        """Format notification for UI display"""
        return {
            "id": notification.id,
            "type": notification.type.value,
            "priority": notification.priority.name,
            "title": notification.title,
            "message": notification.message,
            "actions": notification.recommended_actions,
            "timestamp": notification.created_at.isoformat(),
            "expires": notification.expires_at.isoformat() if notification.expires_at else None,
            "confidence": f"{notification.confidence_score * 100:.0f}%",
            "source": notification.source
        }
    
    @staticmethod
    def format_for_email(notification: SmartNotification) -> str:
        """Format notification for email"""
        email_body = f"""
        {notification.title}
        {'=' * len(notification.title)}
        
        {notification.message}
        
        Affected Players: {', '.join(notification.affected_players)}
        
        Recommended Actions:
        """
        
        for action in notification.recommended_actions:
            email_body += f"\n• {action.get('description', action.get('action'))}"
        
        email_body += f"\n\nConfidence: {notification.confidence_score * 100:.0f}%"
        email_body += f"\nSource: {notification.source}"
        
        if notification.expires_at:
            email_body += f"\nAction Required By: {notification.expires_at.strftime('%Y-%m-%d %H:%M')}"
        
        return email_body
    
    @staticmethod
    def format_for_push(notification: SmartNotification) -> Dict:
        """Format notification for push notification"""
        return {
            "title": notification.title,
            "body": notification.message[:100] + "..." if len(notification.message) > 100 else notification.message,
            "data": {
                "type": notification.type.value,
                "priority": notification.priority.value,
                "notification_id": notification.id
            }
        }