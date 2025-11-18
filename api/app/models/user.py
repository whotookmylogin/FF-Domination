"""
User and authentication models
"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enum"""
    FREE = "free"
    PRO = "pro"
    CHAMPION = "champion"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    stripe_customer_id = Column(String, unique=True, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # OAuth
    oauth_provider = Column(String, nullable=True)
    oauth_provider_id = Column(String, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)


class ApiKey(Base):
    """API Key model for user's OpenAI keys (BYOK)"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Encrypted API key
    encrypted_key = Column(String, nullable=False)
    key_type = Column(String, nullable=False)  # openai, openrouter
    key_name = Column(String, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
