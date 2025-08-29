from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """
    User model representing a fantasy football manager.
    """
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    leagues = relationship("League", back_populates="user")
    credentials = relationship("UserCredential", back_populates="user")

class League(Base):
    """
    League model representing a fantasy football league.
    """
    __tablename__ = 'leagues'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    platform = Column(String, nullable=False)  # ESPN or Sleeper
    league_name = Column(String, nullable=False)
    league_id = Column(String, nullable=False)  # ID from the platform
    season = Column(Integer, nullable=False)
    current_week = Column(Integer, nullable=False)
    total_teams = Column(Integer, nullable=False)
    scoring_settings = Column(String, nullable=True)  # JSON string of custom scoring rules
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="leagues")
    teams = relationship("Team", back_populates="league")
    players = relationship("Player", back_populates="league")
    trades = relationship("Trade", back_populates="league")
    news = relationship("NewsItem", back_populates="league")

class Team(Base):
    """
    Team model representing a user's fantasy team in a league.
    """
    __tablename__ = 'teams'
    
    id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.id'), nullable=False)
    platform_team_id = Column(String, nullable=False)  # ID from the platform
    team_name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    rank = Column(Integer, nullable=False)
    faab_budget = Column(Float, default=100.0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    league = relationship("League", back_populates="teams")
    roster = relationship("RosterSlot", back_populates="team")

class Player(Base):
    """
    Player model representing an NFL player.
    """
    __tablename__ = 'players'
    
    id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.id'), nullable=False)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    team = Column(String, nullable=False)  # NFL team abbreviation
    projected_points = Column(Float, default=0.0)
    injury_status = Column(Integer, default=0)  # 0=Healthy, 1=Questionable, 2=Doubtful, 3=Out
    news_urgency = Column(Integer, default=0)  # 1-5 scale
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    league = relationship("League", back_populates="players")
    roster_slots = relationship("RosterSlot", back_populates="player")

class RosterSlot(Base):
    """
    RosterSlot model representing a player's position on a team roster.
    """
    __tablename__ = 'roster_slots'
    
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey('teams.id'), nullable=False)
    player_id = Column(String, ForeignKey('players.id'), nullable=False)
    slot_type = Column(String, nullable=False)  # STARTER, BENCH, etc.
    position = Column(String, nullable=False)  # Position this player is slotted at
    week = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="roster")
    player = relationship("Player", back_populates="roster_slots")

class Trade(Base):
    """
    Trade model representing a trade proposal or completed trade.
    """
    __tablename__ = 'trades'
    
    id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.id'), nullable=False)
    status = Column(String, nullable=False)  # PENDING, ACCEPTED, DECLINED, EXPIRED
    ai_recommendation = Column(String, nullable=True)  # ACCEPT, DECLINE, PASS
    ai_confidence = Column(String, nullable=True)  # HIGH, MEDIUM, LOW
    fairness_score = Column(Float, nullable=True)
    win_probability_delta = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    league = relationship("League", back_populates="trades")
    trade_players = relationship("TradePlayer", back_populates="trade")

class TradePlayer(Base):
    """
    TradePlayer model representing a player involved in a trade.
    """
    __tablename__ = 'trade_players'
    
    id = Column(String, primary_key=True)
    trade_id = Column(String, ForeignKey('trades.id'), nullable=False)
    player_id = Column(String, ForeignKey('players.id'), nullable=False)
    team_id = Column(String, nullable=False)  # Team that owns this player in the trade
    direction = Column(String, nullable=False)  # ACQUIRE or OFFER
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    trade = relationship("Trade", back_populates="trade_players")
    player = relationship("Player")

class NewsItem(Base):
    """
    NewsItem model representing a news article affecting fantasy football.
    """
    __tablename__ = 'news_items'
    
    id = Column(String, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.id'), nullable=False)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    urgency = Column(Integer, nullable=False)  # 1-5 scale
    summary = Column(Text, nullable=False)
    link = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    league = relationship("League", back_populates="news")
