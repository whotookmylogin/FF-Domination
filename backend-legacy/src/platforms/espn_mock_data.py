"""
Mock data for ESPN integration testing and development.
Provides realistic fantasy football data when ESPN credentials are not available.
"""

from typing import Dict, List, Any
import random
from datetime import datetime, timedelta

# NFL teams data
NFL_TEAMS = {
    1: {"name": "Atlanta Falcons", "abbrev": "ATL"},
    2: {"name": "Buffalo Bills", "abbrev": "BUF"},
    3: {"name": "Chicago Bears", "abbrev": "CHI"},
    4: {"name": "Cincinnati Bengals", "abbrev": "CIN"},
    5: {"name": "Cleveland Browns", "abbrev": "CLE"},
    6: {"name": "Dallas Cowboys", "abbrev": "DAL"},
    7: {"name": "Denver Broncos", "abbrev": "DEN"},
    8: {"name": "Detroit Lions", "abbrev": "DET"},
    9: {"name": "Green Bay Packers", "abbrev": "GB"},
    10: {"name": "Tennessee Titans", "abbrev": "TEN"},
    11: {"name": "Indianapolis Colts", "abbrev": "IND"},
    12: {"name": "Kansas City Chiefs", "abbrev": "KC"},
    13: {"name": "Las Vegas Raiders", "abbrev": "LV"},
    14: {"name": "Los Angeles Rams", "abbrev": "LAR"},
    15: {"name": "Miami Dolphins", "abbrev": "MIA"},
    16: {"name": "Minnesota Vikings", "abbrev": "MIN"},
    17: {"name": "New England Patriots", "abbrev": "NE"},
    18: {"name": "New Orleans Saints", "abbrev": "NO"},
    19: {"name": "New York Giants", "abbrev": "NYG"},
    20: {"name": "New York Jets", "abbrev": "NYJ"},
    21: {"name": "Philadelphia Eagles", "abbrev": "PHI"},
    22: {"name": "Arizona Cardinals", "abbrev": "ARI"},
    23: {"name": "Pittsburgh Steelers", "abbrev": "PIT"},
    24: {"name": "Los Angeles Chargers", "abbrev": "LAC"},
    25: {"name": "San Francisco 49ers", "abbrev": "SF"},
    26: {"name": "Seattle Seahawks", "abbrev": "SEA"},
    27: {"name": "Tampa Bay Buccaneers", "abbrev": "TB"},
    28: {"name": "Washington Commanders", "abbrev": "WSH"},
    29: {"name": "Carolina Panthers", "abbrev": "CAR"},
    30: {"name": "Jacksonville Jaguars", "abbrev": "JAX"},
    33: {"name": "Baltimore Ravens", "abbrev": "BAL"},
    34: {"name": "Houston Texans", "abbrev": "HOU"}
}

