from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
import logging

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fantasy_football.db")

# SQLite specific configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite engine with proper configuration for concurrent access
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 20,  # 20 second timeout for locked database
        },
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )
else:
    # Configuration for other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Setup logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def get_db() -> Session:
    """
    Dependency to get a database session.
    
    Returns:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database():
    """
    Create all database tables.
    This function imports all models and creates the database schema.
    """
    try:
        # Import models to register them with Base
        from . import models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to create database tables: {str(e)}")
        return False

def check_database_connection():
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        # Test the connection
        db.execute("SELECT 1")
        db.close()
        logging.info("Database connection successful")
        return True
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        return False
