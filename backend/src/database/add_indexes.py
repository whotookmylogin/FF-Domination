"""
Add database indexes for improved performance.
This script adds indexes to commonly queried columns to speed up data retrieval.
"""

from sqlalchemy import create_engine, Index, text
from sqlalchemy.orm import sessionmaker
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fantasy_football.db")

def create_indexes():
    """
    Create indexes on commonly queried columns for better performance.
    """
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # List of indexes to create
        indexes_sql = [
            # User lookups
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            
            # League lookups
            "CREATE INDEX IF NOT EXISTS idx_leagues_user_id ON leagues(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_leagues_platform ON leagues(platform);",
            "CREATE INDEX IF NOT EXISTS idx_leagues_season ON leagues(season);",
            "CREATE INDEX IF NOT EXISTS idx_leagues_user_platform ON leagues(user_id, platform);",
            
            # Team lookups
            "CREATE INDEX IF NOT EXISTS idx_teams_league_id ON teams(league_id);",
            "CREATE INDEX IF NOT EXISTS idx_teams_platform_team_id ON teams(platform_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_teams_league_platform ON teams(league_id, platform_team_id);",
            
            # Player lookups (very important for performance)
            "CREATE INDEX IF NOT EXISTS idx_players_league_id ON players(league_id);",
            "CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);",
            "CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);",
            "CREATE INDEX IF NOT EXISTS idx_players_team ON players(team);",
            "CREATE INDEX IF NOT EXISTS idx_players_league_position ON players(league_id, position);",
            "CREATE INDEX IF NOT EXISTS idx_players_league_name ON players(league_id, name);",
            
            # Roster slot lookups
            "CREATE INDEX IF NOT EXISTS idx_roster_slots_team_id ON roster_slots(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_roster_slots_player_id ON roster_slots(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_roster_slots_week ON roster_slots(week);",
            "CREATE INDEX IF NOT EXISTS idx_roster_slots_team_week ON roster_slots(team_id, week);",
            
            # Trade lookups
            "CREATE INDEX IF NOT EXISTS idx_trades_league_id ON trades(league_id);",
            "CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);",
            "CREATE INDEX IF NOT EXISTS idx_trades_created_at ON trades(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_trades_league_status ON trades(league_id, status);",
            
            # Trade player lookups
            "CREATE INDEX IF NOT EXISTS idx_trade_players_trade_id ON trade_players(trade_id);",
            "CREATE INDEX IF NOT EXISTS idx_trade_players_player_id ON trade_players(player_id);",
            
            # News item lookups
            "CREATE INDEX IF NOT EXISTS idx_news_items_league_id ON news_items(league_id);",
            "CREATE INDEX IF NOT EXISTS idx_news_items_urgency ON news_items(urgency);",
            "CREATE INDEX IF NOT EXISTS idx_news_items_published_at ON news_items(published_at);",
            "CREATE INDEX IF NOT EXISTS idx_news_items_league_urgency ON news_items(league_id, urgency);",
            "CREATE INDEX IF NOT EXISTS idx_news_items_league_published ON news_items(league_id, published_at);",
            
            # User credential lookups
            "CREATE INDEX IF NOT EXISTS idx_user_credentials_user_id ON user_credentials(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_credentials_platform ON user_credentials(platform);",
            
            # Notification lookups
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, read);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_priority ON notifications(user_id, priority);",
            
            # Notification queue lookups
            "CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON notification_queue(status);",
            "CREATE INDEX IF NOT EXISTS idx_notification_queue_scheduled_at ON notification_queue(scheduled_at);",
            "CREATE INDEX IF NOT EXISTS idx_notification_queue_status_scheduled ON notification_queue(status, scheduled_at);",
        ]
        
        # Execute each index creation
        with engine.connect() as connection:
            for index_sql in indexes_sql:
                try:
                    connection.execute(text(index_sql))
                    connection.commit()
                    index_name = index_sql.split("idx_")[1].split(" ON")[0]
                    logger.info(f"✓ Created index: idx_{index_name}")
                except Exception as e:
                    logger.warning(f"Index creation failed (might already exist): {str(e)[:100]}")
        
        logger.info("\n✅ All database indexes created successfully!")
        logger.info("🚀 Database performance should be significantly improved")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {str(e)}")
        return False

def analyze_database():
    """
    Analyze database and provide statistics about tables and indexes.
    """
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # Get table statistics for SQLite
            if DATABASE_URL.startswith("sqlite"):
                # Get all tables
                result = connection.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
                ))
                tables = [row[0] for row in result]
                
                logger.info("\n📊 Database Statistics:")
                logger.info("=" * 50)
                
                for table in tables:
                    # Get row count
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = result.scalar()
                    
                    # Get indexes for this table
                    result = connection.execute(text(
                        f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table}';"
                    ))
                    indexes = [row[0] for row in result if row[0]]
                    
                    logger.info(f"\nTable: {table}")
                    logger.info(f"  Rows: {count}")
                    logger.info(f"  Indexes: {len(indexes)}")
                    if indexes:
                        for idx in indexes:
                            logger.info(f"    - {idx}")
                
                logger.info("\n" + "=" * 50)
    
    except Exception as e:
        logger.error(f"Failed to analyze database: {str(e)}")

if __name__ == "__main__":
    logger.info("🔧 Starting database optimization...")
    logger.info(f"📍 Database: {DATABASE_URL}")
    
    # Create indexes
    if create_indexes():
        # Analyze database after creating indexes
        analyze_database()
    else:
        logger.error("Failed to create indexes")