# Sample fantasy players data
SAMPLE_PLAYERS = [
    # Quarterbacks
    {"id": 4046533, "name": "Josh Allen", "position": "QB", "team": "BUF", "status": "Active"},
    {"id": 3139477, "name": "Patrick Mahomes", "position": "QB", "team": "KC", "status": "Active"},
    {"id": 2330, "name": "Aaron Rodgers", "position": "QB", "team": "NYJ", "status": "Active"},
    {"id": 3916387, "name": "Lamar Jackson", "position": "QB", "team": "BAL", "status": "Active"},
    {"id": 4040715, "name": "Joe Burrow", "position": "QB", "team": "CIN", "status": "Active"},
    
    # Running Backs
    {"id": 4036131, "name": "Christian McCaffrey", "position": "RB", "team": "SF", "status": "Active"},
    {"id": 3128390, "name": "Derrick Henry", "position": "RB", "team": "BAL", "status": "Active"},
    {"id": 4035687, "name": "Alvin Kamara", "position": "RB", "team": "NO", "status": "Active"},
    {"id": 4240069, "name": "Jonathan Taylor", "position": "RB", "team": "IND", "status": "Active"},
    {"id": 4239993, "name": "Najee Harris", "position": "RB", "team": "PIT", "status": "Active"},
    
    # Wide Receivers
    {"id": 3929520, "name": "Tyreek Hill", "position": "WR", "team": "MIA", "status": "Active"},
    {"id": 4035710, "name": "Cooper Kupp", "position": "WR", "team": "LAR", "status": "Active"},
    {"id": 4040715, "name": "Ja'Marr Chase", "position": "WR", "team": "CIN", "status": "Active"},
    {"id": 3915416, "name": "Stefon Diggs", "position": "WR", "team": "HOU", "status": "Active"},
    {"id": 4036378, "name": "DK Metcalf", "position": "WR", "team": "SEA", "status": "Active"},
    
    # Tight Ends
    {"id": 3043078, "name": "Travis Kelce", "position": "TE", "team": "KC", "status": "Active"},
    {"id": 4046503, "name": "Mark Andrews", "position": "TE", "team": "BAL", "status": "Active"},
    {"id": 4035329, "name": "George Kittle", "position": "TE", "team": "SF", "status": "Active"},
    {"id": 4240069, "name": "T.J. Hockenson", "position": "TE", "team": "MIN", "status": "Active"},
    {"id": 3917792, "name": "Darren Waller", "position": "TE", "team": "NYG", "status": "Active"},
    
    # Defenses
    {"id": 16, "name": "Bills D/ST", "position": "D/ST", "team": "BUF", "status": "Active"},
    {"id": 21, "name": "Eagles D/ST", "position": "D/ST", "team": "PHI", "status": "Active"},
    {"id": 25, "name": "49ers D/ST", "position": "D/ST", "team": "SF", "status": "Active"},
    
    # Kickers
    {"id": 2306, "name": "Justin Tucker", "position": "K", "team": "BAL", "status": "Active"},
    {"id": 4372, "name": "Harrison Butker", "position": "K", "team": "KC", "status": "Active"}
]

# Sample fantasy team names
SAMPLE_TEAM_NAMES = [
    "Thunder Bolts", "Grid Iron Warriors", "End Zone Crushers", "Fantasy Champions",
    "Touchdown Masters", "Pigskin Legends", "Field Goal Heroes", "Blitz Brigade",
    "Red Zone Raiders", "Super Bowl Bound", "Fantasy Phenoms", "Gridiron Gladiators"
]


