"""
Comprehensive notification service for fantasy football app.
Monitors player injuries, waiver wire opportunities, and relevant news for user rosters.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database.models import (
    User, League, Team, Player, RosterSlot, Notification, 
    NotificationPreferences, NewsItem
)
from ..platforms.service import PlatformIntegrationService
from ..news.service import NewsAggregationService
from .service import NotificationService, create_notification_service

logger = logging.getLogger(__name__)


class FantasyNotificationService:
    """
    Fantasy-specific notification service that monitors:
    - Player injuries for roster players
    - Waiver wire opportunities based on team needs
    - Relevant news for roster players
    """
    
    def __init__(self, platform_service: PlatformIntegrationService = None,
                 news_service: NewsAggregationService = None,
                 notification_service: NotificationService = None):
        """
        Initialize the fantasy notification service.
        
        Args:
            platform_service: Platform integration service for roster data
            news_service: News aggregation service for breaking news
            notification_service: Base notification service for sending notifications
        """
        self.platform_service = platform_service
        self.news_service = news_service
        self.notification_service = notification_service or create_notification_service()
        
        # Track player status to avoid duplicate notifications
        self.player_injury_cache = {}
        self.player_news_cache = {}
        self.last_monitoring_run = None
        
    def monitor_roster_players(self, db: Session, user_id: str, league_id: str, 
                              team_id: str) -> Dict[str, Any]:
        """
        Monitor all players on a user's roster for injuries and news updates.
        
        Args:
            db: Database session
            user_id: User ID to monitor for
            league_id: League ID
            team_id: Team ID within the league
            
        Returns:
            Dict containing monitoring results and any notifications sent
        """
        try:
            logger.info(f"Monitoring roster players for user {user_id}, team {team_id}")
            
            # Get user's current roster
            roster_players = self._get_roster_players(db, team_id)
            if not roster_players:
                logger.warning(f"No roster players found for team {team_id}")
                return {"status": "warning", "message": "No roster players found"}
            
            notifications_sent = []
            
            # Monitor each player for injuries and news
            for player in roster_players:
                # Check for injury updates
                injury_notifications = self._check_player_injuries(
                    db, user_id, player
                )
                notifications_sent.extend(injury_notifications)
                
                # Check for relevant news
                news_notifications = self._check_player_news(
                    db, user_id, player
                )
                notifications_sent.extend(news_notifications)
            
            # Check for waiver wire opportunities based on roster needs
            waiver_notifications = self._check_waiver_opportunities(
                db, user_id, league_id, team_id, roster_players
            )
            notifications_sent.extend(waiver_notifications)
            
            logger.info(f"Roster monitoring complete. Sent {len(notifications_sent)} notifications")
            
            return {
                "status": "success",
                "roster_size": len(roster_players),
                "notifications_sent": len(notifications_sent),
                "notification_details": notifications_sent
            }
            
        except Exception as e:
            logger.error(f"Error monitoring roster players: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_roster_players(self, db: Session, team_id: str) -> List[Player]:
        """
        Get all players currently on a team's roster.
        
        Args:
            db: Database session
            team_id: Team ID
            
        Returns:
            List of Player objects on the roster
        """
        try:
            # Get current week's roster (assuming current week is stored somewhere)
            current_week = self._get_current_week()
            
            roster_query = (
                db.query(Player)
                .join(RosterSlot, Player.id == RosterSlot.player_id)
                .filter(
                    and_(
                        RosterSlot.team_id == team_id,
                        RosterSlot.week == current_week
                    )
                )
            )
            
            players = roster_query.all()
            logger.debug(f"Found {len(players)} players on team {team_id} roster")
            return players
            
        except Exception as e:
            logger.error(f"Error getting roster players: {e}")
            return []
    
    def _check_player_injuries(self, db: Session, user_id: str, 
                              player: Player) -> List[Dict[str, Any]]:
        """
        Check if a player has new injury status updates.
        
        Args:
            db: Database session
            user_id: User ID to notify
            player: Player object to check
            
        Returns:
            List of notification details if injury status changed
        """
        notifications = []
        
        try:
            player_id = player.id
            current_injury_status = player.injury_status
            
            # Get cached status
            cached_status = self.player_injury_cache.get(player_id)
            
            # If status changed and is concerning (not healthy)
            if (cached_status is not None and 
                cached_status != current_injury_status and 
                current_injury_status > 0):  # 0 = healthy
                
                # Map injury status codes to readable status
                status_map = {
                    0: "healthy",
                    1: "questionable", 
                    2: "doubtful",
                    3: "out"
                }
                
                injury_data = {
                    "player_name": player.name,
                    "status": status_map.get(current_injury_status, "unknown"),
                    "position": player.position,
                    "team": player.team,
                    "previous_status": status_map.get(cached_status, "unknown"),
                    "fantasy_impact": self._assess_injury_impact(current_injury_status)
                }
                
                # Send injury notification
                result = self.notification_service.send_injury_update_notification(
                    db, user_id, injury_data
                )
                
                notifications.append({
                    "type": "injury_update",
                    "player": player.name,
                    "status": injury_data["status"],
                    "notification_result": result
                })
                
                logger.info(f"Sent injury notification for {player.name}: {injury_data['status']}")
            
            # Update cache
            self.player_injury_cache[player_id] = current_injury_status
            
        except Exception as e:
            logger.error(f"Error checking player injuries for {player.name}: {e}")
        
        return notifications
    
    def _check_player_news(self, db: Session, user_id: str, 
                          player: Player) -> List[Dict[str, Any]]:
        """
        Check for relevant news updates about a roster player.
        
        Args:
            db: Database session
            user_id: User ID to notify
            player: Player object to check
            
        Returns:
            List of notification details if relevant news found
        """
        notifications = []
        
        try:
            if not self.news_service:
                return notifications
            
            # Get recent news items
            recent_news = self.news_service.aggregate_news()
            
            # Filter for news about this specific player
            player_news = [
                news for news in recent_news
                if self._is_news_about_player(news, player)
            ]
            
            # Check for high-urgency news we haven't notified about
            for news_item in player_news:
                news_id = news_item.get('id', news_item.get('title', ''))
                
                # Skip if we've already notified about this news
                if news_id in self.player_news_cache.get(player.id, set()):
                    continue
                
                # Only notify about high-urgency news (4 or 5)
                urgency = news_item.get('urgency_score', 1)
                if urgency >= 4:
                    news_data = {
                        "headline": news_item.get('title', 'Fantasy News'),
                        "summary": news_item.get('summary', '')[:200] + "...",
                        "urgency_score": urgency,
                        "affected_players": [player.name],
                        "source": news_item.get('source', 'Unknown'),
                        "player_position": player.position,
                        "player_team": player.team
                    }
                    
                    # Send breaking news notification
                    result = self.notification_service.send_breaking_news_notification(
                        db, user_id, news_data
                    )
                    
                    notifications.append({
                        "type": "player_news",
                        "player": player.name,
                        "headline": news_data["headline"],
                        "urgency": urgency,
                        "notification_result": result
                    })
                    
                    # Update cache
                    if player.id not in self.player_news_cache:
                        self.player_news_cache[player.id] = set()
                    self.player_news_cache[player.id].add(news_id)
                    
                    logger.info(f"Sent news notification for {player.name}: {news_data['headline']}")
                    
        except Exception as e:
            logger.error(f"Error checking player news for {player.name}: {e}")
        
        return notifications
    
    def _check_waiver_opportunities(self, db: Session, user_id: str, league_id: str,
                                   team_id: str, roster_players: List[Player]) -> List[Dict[str, Any]]:
        """
        Check for waiver wire opportunities based on roster needs.
        
        Args:
            db: Database session
            user_id: User ID to notify
            league_id: League ID
            team_id: Team ID
            roster_players: Current roster players
            
        Returns:
            List of notification details for waiver opportunities
        """
        notifications = []
        
        try:
            # Analyze roster needs
            roster_needs = self._analyze_roster_needs(roster_players)
            
            if not roster_needs:
                return notifications
            
            # Get available free agents using platform service
            if not self.platform_service:
                return notifications
            
            # Check for high-value free agents at needed positions
            for position in roster_needs:
                try:
                    # Get free agents at this position
                    free_agents = self._get_top_free_agents_by_position(
                        league_id, position, limit=5
                    )
                    
                    # Find high-value opportunities
                    for agent in free_agents:
                        if self._is_high_value_pickup(agent, position, roster_players):
                            waiver_data = {
                                "player_name": agent.get('name', 'Unknown'),
                                "position": position,
                                "team": agent.get('team', 'Unknown'),
                                "projected_points": agent.get('projected_points', 0),
                                "percent_owned": agent.get('percent_owned', 0),
                                "recommendation": "CLAIM",
                                "reason": f"High-value {position} available on waivers",
                                "roster_need": roster_needs[position]
                            }
                            
                            # Create custom waiver notification
                            title = f"🎯 Waiver Wire Opportunity: {waiver_data['player_name']}"
                            message = f"""
