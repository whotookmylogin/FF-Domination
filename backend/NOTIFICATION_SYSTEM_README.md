# Fantasy Football Notification System

A comprehensive notification system for the Fantasy Football Domination App that supports multiple notification channels and automated scheduling.

## Overview

The notification system provides:
- **Multi-channel notifications**: Email, Push, SMS, and In-app
- **Template-based messaging**: Pre-built templates for common scenarios
- **User preference management**: Granular control over notification types and channels
- **Automated scheduling**: Background tasks for recurring notifications
- **Queue system**: Reliable delivery with retry logic
- **Mock mode support**: Development testing without real credentials

## Features

### 🔔 Notification Channels

1. **Email Notifications**
   - SMTP support (Gmail, custom servers)
   - HTML and plain text support
   - Mock mode for development

2. **Push Notifications**  
   - Firebase Cloud Messaging (FCM)
   - Cross-platform (iOS/Android)
   - Custom data payloads

3. **SMS Notifications**
   - Twilio integration
   - Urgent notifications only (configurable)
   - International number support

4. **In-App Notifications**
   - Database-stored notifications
   - Read/unread status tracking
   - Rich data attachments

### 📧 Notification Templates

Pre-built templates for common fantasy football scenarios:

1. **Trade Proposals** 🔄
   - Player exchange details
   - Fairness scoring
   - Win probability impact

2. **Waiver Wire Results** 📋
   - Successful/failed claims
   - Bid amounts
   - Player details

3. **Breaking News Alerts** 🚨
   - Urgency-based formatting
   - Affected player lists
   - Source attribution

4. **Weekly Lineup Reminders** ⏰
   - Game time countdowns
   - Lineup optimization tips
   - Injury/bye week alerts

5. **Injury Updates** 🏥
   - Player status changes
   - Fantasy impact assessment
   - Timeline estimates

### ⚙️ User Preferences

Granular notification controls:
- Enable/disable per channel
- Customize per notification type
- Set quiet hours
- Configure SMS phone numbers
- Adjust lineup reminder timing

### 🕐 Automated Scheduling

Background scheduler handles:
- **Lineup Reminders**: Sunday mornings before games
- **Waiver Results**: Wednesday morning processing
- **Breaking News Monitoring**: Every 15 minutes
- **Weekly Summaries**: Tuesday morning recaps
- **Notification Queue Processing**: Every minute

## Database Schema