class ESPNMockDataProvider:
    """Provides realistic mock data for ESPN fantasy football integration."""
    
    @staticmethod
    def get_mock_roster_data(year: int, league_id: str) -> Dict[str, Any]:
        """
        Generate mock roster data for a fantasy league.
        
        Args:
            year: Fantasy season year
            league_id: League identifier
            
        Returns:
            Dict containing mock roster data
        """
        teams = []
        
        # Generate 10-12 teams with rosters
        num_teams = random.randint(10, 12)
        used_players = set()
        
        for team_id in range(1, num_teams + 1):
            # Create team roster
            roster = []
            positions_needed = {
                'QB': 2, 'RB': 4, 'WR': 6, 'TE': 2, 'D/ST': 2, 'K': 2
            }
            
            for position, count in positions_needed.items():
                available_players = [p for p in SAMPLE_PLAYERS 
                                   if p['position'] == position and p['id'] not in used_players]
                
                if len(available_players) < count:
                    # Generate additional players if needed
                    for i in range(count - len(available_players)):
                        new_player = {
                            'id': random.randint(5000000, 9999999),
                            'name': f"Mock {position} {i+1}",
                            'position': position,
                            'team': random.choice(list(NFL_TEAMS.values()))['abbrev'],
                            'status': random.choice(['Active', 'Questionable', 'Doubtful'])
                        }
                        available_players.append(new_player)
                
                # Add players to roster
                selected = random.sample(available_players, min(count, len(available_players)))
                for player in selected:
                    used_players.add(player['id'])
                    roster.append({
                        'playerId': player['id'],
                        'name': player['name'],
                        'position': player['position'],
                        'proTeam': player['team'],
                        'status': player['status'],
                        'injuryStatus': random.choice([None, 'Questionable', 'Doubtful']) if player['status'] != 'Active' else None
                    })
            
            team_data = {
                'id': team_id,
                'abbrev': f"TM{team_id}",
                'location': f"Team {team_id}",
                'nickname': random.choice(SAMPLE_TEAM_NAMES),
                'owners': [{'id': f"owner_{team_id}", 'displayName': f"Owner {team_id}"}],
                'roster': {'entries': [{'playerPoolEntry': {'player': player}} for player in roster]},
                'record': {
                    'overall': {
                        'wins': random.randint(0, 17),
                        'losses': random.randint(0, 17),
                        'ties': random.randint(0, 2),
                        'pointsFor': round(random.uniform(1200, 1800), 2),
                        'pointsAgainst': round(random.uniform(1200, 1800), 2)
                    }
                }
            }
            teams.append(team_data)
        
        return {
            'status': 'success',
            'teams': teams,
            'settings': {
                'name': f"Mock League {league_id}",
                'size': num_teams,
                'scoringPeriodId': 1,
                'seasonId': year
            }
        }
    
    @staticmethod
    def get_mock_transactions_data(year: int, league_id: str) -> Dict[str, Any]:
        """
        Generate mock transaction data for a fantasy league.
        
        Args:
            year: Fantasy season year
            league_id: League identifier
            
        Returns:
            Dict containing mock transaction data
        """
        transactions = []
        
        # Generate sample transactions
        transaction_types = ['WAIVER', 'FREEAGENT', 'TRADE']
        
        for i in range(random.randint(15, 30)):
            transaction_date = datetime.now() - timedelta(days=random.randint(1, 120))
            
            transaction = {
                'id': f"mock_transaction_{i}",
                'type': random.choice(transaction_types),
                'date': transaction_date.isoformat(),
                'status': 'EXECUTED',
                'memberId': random.randint(1, 12),
                'items': []
            }
            
            # Add transaction items
            if transaction['type'] in ['WAIVER', 'FREEAGENT']:
                # Add/drop transaction
                player = random.choice(SAMPLE_PLAYERS)
                transaction['items'] = [
                    {
                        'type': 'ADD',
                        'playerId': player['id'],
                        'playerName': player['name']
                    },
                    {
                        'type': 'DROP',
                        'playerId': random.randint(5000000, 9999999),
                        'playerName': f"Dropped Player {i}"
                    }
                ]
            elif transaction['type'] == 'TRADE':
                # Trade transaction
                player1 = random.choice(SAMPLE_PLAYERS[:10])
                player2 = random.choice(SAMPLE_PLAYERS[10:20])
                transaction['items'] = [
                    {
                        'type': 'TRADE_GIVE',
                        'playerId': player1['id'],
                        'playerName': player1['name']
                    },
                    {
                        'type': 'TRADE_RECEIVE',
                        'playerId': player2['id'],
                        'playerName': player2['name']
                    }
                ]
            
            transactions.append(transaction)
        
        return {
            'status': 'success',
            'transactions': transactions,
            'league_id': league_id,
            'year': year
        }
    
    @staticmethod
    def get_mock_players_data(year: int) -> Dict[str, Any]:
        """
        Generate mock players data for a fantasy season.
        
        Args:
            year: Fantasy season year
            
        Returns:
            Dict containing mock players data
        """
        # Extended player list with stats
        extended_players = []
        
        for player in SAMPLE_PLAYERS:
            # Add mock stats based on position
            stats = {}
            if player['position'] == 'QB':
                stats = {
                    'passingYards': random.randint(2500, 5000),
                    'passingTouchdowns': random.randint(20, 45),
                    'interceptions': random.randint(5, 15),
                    'rushingYards': random.randint(200, 800),
                    'rushingTouchdowns': random.randint(2, 12)
                }
            elif player['position'] == 'RB':
                stats = {
                    'rushingYards': random.randint(800, 2000),
                    'rushingTouchdowns': random.randint(8, 25),
                    'receivingYards': random.randint(200, 800),
                    'receivingTouchdowns': random.randint(2, 10),
                    'receptions': random.randint(20, 80)
                }
            elif player['position'] == 'WR':
                stats = {
                    'receivingYards': random.randint(600, 1800),
                    'receivingTouchdowns': random.randint(5, 15),
                    'receptions': random.randint(50, 120),
                    'rushingYards': random.randint(0, 200),
                    'rushingTouchdowns': random.randint(0, 3)
                }
            elif player['position'] == 'TE':
                stats = {
                    'receivingYards': random.randint(400, 1200),
                    'receivingTouchdowns': random.randint(3, 12),
                    'receptions': random.randint(40, 100)
                }
            
            extended_player = {
                **player,
                'stats': stats,
                'fantasyPoints': round(random.uniform(150, 350), 2),
                'averagePoints': round(random.uniform(8, 25), 2),
                'ownership': round(random.uniform(0.1, 100), 1)
            }
            extended_players.append(extended_player)
        
        return {
            'status': 'success',
            'players': extended_players,
            'year': year,
            'total_players': len(extended_players)
        }
    
    @staticmethod
    def get_mock_user_data(user_id: str) -> Dict[str, Any]:
        """
        Generate mock user data.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing mock user data
        """
        return {
            'status': 'success',
            'user': {
                'id': user_id,
                'displayName': f"Fantasy User {user_id}",
                'firstName': f"User",
                'lastName': f"{user_id}",
                'profileImageUrl': None,
                'teams': [
                    {
                        'id': random.randint(1, 12),
                        'name': random.choice(SAMPLE_TEAM_NAMES),
                        'wins': random.randint(0, 17),
                        'losses': random.randint(0, 17),
                        'ties': random.randint(0, 2),
                        'points_for': round(random.uniform(1200, 1800), 2),
                        'points_against': round(random.uniform(1200, 1800), 2)
                    }
                ]
            }
        }
    
    @staticmethod  
    def get_mock_api_roster_data(user_id: str) -> List[Dict[str, Any]]:
        """
        Generate mock roster data in ESPN API format.
        
        Args:
            user_id: User/team identifier
            
        Returns:
            List of player dictionaries
        """
        roster = []
        positions_needed = {'QB': 2, 'RB': 3, 'WR': 4, 'TE': 2, 'K': 1, 'D/ST': 1}
        
        for position, count in positions_needed.items():
            available_players = [p for p in SAMPLE_PLAYERS if p['position'] == position]
            selected = random.sample(available_players, min(count, len(available_players)))
            
            for player in selected:
                roster.append({
                    'player_id': player['id'],
                    'name': player['name'],
                    'position': player['position'],
                    'team': player['team'],
                    'status': player['status'],
                    'injury_status': random.choice([None, 'Questionable', 'Doubtful'])
                })
        
        return roster
    
    @staticmethod
    def get_mock_api_user_data(user_id: str) -> Dict[str, Any]:
        """
        Generate mock user data in ESPN API format.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing mock user data
        """
        return {
            'user_id': user_id,
            'team_name': random.choice(SAMPLE_TEAM_NAMES),
            'wins': random.randint(0, 17),
            'losses': random.randint(0, 17),
            'ties': random.randint(0, 2),
            'points_for': round(random.uniform(1200, 1800), 2),
            'points_against': round(random.uniform(1200, 1800), 2)
        }
    
    @staticmethod
    def get_mock_api_transactions(user_id: str) -> List[Dict[str, Any]]:
        """
        Generate mock transaction data in ESPN API format.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        for i in range(random.randint(5, 15)):
            transaction_date = datetime.now() - timedelta(days=random.randint(1, 60))
            
            transaction = {
                'type': random.choice(['WAIVER', 'FREEAGENT', 'TRADE']),
                'player': random.choice(SAMPLE_PLAYERS)['name'],
                'date': transaction_date.isoformat()
            }
            transactions.append(transaction)
        
        return transactions