High-value {position} available on waivers!

Player: {waiver_data['player_name']} ({waiver_data['team']})
Projected Points: {waiver_data['projected_points']:.1f}
Ownership: {waiver_data['percent_owned']:.1f}%

Reason: {waiver_data['reason']}
Team Need: {waiver_data['roster_need']}

Consider claiming this player to strengthen your roster!
                            """.strip()
                            
                            result = self.notification_service.send_notification(
                                db, user_id, title, message, "waiver", 
                                priority=3, data=waiver_data
                            )
                            
                            notifications.append({
                                "type": "waiver_opportunity",
                                "player": waiver_data['player_name'],
                                "position": position,
                                "notification_result": result
                            })
                            
                            logger.info(f"Sent waiver opportunity notification for {waiver_data['player_name']}")
                            
                except Exception as e:
                    logger.error(f"Error checking waiver opportunities for {position}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking waiver opportunities: {e}")
        
        return notifications
    
    def _analyze_roster_needs(self, roster_players: List[Player]) -> Dict[str, str]:
        """
        Analyze roster to identify positional needs.
        
        Args:
            roster_players: List of current roster players
            
        Returns:
            Dict mapping positions to need descriptions
        """
        position_counts = {}
        injured_positions = set()
        
        for player in roster_players:
            position = player.position
            position_counts[position] = position_counts.get(position, 0) + 1
            
            # Track positions with injured players
            if player.injury_status >= 2:  # Doubtful or Out
                injured_positions.add(position)
        
        needs = {}
        
        # Standard roster requirements (can be customized)
        min_requirements = {
            'QB': 2,
            'RB': 4, 
            'WR': 4,
            'TE': 2,
            'DEF': 2,
            'K': 2
        }
        
        for position, min_needed in min_requirements.items():
            current_count = position_counts.get(position, 0)
            
            if current_count < min_needed:
                needs[position] = f"Below minimum depth ({current_count}/{min_needed})"
            elif position in injured_positions:
                needs[position] = f"Injured players at position"
        
        return needs
    
    def _get_top_free_agents_by_position(self, league_id: str, position: str, 
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top free agents at a specific position.
        
        Args:
            league_id: League ID
            position: Position to search for
            limit: Number of players to return
            
        Returns:
            List of free agent player data
        """
        try:
            if not self.platform_service:
                return []
            
            # Get free agents from platform (ESPN/Sleeper)
            free_agents = self.platform_service.get_free_agents(
                "espn", league_id, position=position, size=limit
            )
            
            return free_agents or []
            
        except Exception as e:
            logger.error(f"Error getting free agents for {position}: {e}")
            return []
    
    def _is_high_value_pickup(self, free_agent: Dict[str, Any], position: str, 
                             roster_players: List[Player]) -> bool:
        """
        Determine if a free agent is a high-value pickup.
        
        Args:
            free_agent: Free agent player data
            position: Position of the player
            roster_players: Current roster players
            
        Returns:
            True if this is a high-value pickup opportunity
        """
        try:
            projected_points = free_agent.get('projected_points', 0)
            percent_owned = free_agent.get('percent_owned', 100)
            
            # High-value criteria:
            # 1. Low ownership (< 50%) but decent projections
            # 2. Recent breakout performance
            # 3. Better than worst player at same position on roster
            
            if percent_owned > 75:  # Too widely owned
                return False
            
            # Position-specific thresholds
            min_projections = {
                'QB': 15,
                'RB': 8,
                'WR': 8,
                'TE': 6,
                'DEF': 5,
                'K': 5
            }
            
            min_projection = min_projections.get(position, 5)
            
            if projected_points < min_projection:
                return False
            
            # Compare to worst player at same position on roster
            same_position_players = [p for p in roster_players if p.position == position]
            if same_position_players:
                worst_projection = min([p.projected_points for p in same_position_players])
                if projected_points > worst_projection + 2:  # Meaningful improvement
                    return True
            
            # Consider it high-value if decent projections and low ownership
            return projected_points >= min_projection and percent_owned < 30
            
        except Exception as e:
            logger.error(f"Error evaluating pickup value: {e}")
            return False
    
    def _is_news_about_player(self, news_item: Dict[str, Any], player: Player) -> bool:
        """
        Check if a news item is about a specific player.
        
        Args:
            news_item: News item data
            player: Player object
            
        Returns:
            True if news is about this player
        """
        try:
            title = news_item.get('title', '').lower()
            summary = news_item.get('summary', '').lower()
            player_name = player.name.lower()
            
            # Simple name matching (could be enhanced with fuzzy matching)
            name_parts = player_name.split()
            
            # Check if any part of the player's name appears in title or summary
            for part in name_parts:
                if len(part) > 2 and (part in title or part in summary):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking news relevance: {e}")
            return False
    
    def _assess_injury_impact(self, injury_status: int) -> str:
        """
        Assess the fantasy impact of an injury status.
        
        Args:
            injury_status: Injury status code (0-3)
            
        Returns:
            String describing fantasy impact
        """
        impact_map = {
            0: "No impact - player healthy",
            1: "Monitor closely - game-time decision likely",
            2: "Consider backup options - unlikely to play", 
            3: "Immediate action needed - player will not play"
        }
        
        return impact_map.get(injury_status, "Unknown impact")
    
    def _get_current_week(self) -> int:
        """
        Get current NFL week.
        
        Returns:
            Current NFL week (1-18)
        """
        # Simple implementation - in production would use actual NFL schedule
        import datetime
        now = datetime.datetime.now()
        week_of_year = now.isocalendar()[1]
        
        # Estimate NFL week (season typically starts around week 36)
        if week_of_year >= 36:
            return min(week_of_year - 35, 18)
        elif week_of_year <= 18:
            return week_of_year
        else:
            return 1
    
    def monitor_all_users(self, db: Session) -> Dict[str, Any]:
        """
        Monitor all users' rosters for notifications.
        
        Args:
            db: Database session
            
        Returns:
            Summary of monitoring results
        """
        try:
            logger.info("Starting comprehensive user roster monitoring")
            
            # Get all active users with teams
            users_with_teams = (
                db.query(User, Team, League)
                .join(League, User.id == League.user_id)
                .join(Team, League.id == Team.league_id)
                .all()
            )
            
            total_notifications = 0
            users_processed = 0
            errors = []
            
            for user, team, league in users_with_teams:
                try:
                    result = self.monitor_roster_players(
                        db, user.id, league.id, team.id
                    )
                    
                    if result.get("status") == "success":
                        total_notifications += result.get("notifications_sent", 0)
                        users_processed += 1
                    else:
                        errors.append(f"User {user.id}: {result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    error_msg = f"User {user.id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"Error monitoring user {user.id}: {e}")
            
            # Update last monitoring run timestamp
            self.last_monitoring_run = datetime.utcnow()
            
            summary = {
                "status": "completed",
                "users_processed": users_processed,
                "total_notifications_sent": total_notifications,
                "errors": errors,
                "monitoring_timestamp": self.last_monitoring_run.isoformat()
            }
            
            logger.info(f"Monitoring complete: {users_processed} users, {total_notifications} notifications")
            return summary
            
        except Exception as e:
            logger.error(f"Error in comprehensive monitoring: {e}")
            return {
                "status": "error",
                "message": str(e),
                "monitoring_timestamp": datetime.utcnow().isoformat()
            }
    
    def clear_caches(self):
        """Clear all internal caches."""
        self.player_injury_cache.clear()
        self.player_news_cache.clear()
        logger.info("Notification service caches cleared")