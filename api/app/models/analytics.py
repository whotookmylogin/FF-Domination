"""
Analytics and AI query models
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class AIQuery(Base):
    """AI Query tracking for billing and analytics"""
    __tablename__ = "ai_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Query details
    query_type = Column(String, nullable=False)  # trade, draft, waiver, lineup
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)

    # Usage tracking
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(10, 6), default=0.0)
    model = Column(String, nullable=True)  # gpt-4, claude-3.5, etc

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    execution_time_ms = Column(Integer, nullable=True)


class Trade(Base):
    """Trade analysis and proposals"""
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False, index=True)

    # Teams involved
    team_from_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    team_to_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)

    # Players
    players_offered = Column(JSON, nullable=False)  # Array of player IDs
    players_requested = Column(JSON, nullable=False)

    # AI Analysis
    ai_score = Column(Numeric(5, 2), nullable=True)  # 0-100 value score
    ai_reasoning = Column(String, nullable=True)
    confidence = Column(Numeric(3, 2), nullable=True)  # 0-1

    # Status
    status = Column(String, default="proposed")  # proposed, accepted, rejected, countered

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NewsItem(Base):
    """News and breaking updates"""
    __tablename__ = "news_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # News content
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    source = Column(String, nullable=False)  # espn, fantasypros, nfl
    url = Column(String, nullable=True)

    # Analysis
    player_ids = Column(JSON, nullable=True)  # Affected players
    urgency = Column(Integer, default=1)  # 1-5 scale
    category = Column(String, nullable=True)  # injury, trade, signing

    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SubscriptionUsage(Base):
    """Track subscription usage for billing"""
    __tablename__ = "subscription_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Usage metrics
    ai_queries_used = Column(Integer, default=0)
    ai_queries_limit = Column(Integer, nullable=True)
    leagues_connected = Column(Integer, default=0)

    # Overage
    overage_charges = Column(Numeric(10, 2), default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
