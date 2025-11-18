"""
League and team models
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class Platform(str, enum.Enum):
    """Fantasy platform enum"""
    ESPN = "espn"
    SLEEPER = "sleeper"


class League(Base):
    """League model"""
    __tablename__ = "leagues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Platform info
    platform = Column(SQLEnum(Platform), nullable=False)
    external_id = Column(String, nullable=False)  # Platform's league ID

    # League details
    name = Column(String, nullable=False)
    season = Column(Integer, nullable=False)
    scoring_type = Column(String, nullable=True)  # ppr, standard, half_ppr
    team_count = Column(Integer, nullable=True)
    roster_positions = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)

    # Sync metadata
    last_synced = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Team(Base):
    """Team model"""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False, index=True)

    # Team details
    external_id = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)

    # Record
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    points_for = Column(Integer, default=0)
    points_against = Column(Integer, default=0)

    # Roster snapshot
    roster = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Player(Base):
    """Player model"""
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, nullable=True)

    # Player info
    name = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False)  # QB, RB, WR, TE, K, DEF
    team = Column(String, nullable=True)  # NFL team
    status = Column(String, default="active")  # active, injured, out, questionable
    bye_week = Column(Integer, nullable=True)

    # Stats and projections
    stats = Column(JSON, nullable=True)
    projections = Column(JSON, nullable=True)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
