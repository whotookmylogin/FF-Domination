"""Initial database schema for Fantasy Football App

Revision ID: 001
Revises: 
Create Date: 2024-12-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema with all Fantasy Football models."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create leagues table
    op.create_table(
        'leagues',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('league_name', sa.String(), nullable=False),
        sa.Column('league_id', sa.String(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('current_week', sa.Integer(), nullable=False),
        sa.Column('total_teams', sa.Integer(), nullable=False),
        sa.Column('scoring_settings', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('league_id', sa.String(), nullable=False),
        sa.Column('platform_team_id', sa.String(), nullable=False),
        sa.Column('team_name', sa.String(), nullable=False),
        sa.Column('owner', sa.String(), nullable=False),
        sa.Column('wins', sa.Integer(), nullable=True, default=0),
        sa.Column('losses', sa.Integer(), nullable=True, default=0),
        sa.Column('ties', sa.Integer(), nullable=True, default=0),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('faab_budget', sa.Float(), nullable=True, default=100.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create players table
    op.create_table(
        'players',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('league_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('position', sa.String(), nullable=False),
        sa.Column('team', sa.String(), nullable=False),
        sa.Column('projected_points', sa.Float(), nullable=True, default=0.0),
        sa.Column('injury_status', sa.Integer(), nullable=True, default=0),
        sa.Column('news_urgency', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create roster_slots table
    op.create_table(
        'roster_slots',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('slot_type', sa.String(), nullable=False),
        sa.Column('position', sa.String(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create trades table
    op.create_table(
        'trades',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('league_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('ai_recommendation', sa.String(), nullable=True),
        sa.Column('ai_confidence', sa.String(), nullable=True),
        sa.Column('fairness_score', sa.Float(), nullable=True),
        sa.Column('win_probability_delta', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create trade_players table
    op.create_table(
        'trade_players',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('trade_id', sa.String(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('direction', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create news_items table
    op.create_table(
        'news_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('league_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('urgency', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create missing UserCredential table for credential storage
    op.create_table(
        'user_credentials',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('credential_type', sa.String(), nullable=False),
        sa.Column('encrypted_value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'platform', 'credential_type', name='unique_user_platform_credential')
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_table('user_credentials')
    op.drop_table('news_items')
    op.drop_table('trade_players')
    op.drop_table('trades')
    op.drop_table('roster_slots')
    op.drop_table('players')
    op.drop_table('teams')
    op.drop_table('leagues')
    op.drop_table('users')