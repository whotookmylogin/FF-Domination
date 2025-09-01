import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database.connection import get_db
from ..database.models import User, League, NotificationPreferences, NotificationQueue
from .service import NotificationService, create_notification_service

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """
    Notification scheduler for automated notifications.
    """
    
    def __init__(self, notification_service: NotificationService = None):
        """
        Initialize notification scheduler.
        
        Args:
            notification_service (NotificationService): Notification service instance
        """
        self.notification_service = notification_service or create_notification_service()
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the notification scheduler."""
        if self.running:
            logger.warning("Notification scheduler is already running")
            return
        
        logger.info("Starting notification scheduler...")
        self.running = True
        
        # Schedule different types of notifications
        self._setup_schedules()
        
        # Start the scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Notification scheduler started successfully")
    
    def stop(self):
        """Stop the notification scheduler."""
        logger.info("Stopping notification scheduler...")
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Notification scheduler stopped")
    
    def _setup_schedules(self):
        """Set up all scheduled notification tasks."""
        
        # Process notification queue every minute
        schedule.every(1).minutes.do(self.process_notification_queue)
        
        # Send lineup reminders (Sundays at 10 AM and 1 PM)
        schedule.every().sunday.at("10:00").do(self.send_lineup_reminders)
        schedule.every().sunday.at("13:00").do(self.send_lineup_reminders)
        
        # Process waiver wire results (Wednesdays at 4 AM)
        schedule.every().wednesday.at("04:00").do(self.process_waiver_results)
        
        # Check for breaking news (every 15 minutes)
        schedule.every(15).minutes.do(self.check_breaking_news)
        
        # Send weekly summary notifications (Tuesdays at 9 AM)
        schedule.every().tuesday.at("09:00").do(self.send_weekly_summaries)
        
        logger.info("Notification schedules set up successfully")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
    
    def process_notification_queue(self):
        """
        Process queued notifications that are ready to be sent.
        """
        try:
            logger.debug("Processing notification queue...")
            
            with next(get_db()) as db:
                # Get pending notifications that are ready to be sent
                now = datetime.utcnow()
                pending_notifications = db.query(NotificationQueue).filter(
                    and_(
                        NotificationQueue.status == 'pending',
                        NotificationQueue.scheduled_at <= now
                    )
                ).limit(50).all()  # Process up to 50 at a time
                
                processed_count = 0
                for queue_item in pending_notifications:
                    try:
                        # Mark as processing
                        queue_item.status = 'processing'
                        queue_item.updated_at = now
                        db.commit()
                        
                        # Get the notification details
                        notification = queue_item.notification
                        if not notification:
                            logger.warning(f"Notification not found for queue item {queue_item.id}")
                            queue_item.status = 'failed'
                            queue_item.error_message = 'Notification not found'
                            db.commit()
                            continue
                        
                        # Process based on channel
                        success = self._process_queue_item(db, queue_item, notification)
                        
                        if success:
                            queue_item.status = 'sent'
                            queue_item.processed_at = now
                            logger.debug(f"Successfully processed queue item {queue_item.id}")
                        else:
                            # Retry logic
                            queue_item.retry_count += 1
                            if queue_item.retry_count >= queue_item.max_retries:
                                queue_item.status = 'failed'
                                logger.warning(f"Queue item {queue_item.id} failed after {queue_item.max_retries} retries")
                            else:
                                queue_item.status = 'pending'
                                # Retry in 5 minutes
                                queue_item.scheduled_at = now + timedelta(minutes=5)
                                logger.debug(f"Retrying queue item {queue_item.id} in 5 minutes")
                        
                        queue_item.updated_at = now
                        db.commit()
                        processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing queue item {queue_item.id}: {e}")
                        queue_item.status = 'failed'
                        queue_item.error_message = str(e)
                        queue_item.updated_at = now
                        db.commit()
                
                if processed_count > 0:
                    logger.info(f"Processed {processed_count} queued notifications")
                    
        except Exception as e:
            logger.error(f"Error in process_notification_queue: {e}")
    
    def _process_queue_item(self, db: Session, queue_item: NotificationQueue, 
                           notification) -> bool:
        """
        Process a single queue item.
        
        Args:
            db (Session): Database session
            queue_item (NotificationQueue): Queue item to process
            notification: Notification object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user = db.query(User).filter(User.id == notification.user_id).first()
            if not user:
                logger.warning(f"User not found for notification {notification.id}")
                return False
            
            channel = queue_item.channel
            title = notification.title
            message = notification.message
            data = notification.data
            
            if channel == 'email' and user.email:
                result = self.notification_service.email_service.send_email(
                    user.email, title, message
                )
                return result.get('success', False)
                
            elif channel == 'push':
                device_tokens = data.get('device_tokens', []) if data else []
                result = self.notification_service.push_service.send_push_notification(
                    device_tokens, title, message, data
                )
                return result.get('success', False)
                
            elif channel == 'sms':
                preferences = self.notification_service.get_user_preferences(db, user.id)
                if preferences.sms_phone_number:
                    result = self.notification_service.sms_service.send_sms(
                        preferences.sms_phone_number, f"{title}\n\n{message}"
                    )
                    return result.get('success', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing queue item: {e}")
            return False
    
    def send_lineup_reminders(self):
        """
        Send lineup reminder notifications to users.
        """
        try:
            logger.info("Sending lineup reminders...")
            
            with next(get_db()) as db:
                # Get all users who have lineup reminders enabled
                users = db.query(User).join(NotificationPreferences).filter(
                    and_(
                        NotificationPreferences.email_lineup_reminders == True,
                        NotificationPreferences.email_enabled == True
                    )
                ).all()
                
                current_week = self._get_current_nfl_week()
                hours_until_games = self._get_hours_until_games()
                
                # Only send reminders if games are within the next 6 hours
                if hours_until_games and hours_until_games <= 6:
                    sent_count = 0
                    for user in users:
                        try:
                            reminder_data = {
                                "week": current_week,
                                "hours_until_games": hours_until_games
                            }
                            
                            self.notification_service.send_lineup_reminder_notification(
                                db, user.id, reminder_data
                            )
                            sent_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error sending lineup reminder to user {user.id}: {e}")
                    
                    logger.info(f"Sent lineup reminders to {sent_count} users")
                else:
                    logger.debug(f"Skipping lineup reminders - games not within reminder window ({hours_until_games} hours)")
                    
        except Exception as e:
            logger.error(f"Error in send_lineup_reminders: {e}")
    
    def process_waiver_results(self):
        """
        Process and send waiver wire result notifications.
        """
        try:
            logger.info("Processing waiver wire results...")
            
            with next(get_db()) as db:
                # Get all leagues that had waiver processing
                leagues = db.query(League).all()
                
                for league in leagues:
                    try:
                        # In a real implementation, you would:
                        # 1. Check if waiver processing happened overnight
                        # 2. Get waiver results from the platform
                        # 3. Send notifications to affected users
                        
                        # Mock waiver results for demonstration
                        mock_waiver_data = {
                            "successful_claims": [
                                {"player_name": "Backup RB", "bid_amount": 15}
                            ],
                            "failed_claims": [
                                {"player_name": "Handcuff WR", "winning_bid": 25}
                            ]
                        }
                        
                        # Get league teams/users and send notifications
                        teams = league.teams
                        for team in teams:
                            # In reality, you'd only notify users who had waiver activity
                            if mock_waiver_data['successful_claims'] or mock_waiver_data['failed_claims']:
                                self.notification_service.send_waiver_results_notification(
                                    db, league.user_id, mock_waiver_data
                                )
                        
                        logger.debug(f"Processed waiver results for league {league.id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing waiver results for league {league.id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in process_waiver_results: {e}")
    
    def check_breaking_news(self):
        """
        Check for breaking news and send urgent notifications.
        """
        try:
            logger.debug("Checking for breaking news...")
            
            with next(get_db()) as db:
                # In a real implementation, you would:
                # 1. Check news sources for breaking news
                # 2. Identify high-urgency items (urgency >= 4)
                # 3. Send notifications to affected users
                
                # For now, we'll just log that we checked
                logger.debug("Breaking news check completed (mock implementation)")
                
        except Exception as e:
            logger.error(f"Error in check_breaking_news: {e}")
    
    def send_weekly_summaries(self):
        """
        Send weekly summary notifications.
        """
        try:
            logger.info("Sending weekly summaries...")
            
            with next(get_db()) as db:
                # Get users who want weekly summaries
                users = db.query(User).join(NotificationPreferences).filter(
                    and_(
                        NotificationPreferences.email_enabled == True,
                        NotificationPreferences.email_lineup_reminders == True  # Using this as proxy for wanting summaries
                    )
                ).all()
                
                current_week = self._get_current_nfl_week()
                
                sent_count = 0
                for user in users:
                    try:
                        summary_data = {
                            "week": current_week - 1,  # Previous week summary
                            "highlights": [
                                "Your team scored 125.4 points",
                                "You won your matchup by 12.8 points", 
                                "Your waiver claim for Player X was successful"
                            ]
                        }
                        
                        # Send as a general notification
                        self.notification_service.send_notification(
                            db, user.id, 
                            f"📊 Week {current_week - 1} Summary",
                            f"Here's your weekly fantasy football summary:\n\n" + 
                            "\n".join([f"• {highlight}" for highlight in summary_data['highlights']]),
                            "weekly_summary", priority=1, data=summary_data
                        )
                        sent_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error sending weekly summary to user {user.id}: {e}")
                
                logger.info(f"Sent weekly summaries to {sent_count} users")
                
        except Exception as e:
            logger.error(f"Error in send_weekly_summaries: {e}")
    
    def _get_current_nfl_week(self) -> int:
        """
        Get the current NFL week.
        
        Returns:
            int: Current NFL week (1-18)
        """
        # Simple implementation - in reality you'd calculate based on NFL schedule
        # For now, return a mock week number
        import datetime
        week_of_year = datetime.datetime.now().isocalendar()[1]
        # Assuming NFL season starts around week 36 and goes for 18 weeks
        if week_of_year >= 36:
            return min(week_of_year - 35, 18)
        elif week_of_year <= 18:
            return week_of_year
        else:
            return 1  # Off-season
    
    def _get_hours_until_games(self) -> int:
        """
        Get hours until the next NFL games start.
        
        Returns:
            int: Hours until games start, None if not a game day
        """
        # Simple implementation - assumes Sunday games start at 1 PM EST
        now = datetime.now()
        
        if now.weekday() == 6:  # Sunday
            game_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
            if now < game_time:
                delta = game_time - now
                return int(delta.total_seconds() / 3600)
        
        return None
    
    def schedule_notification(self, db: Session, notification_id: str, 
                             channels: List[str], scheduled_at: datetime):
        """
        Schedule a notification to be sent at a specific time.
        
        Args:
            db (Session): Database session
            notification_id (str): Notification ID
            channels (list): List of channels to send through
            scheduled_at (datetime): When to send the notification
        """
        self.notification_service.queue_notification(
            db, notification_id, channels, scheduled_at
        )
        logger.info(f"Scheduled notification {notification_id} for {scheduled_at}")

# Global scheduler instance
notification_scheduler = NotificationScheduler()

def start_notification_scheduler():
    """Start the global notification scheduler."""
    notification_scheduler.start()

def stop_notification_scheduler():
    """Stop the global notification scheduler."""
    notification_scheduler.stop()

def schedule_lineup_reminder(db: Session, user_id: str, game_time: datetime, 
                           hours_before: int = 2):
    """
    Schedule a lineup reminder for a specific user and game time.
    
    Args:
        db (Session): Database session
        user_id (str): User ID
        game_time (datetime): When the games start
        hours_before (int): How many hours before game time to send reminder
    """
    try:
        notification_service = create_notification_service()
        
        reminder_data = {
            "week": notification_scheduler._get_current_nfl_week(),
            "hours_until_games": hours_before
        }
        
        # Create the notification
        notification_id = notification_service.create_notification(
            db, user_id,
            "⏰ Lineup Reminder",
            f"Don't forget to set your lineup! Games start in {hours_before} hours.",
            "lineup_reminders",
            priority=2,
            data=reminder_data,
            scheduled_at=game_time - timedelta(hours=hours_before)
        )
        
        # Queue it for processing
        preferences = notification_service.get_user_preferences(db, user_id)
        channels = notification_service._get_notification_channels(
            preferences, "lineup_reminders", 2
        )
        
        notification_scheduler.schedule_notification(
            db, notification_id, channels, game_time - timedelta(hours=hours_before)
        )
        
        logger.info(f"Scheduled lineup reminder for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error scheduling lineup reminder: {e}")

def schedule_breaking_news_alert(db: Session, news_data: Dict[str, Any], 
                                affected_user_ids: List[str]):
    """
    Schedule breaking news alerts for affected users.
    
    Args:
        db (Session): Database session
        news_data (dict): Breaking news data
        affected_user_ids (list): List of user IDs to notify
    """
    try:
        notification_service = create_notification_service()
        
        for user_id in affected_user_ids:
            # Send immediately for breaking news
            notification_service.send_breaking_news_notification(
                db, user_id, news_data
            )
        
        logger.info(f"Sent breaking news alerts to {len(affected_user_ids)} users")
        
    except Exception as e:
        logger.error(f"Error sending breaking news alerts: {e}")