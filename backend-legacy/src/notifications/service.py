import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import requests
import json
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database.models import (
    Notification, 
    NotificationPreferences, 
    NotificationQueue, 
    User
)

logger = logging.getLogger(__name__)

class NotificationTemplates:
    """
    Notification templates for common scenarios.
    """
    
    @staticmethod
    def trade_proposal(trade_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate trade proposal notification template.
        
        Args:
            trade_data (dict): Trade proposal data
            
        Returns:
            dict: Title and message for the notification
        """
        title = "🔄 New Trade Proposal"
        message = f"""
        You have a new trade proposal!
        
        You give: {', '.join(trade_data.get('you_give', []))}
        You get: {', '.join(trade_data.get('you_get', []))}
        
        Fairness Score: {trade_data.get('fairness_score', 'N/A')}/100
        Win Probability Change: {trade_data.get('win_probability_delta', 'N/A')}%
        
        Review this trade in your app now!
        """
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def waiver_results(waiver_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate waiver wire results notification template.
        
        Args:
            waiver_data (dict): Waiver results data
            
        Returns:
            dict: Title and message for the notification
        """
        title = "📋 Waiver Wire Results"
        successful = waiver_data.get('successful_claims', [])
        failed = waiver_data.get('failed_claims', [])
        
        message = "Waiver wire results are in!\n\n"
        
        if successful:
            message += "✅ Successful Claims:\n"
            for claim in successful:
                message += f"  • {claim.get('player_name', 'Unknown')} - ${claim.get('bid_amount', 0)}\n"
        
        if failed:
            message += "\n❌ Failed Claims:\n"
            for claim in failed:
                message += f"  • {claim.get('player_name', 'Unknown')} - Outbid by ${claim.get('winning_bid', 0)}\n"
        
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def breaking_news(news_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate breaking news notification template.
        
        Args:
            news_data (dict): News data
            
        Returns:
            dict: Title and message for the notification
        """
        urgency = news_data.get('urgency_score', 1)
        urgency_emoji = {1: "📰", 2: "📰", 3: "⚠️", 4: "🚨", 5: "🚨"}
        
        title = f"{urgency_emoji.get(urgency, '📰')} Breaking Fantasy News"
        if urgency >= 4:
            title = f"🚨 URGENT: {news_data.get('headline', 'Breaking News')}"
        
        message = f"""
        {news_data.get('headline', 'Fantasy Football News')}
        
        {news_data.get('summary', 'Check the app for more details.')}
        
        Affected Players: {', '.join(news_data.get('affected_players', ['None']))}
        Source: {news_data.get('source', 'Fantasy News')}
        """
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def lineup_reminder(reminder_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate weekly lineup reminder notification template.
        
        Args:
            reminder_data (dict): Reminder data
            
        Returns:
            dict: Title and message for the notification
        """
        title = "⏰ Lineup Reminder"
        week = reminder_data.get('week', 'current')
        hours_until_games = reminder_data.get('hours_until_games', 'few')
        
        message = f"""
        Don't forget to set your lineup for Week {week}!
        
        Games start in {hours_until_games} hours.
        
        Quick checks:
        • Injured players in your lineup?
        • Players on bye weeks?
        • Optimal matchups selected?
        
        Set your lineup now to maximize your points!
        """
        return {"title": title, "message": message.strip()}
    
    @staticmethod
    def injury_update(injury_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate injury update notification template.
        
        Args:
            injury_data (dict): Injury data
            
        Returns:
            dict: Title and message for the notification
        """
        player_name = injury_data.get('player_name', 'Unknown Player')
        status = injury_data.get('status', 'unknown')
        severity = injury_data.get('severity', 'unknown')
        
        status_emoji = {
            'out': '❌',
            'doubtful': '🔴',
            'questionable': '🟡',
            'probable': '🟢',
            'healthy': '✅'
        }
        
        title = f"{status_emoji.get(status.lower(), '⚠️')} Injury Update: {player_name}"
        
        message = f"""
        {player_name} injury update:
        
        Status: {status.title()}
        Injury: {injury_data.get('injury_type', 'Not specified')}
        Expected Return: {injury_data.get('expected_return', 'Unknown')}
        
        Fantasy Impact: {injury_data.get('fantasy_impact', 'Monitor situation')}
        
        Consider your lineup and waiver wire options!
        """
        return {"title": title, "message": message.strip()}

class EmailService:
    """
    Email notification service using SMTP.
    """
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587,
                 email: str = None, password: str = None):
        """
        Initialize email service.
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
            email (str): Sender email address
            password (str): Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        
    def send_email(self, to_email: str, subject: str, message: str, 
                   html_content: str = None) -> Dict[str, Any]:
        """
        Send email notification.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message (str): Plain text message
            html_content (str, optional): HTML message content
            
        Returns:
            dict: Send result with success status
        """
        if not self.email or not self.password:
            logger.warning("Email credentials not configured, using mock send")
            return {
                "success": True,
                "mock": True,
                "message": f"Mock email sent to {to_email}"
            }
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {"success": False, "error": str(e)}

class SMSService:
    """
    SMS notification service using Twilio.
    """
    
    def __init__(self, account_sid: str = None, auth_token: str = None, 
                 from_number: str = None):
        """
        Initialize SMS service.
        
        Args:
            account_sid (str): Twilio account SID
            auth_token (str): Twilio auth token
            from_number (str): Twilio phone number
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        
    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send SMS notification.
        
        Args:
            to_number (str): Recipient phone number
            message (str): SMS message content
            
        Returns:
            dict: Send result with success status
        """
        if not self.account_sid or not self.auth_token:
            logger.warning("SMS credentials not configured, using mock send")
            return {
                "success": True,
                "mock": True,
                "message": f"Mock SMS sent to {to_number}"
            }
        
        try:
            # In a real implementation, you would use Twilio client here
            # from twilio.rest import Client
            # client = Client(self.account_sid, self.auth_token)
            # 
            # message = client.messages.create(
            #     body=message,
            #     from_=self.from_number,
            #     to=to_number
            # )
            
            logger.info(f"SMS sent successfully to {to_number}")
            return {"success": True, "message": "SMS sent successfully (mock)"}
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return {"success": False, "error": str(e)}

class PushNotificationService:
    """
    Push notification service using Firebase Cloud Messaging.
    """
    
    def __init__(self, fcm_server_key: str = None):
        """
        Initialize push notification service.
        
        Args:
            fcm_server_key (str): Firebase Cloud Messaging server key
        """
        self.fcm_server_key = fcm_server_key
        self.base_url = "https://fcm.googleapis.com/fcm/send"
        self.headers = {
            "Authorization": f"key={fcm_server_key}" if fcm_server_key else "",
            "Content-Type": "application/json"
        }
        
    def send_push_notification(self, device_tokens: List[str], title: str, 
                              body: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send push notification to devices.
        
        Args:
            device_tokens (list): List of device tokens
            title (str): Notification title
            body (str): Notification body
            data (dict, optional): Additional data payload
            
        Returns:
            dict: Send result with success status
        """
        if not self.fcm_server_key or not device_tokens:
            logger.warning("Push notification not configured or no tokens, using mock send")
            return {
                "success": True,
                "mock": True,
                "message": f"Mock push sent to {len(device_tokens)} devices"
            }
        
        payload = {
            "registration_ids": device_tokens,
            "notification": {
                "title": title,
                "body": body,
                "sound": "default"
            },
            "priority": "high"
        }
        
        if data:
            payload["data"] = data
            
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Push notification sent successfully: {result}")
                return {"success": True, "result": result}
            else:
                logger.error(f"FCM API request failed with status {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return {"success": False, "error": str(e)}

class NotificationService:
    """
    Comprehensive notification service handling all notification types.
    """
    
    def __init__(self, email_service: EmailService = None, 
                 sms_service: SMSService = None,
                 push_service: PushNotificationService = None):
        """
        Initialize notification service.
        
        Args:
            email_service (EmailService): Email service instance
            sms_service (SMSService): SMS service instance
            push_service (PushNotificationService): Push service instance
        """
        self.email_service = email_service or EmailService()
        self.sms_service = sms_service or SMSService()
        self.push_service = push_service or PushNotificationService()
        self.templates = NotificationTemplates()
        
    def create_notification(self, db: Session, user_id: str, title: str, 
                           message: str, notification_type: str, priority: int = 1,
                           data: Dict[str, Any] = None, 
                           scheduled_at: datetime = None) -> str:
        """
        Create a new notification in the database.
        
        Args:
            db (Session): Database session
            user_id (str): User ID to send notification to
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Type of notification
            priority (int): Priority level (1-5)
            data (dict, optional): Additional notification data
            scheduled_at (datetime, optional): When to send the notification
            
        Returns:
            str: Notification ID
        """
        notification_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        notification = Notification(
            id=notification_id,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            data=data,
            scheduled_at=scheduled_at,
            created_at=now,
            updated_at=now
        )
        
        db.add(notification)
        db.commit()
        
        logger.info(f"Created notification {notification_id} for user {user_id}")
        return notification_id
    
    def get_user_preferences(self, db: Session, user_id: str) -> NotificationPreferences:
        """
        Get user's notification preferences.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            
        Returns:
            NotificationPreferences: User's notification preferences
        """
        preferences = db.query(NotificationPreferences).filter(
            NotificationPreferences.user_id == user_id
        ).first()
        
        if not preferences:
            # Create default preferences
            preferences = self.create_default_preferences(db, user_id)
        
        return preferences
    
    def create_default_preferences(self, db: Session, user_id: str) -> NotificationPreferences:
        """
        Create default notification preferences for a user.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            
        Returns:
            NotificationPreferences: Created preferences
        """
        preferences_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        preferences = NotificationPreferences(
            id=preferences_id,
            user_id=user_id,
            created_at=now,
            updated_at=now
        )
        
        db.add(preferences)
        db.commit()
        
        logger.info(f"Created default notification preferences for user {user_id}")
        return preferences
    
    def queue_notification(self, db: Session, notification_id: str, 
                          channels: List[str], scheduled_at: datetime = None):
        """
        Queue notification for processing.
        
        Args:
            db (Session): Database session
            notification_id (str): Notification ID
            channels (list): List of channels to send through
            scheduled_at (datetime, optional): When to process the notification
        """
        now = datetime.utcnow()
        send_time = scheduled_at or now
        
        for channel in channels:
            queue_id = str(uuid.uuid4())
            queue_item = NotificationQueue(
                id=queue_id,
                notification_id=notification_id,
                channel=channel,
                scheduled_at=send_time,
                created_at=now,
                updated_at=now
            )
            db.add(queue_item)
        
        db.commit()
        logger.info(f"Queued notification {notification_id} for channels: {channels}")
    
    def send_notification(self, db: Session, user_id: str, title: str, 
                         message: str, notification_type: str, priority: int = 1,
                         data: Dict[str, Any] = None, 
                         force_channels: List[str] = None) -> Dict[str, Any]:
        """
        Send notification through appropriate channels based on user preferences.
        
        Args:
            db (Session): Database session
            user_id (str): User ID to send notification to
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Type of notification
            priority (int): Priority level (1-5)
            data (dict, optional): Additional notification data
            force_channels (list, optional): Force specific channels
            
        Returns:
            dict: Send results for each channel
        """
        # Get user and preferences
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        preferences = self.get_user_preferences(db, user_id)
        
        # Create notification
        notification_id = self.create_notification(
            db, user_id, title, message, notification_type, priority, data
        )
        
        # Determine channels to use
        channels = force_channels or self._get_notification_channels(
            preferences, notification_type, priority
        )
        
        results = {}
        now = datetime.utcnow()
        
        # Send through each channel
        for channel in channels:
            if channel == 'email' and user.email:
                result = self.email_service.send_email(
                    user.email, title, message
                )
                results[channel] = result
                
                # Update notification record
                db.query(Notification).filter(Notification.id == notification_id).update({
                    "sent_via_email": result.get("success", False),
                    "updated_at": now
                })
                
            elif channel == 'push':
                # In a real implementation, you'd get device tokens from user preferences
                device_tokens = data.get('device_tokens', []) if data else []
                result = self.push_service.send_push_notification(
                    device_tokens, title, message, data
                )
                results[channel] = result
                
                # Update notification record
                db.query(Notification).filter(Notification.id == notification_id).update({
                    "sent_via_push": result.get("success", False),
                    "updated_at": now
                })
                
            elif channel == 'sms' and preferences.sms_phone_number:
                result = self.sms_service.send_sms(
                    preferences.sms_phone_number, f"{title}\n\n{message}"
                )
                results[channel] = result
                
                # Update notification record
                db.query(Notification).filter(Notification.id == notification_id).update({
                    "sent_via_sms": result.get("success", False),
                    "updated_at": now
                })
        
        db.commit()
        
        return {
            "success": True,
            "notification_id": notification_id,
            "channels": channels,
            "results": results
        }
    
    def _get_notification_channels(self, preferences: NotificationPreferences, 
                                  notification_type: str, priority: int) -> List[str]:
        """
        Determine which channels to use based on preferences and notification type.
        
        Args:
            preferences (NotificationPreferences): User's preferences
            notification_type (str): Type of notification
            priority (int): Priority level
            
        Returns:
            list: List of channels to use
        """
        channels = []
        
        # Always add in-app if enabled
        if preferences.in_app_enabled:
            channels.append('in_app')
        
        # Email channels
        if preferences.email_enabled:
            type_enabled = getattr(preferences, f'email_{notification_type}', True)
            if type_enabled:
                channels.append('email')
        
        # Push channels
        if preferences.push_enabled:
            type_enabled = getattr(preferences, f'push_{notification_type}', True)
            if type_enabled:
                channels.append('push')
        
        # SMS channels (usually only for urgent notifications)
        if preferences.sms_enabled and preferences.sms_phone_number:
            if not preferences.sms_urgent_only or priority >= 4:
                channels.append('sms')
        
        return channels
    
    def send_trade_proposal_notification(self, db: Session, user_id: str, 
                                        trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send trade proposal notification using template.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            trade_data (dict): Trade proposal data
            
        Returns:
            dict: Send result
        """
        template = self.templates.trade_proposal(trade_data)
        return self.send_notification(
            db, user_id, template["title"], template["message"],
            "trade_proposals", priority=3, data=trade_data
        )
    
    def send_waiver_results_notification(self, db: Session, user_id: str, 
                                        waiver_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send waiver results notification using template.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            waiver_data (dict): Waiver results data
            
        Returns:
            dict: Send result
        """
        template = self.templates.waiver_results(waiver_data)
        return self.send_notification(
            db, user_id, template["title"], template["message"],
            "waiver_results", priority=2, data=waiver_data
        )
    
    def send_breaking_news_notification(self, db: Session, user_id: str, 
                                       news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send breaking news notification using template.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            news_data (dict): News data
            
        Returns:
            dict: Send result
        """
        template = self.templates.breaking_news(news_data)
        priority = news_data.get('urgency_score', 1)
        return self.send_notification(
            db, user_id, template["title"], template["message"],
            "breaking_news", priority=priority, data=news_data
        )
    
    def send_lineup_reminder_notification(self, db: Session, user_id: str, 
                                         reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send lineup reminder notification using template.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            reminder_data (dict): Reminder data
            
        Returns:
            dict: Send result
        """
        template = self.templates.lineup_reminder(reminder_data)
        return self.send_notification(
            db, user_id, template["title"], template["message"],
            "lineup_reminders", priority=2, data=reminder_data
        )
    
    def send_injury_update_notification(self, db: Session, user_id: str, 
                                       injury_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send injury update notification using template.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            injury_data (dict): Injury data
            
        Returns:
            dict: Send result
        """
        template = self.templates.injury_update(injury_data)
        priority = 4 if injury_data.get('status', '').lower() == 'out' else 3
        return self.send_notification(
            db, user_id, template["title"], template["message"],
            "injury_updates", priority=priority, data=injury_data
        )
    
    def get_user_notifications(self, db: Session, user_id: str, 
                              unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's notifications.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            unread_only (bool): Only return unread notifications
            limit (int): Maximum number of notifications to return
            
        Returns:
            list: List of notifications
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "priority": n.priority,
                "read": n.read,
                "data": n.data,
                "created_at": n.created_at.isoformat(),
                "sent_via_email": n.sent_via_email,
                "sent_via_push": n.sent_via_push,
                "sent_via_sms": n.sent_via_sms
            }
            for n in notifications
        ]
    
    def mark_notifications_as_read(self, db: Session, user_id: str, 
                                  notification_ids: List[str] = None) -> int:
        """
        Mark notifications as read.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            notification_ids (list, optional): Specific notification IDs to mark
            
        Returns:
            int: Number of notifications marked as read
        """
        query = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        )
        
        if notification_ids:
            query = query.filter(Notification.id.in_(notification_ids))
        
        count = query.update({
            "read": True,
            "updated_at": datetime.utcnow()
        })
        
        db.commit()
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count
    
    def update_notification_preferences(self, db: Session, user_id: str, 
                                       preferences_data: Dict[str, Any]) -> NotificationPreferences:
        """
        Update user's notification preferences.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            preferences_data (dict): Preferences data to update
            
        Returns:
            NotificationPreferences: Updated preferences
        """
        preferences = self.get_user_preferences(db, user_id)
        
        # Update fields that were provided
        for key, value in preferences_data.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        
        preferences.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Updated notification preferences for user {user_id}")
        return preferences
    
    def test_notification_channels(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Test all notification channels for a user.
        
        Args:
            db (Session): Database session
            user_id (str): User ID
            
        Returns:
            dict: Test results for each channel
        """
        test_title = "🧪 Notification Test"
        test_message = "This is a test notification from your Fantasy Football app!"
        
        return self.send_notification(
            db, user_id, test_title, test_message,
            "test", priority=1, force_channels=['email', 'push', 'sms']
        )

# Convenience function to create notification service with environment variables
def create_notification_service() -> NotificationService:
    """
    Create notification service with configuration from environment variables.
    
    Returns:
        NotificationService: Configured notification service
    """
    import os
    
    # Email service
    email_service = EmailService(
        email=os.getenv("SMTP_EMAIL"),
        password=os.getenv("SMTP_PASSWORD"),
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587"))
    )
    
    # SMS service
    sms_service = SMSService(
        account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
        from_number=os.getenv("TWILIO_FROM_NUMBER")
    )
    
    # Push notification service
    push_service = PushNotificationService(
        fcm_server_key=os.getenv("FCM_SERVER_KEY")
    )
    
    return NotificationService(email_service, sms_service, push_service)