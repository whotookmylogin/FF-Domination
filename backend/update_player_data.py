#!/usr/bin/env python3
"""
Script to update player data in the database from ESPN API
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import Base, Player, Team, League, RosterSlot
from src.platforms.espn_api_integration import ESPNAPIIntegration

# Database configuration
DATABASE_URL = "sqlite:///fantasy_football.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def update_player_data():
    """Fetch and update all player data from ESPN"""
    session = Session()
    
    try:
        # ESPN configuration
        espn_s2 = os.getenv("ESPN_S2")
        espn_swid = os.getenv("ESPN_SWID")
        year = int(os.getenv("ESPN_SEASON_YEAR", "2025"))
        league_id = "83806"
        
        print(f"Connecting to ESPN league {league_id} for year {year}...")
        espn_service = ESPNAPIIntegration(
            league_id=league_id,
            year=year,
            espn_s2=espn_s2,
            swid=espn_swid
        )
        
        # Check if league exists in database, create if not
        league = session.query(League).filter_by(league_id=league_id).first()
        if not league:
            print(f"Creating league {league_id} in database...")
            league = League(
                id=f"espn_{league_id}",
                user_id="default_user",  # You may want to update this
                platform="ESPN",
                league_name="Fantasy Football League",
                league_id=league_id,
                season=year,
                current_week=1,
                total_teams=12,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(league)
            session.commit()
        
        # Clear existing players for this league
        print("Clearing existing player data...")
        session.query(Player).filter_by(league_id=league.id).delete()
        
        # Fetch all players from all teams
        all_players = {}
        player_count = 0
        
        print("Fetching player data from all teams...")
        for team_id in range(1, 13):
            roster = espn_service.get_roster_data(str(team_id))
            if roster:
                print(f"  Team {team_id}: {len(roster)} players")
                for player_data in roster:
                    player_key = f"{player_data.get('name')}_{player_data.get('team')}"
                    
                    # Skip duplicates
                    if player_key not in all_players:
                        # Map injury status
                        injury_map = {
                            'ACTIVE': 0,
                            'QUESTIONABLE': 1,
                            'DOUBTFUL': 2,
                            'OUT': 3,
                            'IR': 3
                        }
                        injury_status = injury_map.get(
                            player_data.get('injury_status', 'ACTIVE'), 0
                        )
                        
                        # Create player record with unique ID
                        player_id = player_data.get('player_id', f'unknown_{player_count}')
                        player = Player(
                            id=f"espn_{player_id}_{player_count}",
                            league_id=league.id,
                            name=player_data.get('name', 'Unknown'),
                            position=player_data.get('position', 'Unknown'),
                            team=player_data.get('team', 'FA'),
                            projected_points=player_data.get('projected_points', 0.0),
                            injury_status=injury_status,
                            news_urgency=0,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        session.add(player)
                        all_players[player_key] = player
                        player_count += 1
        
        # Fetch free agents
        print("\nFetching free agents...")
        free_agents = espn_service.get_free_agents(size=100)
        if free_agents:
            print(f"  Found {len(free_agents)} free agents")
            for player_data in free_agents:
                player_key = f"{player_data.get('name')}_{player_data.get('team')}"
                
                # Skip duplicates
                if player_key not in all_players:
                    # Map injury status
                    injury_map = {
                        'ACTIVE': 0,
                        'QUESTIONABLE': 1,
                        'DOUBTFUL': 2,
                        'OUT': 3,
                        'IR': 3
                    }
                    injury_status = injury_map.get(
                        player_data.get('injury_status', 'ACTIVE'), 0
                    )
                    
                    # Create player record with unique ID
                    player_id = player_data.get('player_id', f'fa_{player_count}')
                    player = Player(
                        id=f"espn_fa_{player_id}_{player_count}",
                        league_id=league.id,
                        name=player_data.get('name', 'Unknown'),
                        position=player_data.get('position', 'Unknown'),
                        team=player_data.get('team', 'FA'),
                        projected_points=player_data.get('projected_points', 0.0),
                        injury_status=injury_status,
                        news_urgency=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(player)
                    all_players[player_key] = player
                    player_count += 1
        
        # Commit all changes
        session.commit()
        print(f"\n✅ Successfully updated {player_count} players in the database")
        
        # Show sample of data
        sample_players = session.query(Player).limit(10).all()
        print("\nSample of players in database:")
        for p in sample_players:
            injury_status = ['Healthy', 'Questionable', 'Doubtful', 'Out'][p.injury_status]
            print(f"  {p.name}: {p.position} - {p.team} ({p.projected_points:.1f} pts, {injury_status})")
        
        # Show statistics
        total_count = session.query(Player).count()
        by_position = {}
        for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'D/ST']:
            count = session.query(Player).filter_by(position=pos).count()
            if count > 0:
                by_position[pos] = count
        
        print(f"\nDatabase Statistics:")
        print(f"  Total players: {total_count}")
        print(f"  By position:")
        for pos, count in by_position.items():
            print(f"    {pos}: {count}")
        
    except Exception as e:
        print(f"❌ Error updating player data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("PLAYER DATA UPDATE SCRIPT")
    print("=" * 60)
    update_player_data()