### Notifications Table
```sql
CREATE TABLE notifications (
    id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    title STRING NOT NULL,
    message TEXT NOT NULL,
    notification_type STRING NOT NULL,
    priority INTEGER DEFAULT 1,
    read BOOLEAN DEFAULT FALSE,
    sent_via_email BOOLEAN DEFAULT FALSE,
    sent_via_push BOOLEAN DEFAULT FALSE,
    sent_via_sms BOOLEAN DEFAULT FALSE,
    data JSON,
    scheduled_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### Notification Preferences Table
```sql
CREATE TABLE notification_preferences (
    id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE,
    email_trade_proposals BOOLEAN DEFAULT TRUE,
    email_waiver_results BOOLEAN DEFAULT TRUE,
    email_breaking_news BOOLEAN DEFAULT TRUE,
    email_lineup_reminders BOOLEAN DEFAULT TRUE,
    email_injury_updates BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    push_trade_proposals BOOLEAN DEFAULT TRUE,
    push_waiver_results BOOLEAN DEFAULT TRUE,
    push_breaking_news BOOLEAN DEFAULT TRUE,
    push_lineup_reminders BOOLEAN DEFAULT TRUE,
    push_injury_updates BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    sms_phone_number STRING,
    sms_urgent_only BOOLEAN DEFAULT TRUE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    lineup_reminder_time INTEGER DEFAULT 2,
    quiet_hours_start INTEGER DEFAULT 22,
    quiet_hours_end INTEGER DEFAULT 8,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### Notification Queue Table
```sql
CREATE TABLE notification_queue (
    id STRING PRIMARY KEY,
    notification_id STRING NOT NULL,
    channel STRING NOT NULL,
    status STRING DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    scheduled_at DATETIME NOT NULL,
    processed_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

## API Endpoints

### Core Notification Endpoints

#### Send Notification
```http
POST /notifications/send
{
    "user_id": "user123",
    "title": "Test Notification",
    "message": "This is a test message",
    "type": "test",
    "priority": 1,
    "data": {},
    "channels": ["email", "push", "sms"]
}
```

#### Get User Notifications
```http
GET /notifications/user/{user_id}?unread_only=false&limit=50
```

#### Mark Notifications as Read
```http
POST /notifications/mark-read
{
    "user_id": "user123",
    "notification_ids": ["notif1", "notif2"]
}
```

### Preference Management

#### Get Notification Preferences
```http
GET /notifications/preferences/{user_id}
```

#### Update Notification Preferences
```http
PUT /notifications/preferences/{user_id}
{
    "email_enabled": true,
    "push_enabled": true,
    "sms_enabled": false,
    "sms_phone_number": "+1234567890"
}
```

### Template-Based Notifications

#### Trade Proposal Notification
```http
POST /notifications/trade-proposal
{
    "user_id": "user123",
    "trade_data": {
        "you_give": ["Player A", "Player B"],
        "you_get": ["Player C"],
        "fairness_score": 85,
        "win_probability_delta": 12.5
    }
}
```

#### Waiver Results Notification
```http
POST /notifications/waiver-results
{
    "user_id": "user123",
    "waiver_data": {
        "successful_claims": [
            {"player_name": "Player A", "bid_amount": 25}
        ],
        "failed_claims": [
            {"player_name": "Player B", "winning_bid": 50}
        ]
    }
}
```

#### Breaking News Alert
```http
POST /notifications/breaking-news
{
    "user_id": "user123",
    "news_data": {
        "headline": "Player X suffers injury",
        "summary": "Details about the injury...",
        "urgency_score": 5,
        "affected_players": ["Player X"],
        "source": "ESPN"
    }
}
```

#### Lineup Reminder
```http
POST /notifications/lineup-reminder
{
    "user_id": "user123",
    "reminder_data": {
        "week": 8,
        "hours_until_games": 2
    }
}
```

#### Injury Update
```http
POST /notifications/injury-update
{
    "user_id": "user123",
    "injury_data": {
        "player_name": "Player X",
        "status": "out",
        "injury_type": "ACL tear",
        "expected_return": "Next season",
        "fantasy_impact": "Drop immediately"
    }
}
```

### Scheduler Management

#### Start/Stop Scheduler
```http
POST /notifications/scheduler/start
POST /notifications/scheduler/stop
GET /notifications/scheduler/status
```

#### Schedule Lineup Reminder
```http
POST /notifications/schedule/lineup-reminder
{
    "user_id": "user123",
    "game_time": "2024-01-07T13:00:00Z",
    "hours_before": 2
}
```

#### Send Breaking News Alert
```http
POST /notifications/schedule/breaking-news
{
    "news_data": {
        "headline": "Player X suffers injury",
        "urgency_score": 5
    },
    "affected_user_ids": ["user1", "user2"]
}
```

### Testing Endpoint

#### Test All Notification Channels
```http
POST /notifications/test/{user_id}
```

## Configuration

### Environment Variables

```bash
# Email Configuration (SMTP)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Push Notifications (Firebase)
FCM_SERVER_KEY=your-fcm-server-key

# SMS Notifications (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### Development Setup

For development without external service credentials:

1. **Mock Mode**: All services run in mock mode when credentials are not provided
2. **Database Only**: Notifications are still stored in database
3. **Template Testing**: All templates can be tested without external dependencies

## Usage Examples

### Python Service Usage

```python
from src.notifications.service import create_notification_service
from src.database.connection import get_db

# Initialize service
notification_service = create_notification_service()

# Send a basic notification
with next(get_db()) as db:
    result = notification_service.send_notification(
        db, 
        user_id="user123",
        title="Welcome!",
        message="Welcome to Fantasy Football Domination!",
        notification_type="welcome",
        priority=1
    )

# Send trade proposal notification
trade_data = {
    "you_give": ["Christian McCaffrey"],
    "you_get": ["Derrick Henry", "Calvin Ridley"],
    "fairness_score": 88,
    "win_probability_delta": 15.2
}

result = notification_service.send_trade_proposal_notification(
    db, "user123", trade_data
)
```

### Scheduler Usage

```python
from src.notifications.scheduler import start_notification_scheduler, schedule_lineup_reminder
from datetime import datetime, timedelta

# Start the background scheduler
start_notification_scheduler()

# Schedule a specific lineup reminder
with next(get_db()) as db:
    game_time = datetime.now() + timedelta(hours=4)
    schedule_lineup_reminder(db, "user123", game_time, hours_before=2)
```

## Testing

### Template Tests
```bash
cd /Users/joethomas/Documents/dev/FantasyFootball/.conductor/ff_app/backend
python3 test_templates_only.py
```

### Full System Tests (requires dependencies)
```bash
cd /Users/joethomas/Documents/dev/FantasyFootball/.conductor/ff_app/backend
python3 test_notification_system.py
```

## Architecture

### Service Layer Architecture

```
NotificationService
├── EmailService (SMTP)
├── SMSService (Twilio)
├── PushNotificationService (FCM)
├── NotificationTemplates
└── Database Integration

NotificationScheduler
├── Background Task Processing
├── Automated Scheduling
├── Queue Management
└── Retry Logic
```

### Data Flow

1. **Notification Creation**: API endpoint or service call creates notification
2. **Preference Check**: User preferences determine delivery channels
3. **Queue Processing**: Notifications queued for background processing
4. **Channel Delivery**: Each channel processes notifications independently
5. **Status Tracking**: Delivery status updated in database
6. **Retry Logic**: Failed notifications retried up to max attempts

## Production Considerations

### Security
- Store API keys securely in environment variables
- Validate all user inputs
- Rate limit notification endpoints
- Encrypt sensitive data in database

### Performance
- Use background workers for notification processing
- Implement proper database indexing
- Cache user preferences
- Batch process notifications where possible

### Monitoring
- Track notification delivery rates
- Monitor queue processing times
- Log failed notifications for analysis
- Set up alerts for system failures

### Scalability
- Consider message queues (Redis, RabbitMQ) for high volume
- Implement horizontal scaling for background workers
- Use CDN for push notification assets
- Database sharding for large user bases

## Maintenance

### Regular Tasks
- Clean up old notifications (retention policy)
- Monitor and rotate API keys
- Update notification templates
- Review user preference analytics

### Troubleshooting
- Check service credentials and configuration
- Verify database connectivity
- Review queue processing logs
- Test notification channels individually

## Future Enhancements

### Planned Features
- **Rich Push Notifications**: Images, actions, deep links
- **Email Templates**: HTML email templates with branding
- **Analytics Dashboard**: Notification delivery metrics
- **A/B Testing**: Template performance testing
- **Internationalization**: Multi-language support
- **Smart Scheduling**: ML-based optimal send times
- **Integration Webhooks**: Third-party service notifications

### API Extensions
- **Bulk Operations**: Send notifications to multiple users
- **Template Management**: Dynamic template creation/editing
- **Advanced Filtering**: Complex user targeting rules
- **Notification History**: Detailed delivery logs and analytics

---

## Summary

The Fantasy Football Notification System is a production-ready, multi-channel notification platform that provides:

✅ **Complete Implementation**: All notification channels implemented with mock mode support
✅ **Rich Templates**: Fantasy football-specific notification templates  
✅ **User Preferences**: Granular control over notification types and channels
✅ **Automated Scheduling**: Background tasks for recurring notifications
✅ **Database Integration**: Full persistence layer with queue management
✅ **API Endpoints**: Comprehensive REST API for all functionality
✅ **Testing Framework**: Validation of core functionality
✅ **Production Ready**: Proper error handling, retry logic, and configuration

The system is ready for development testing and can be easily configured for production use with real service credentials.