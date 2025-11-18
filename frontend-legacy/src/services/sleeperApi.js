/**
 * Sleeper Fantasy Football API Service
 * Official API Documentation: https://docs.sleeper.com/
 * 
 * Key Features:
 * - No authentication required (read-only)
 * - Rate limit: <1000 calls per minute
 * - Free to use
 * - Backend proxy support for better CORS handling
 */

const SLEEPER_BASE_URL = 'https://api.sleeper.app/v1';
const BACKEND_BASE_URL = 'http://localhost:8000';
const CURRENT_SEASON = '2024';

class SleeperApiService {
  /**
   * Get user information by username
   * @param {string} username - Sleeper username
   * @returns {Promise<Object>} User data including user_id
   */
  static async getUser(username) {
    try {
      // Try backend proxy first for better CORS support
      try {
        const backendResponse = await fetch(`${BACKEND_BASE_URL}/sleeper/user/${username}`);
        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          if (backendData.status === 'success') {
            return {
              status: 'success',
              data: {
                user_id: backendData.data.user_id,
                username: backendData.data.username,
                display_name: backendData.data.display_name,
                avatar: backendData.data.avatar,
                created: backendData.data.created,
                is_bot: backendData.data.is_bot || false
              }
            };
          }
        }
      } catch (backendError) {
        console.log('Backend unavailable, using direct Sleeper API:', backendError.message);
      }

      // Fallback to direct Sleeper API
      const response = await fetch(`${SLEEPER_BASE_URL}/user/${username}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const userData = await response.json();
      
      return {
        status: 'success',
        data: {
          user_id: userData.user_id,
          username: userData.username,
          display_name: userData.display_name,
          avatar: userData.avatar,
          created: userData.created,
          is_bot: userData.is_bot || false
        }
      };
    } catch (error) {
      console.error('Error fetching Sleeper user:', error);
      return {
        status: 'error',
        message: `Failed to find user: ${username}`,
        error: error.message
      };
    }
  }

  /**
   * Get all leagues for a user in a specific season
   * @param {string} userId - User ID from Sleeper
   * @param {string} season - Season year (defaults to current season)  
   * @returns {Promise<Object>} Array of league data
   */
  static async getUserLeagues(userId, season = CURRENT_SEASON) {
    try {
      // Try backend proxy first for better CORS support
      try {
        const backendResponse = await fetch(`${BACKEND_BASE_URL}/sleeper/user/${userId}/leagues?season=${season}`);
        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          if (backendData.status === 'success') {
            // Process and standardize league data from backend
            const processedLeagues = backendData.data.map(league => ({
              id: league.league_id,
              name: league.name,
              platform: 'Sleeper',
              season: parseInt(league.season),
              total_rosters: league.total_rosters,
              status: league.status,
              settings: {
                playoff_week_start: league.settings?.playoff_week_start,
                num_teams: league.total_rosters,
                scoring_type: league.scoring_settings ? 'custom' : 'standard'
              },
              roster_positions: league.roster_positions,
              scoring_settings: league.scoring_settings
            }));

            return {
              status: 'success',
              data: processedLeagues
            };
          }
        }
      } catch (backendError) {
        console.log('Backend unavailable, using direct Sleeper API:', backendError.message);
      }

      // Fallback to direct Sleeper API
      const response = await fetch(`${SLEEPER_BASE_URL}/user/${userId}/leagues/nfl/${season}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const leagues = await response.json();
      
      // Process and standardize league data
      const processedLeagues = leagues.map(league => ({
        id: league.league_id,
        name: league.name,
        platform: 'Sleeper',
        season: parseInt(league.season),
        total_rosters: league.total_rosters,
        status: league.status,
        settings: {
          playoff_week_start: league.settings?.playoff_week_start,
          num_teams: league.total_rosters,
          scoring_type: league.scoring_settings ? 'custom' : 'standard'
        },
        roster_positions: league.roster_positions,
        scoring_settings: league.scoring_settings
      }));

      return {
        status: 'success',
        data: processedLeagues
      };
    } catch (error) {
      console.error('Error fetching Sleeper leagues:', error);
      return {
        status: 'error',
        message: 'Failed to fetch user leagues',
        error: error.message
      };
    }
  }

  /**
   * Get specific league information
   * @param {string} leagueId - League ID
   * @returns {Promise<Object>} League details
   */
  static async getLeague(leagueId) {
    try {
      const response = await fetch(`${SLEEPER_BASE_URL}/league/${leagueId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const league = await response.json();
      
      return {
        status: 'success',
        data: {
          league_id: league.league_id,
          name: league.name,
          season: league.season,
          status: league.status,
          total_rosters: league.total_rosters,
          settings: league.settings,
          scoring_settings: league.scoring_settings,
          roster_positions: league.roster_positions,
          previous_league_id: league.previous_league_id
        }
      };
    } catch (error) {
      console.error('Error fetching Sleeper league:', error);
      return {
        status: 'error',
        message: 'Failed to fetch league data',
        error: error.message
      };
    }
  }

  /**
   * Get all rosters in a league
   * @param {string} leagueId - League ID  
   * @returns {Promise<Object>} Array of roster data
   */
  static async getLeagueRosters(leagueId) {
    try {
      // Try backend proxy first for better CORS support
      try {
        const backendResponse = await fetch(`${BACKEND_BASE_URL}/sleeper/league/${leagueId}/rosters`);
        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          if (backendData.status === 'success') {
            return {
              status: 'success',
              data: backendData.data.map(roster => ({
                roster_id: roster.roster_id,
                owner_id: roster.owner_id,
                players: roster.players || [],
                starters: roster.starters || [],
                reserve: roster.reserve || [],
                taxi: roster.taxi || [],
                settings: {
                  wins: roster.settings?.wins || 0,
                  losses: roster.settings?.losses || 0,
                  ties: roster.settings?.ties || 0,
                  fpts: roster.settings?.fpts || 0,
                  fpts_against: roster.settings?.fpts_against || 0,
                  fpts_decimal: roster.settings?.fpts_decimal || 0,
                  fpts_against_decimal: roster.settings?.fpts_against_decimal || 0
                }
              }))
            };
          }
        }
      } catch (backendError) {
        console.log('Backend unavailable, using direct Sleeper API:', backendError.message);
      }

      // Fallback to direct Sleeper API
      const response = await fetch(`${SLEEPER_BASE_URL}/league/${leagueId}/rosters`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const rosters = await response.json();
      
      return {
        status: 'success',
        data: rosters.map(roster => ({
          roster_id: roster.roster_id,
          owner_id: roster.owner_id,
          players: roster.players || [],
          starters: roster.starters || [],
          reserve: roster.reserve || [],
          taxi: roster.taxi || [],
          settings: {
            wins: roster.settings?.wins || 0,
            losses: roster.settings?.losses || 0,
            ties: roster.settings?.ties || 0,
            fpts: roster.settings?.fpts || 0,
            fpts_against: roster.settings?.fpts_against || 0,
            fpts_decimal: roster.settings?.fpts_decimal || 0,
            fpts_against_decimal: roster.settings?.fpts_against_decimal || 0
          }
        }))
      };
    } catch (error) {
      console.error('Error fetching Sleeper rosters:', error);
      return {
        status: 'error',
        message: 'Failed to fetch league rosters',
        error: error.message
      };
    }
  }

  /**
   * Get league users (team owners)
   * @param {string} leagueId - League ID
   * @returns {Promise<Object>} Array of league users
   */
  static async getLeagueUsers(leagueId) {
    try {
      // Try backend proxy first for better CORS support
      try {
        const backendResponse = await fetch(`${BACKEND_BASE_URL}/sleeper/league/${leagueId}/users`);
        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          if (backendData.status === 'success') {
            return {
              status: 'success',
              data: backendData.data.map(user => ({
                user_id: user.user_id,
                username: user.username,
                display_name: user.display_name,
                avatar: user.avatar,
                team_name: user.metadata?.team_name || user.display_name,
                is_owner: user.is_owner || false
              }))
            };
          }
        }
      } catch (backendError) {
        console.log('Backend unavailable, using direct Sleeper API:', backendError.message);
      }

      // Fallback to direct Sleeper API  
      const response = await fetch(`${SLEEPER_BASE_URL}/league/${leagueId}/users`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const users = await response.json();
      
      return {
        status: 'success',
        data: users.map(user => ({
          user_id: user.user_id,
          username: user.username,
          display_name: user.display_name,
          avatar: user.avatar,
          team_name: user.metadata?.team_name || user.display_name,
          is_owner: user.is_owner || false
        }))
      };
    } catch (error) {
      console.error('Error fetching league users:', error);
      return {
        status: 'error',
        message: 'Failed to fetch league users',
        error: error.message
      };
    }
  }

  /**
   * Get all NFL players (warning: ~5MB response)
   * This should be called sparingly and cached locally
   * @returns {Promise<Object>} All NFL players data
   */
  static async getAllPlayers() {
    try {
      // Check if we have cached players data
      const cachedPlayers = localStorage.getItem('sleeper_players');
      const cacheTimestamp = localStorage.getItem('sleeper_players_timestamp');
      const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
      
      if (cachedPlayers && cacheTimestamp && parseInt(cacheTimestamp) > oneDayAgo) {
        return {
          status: 'success',
          data: JSON.parse(cachedPlayers),
          cached: true
        };
      }

      const response = await fetch(`${SLEEPER_BASE_URL}/players/nfl`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const players = await response.json();
      
      // Cache the players data
      localStorage.setItem('sleeper_players', JSON.stringify(players));
      localStorage.setItem('sleeper_players_timestamp', Date.now().toString());
      
      return {
        status: 'success',
        data: players,
        cached: false
      };
    } catch (error) {
      console.error('Error fetching Sleeper players:', error);
      return {
        status: 'error',
        message: 'Failed to fetch players data',
        error: error.message
      };
    }
  }

  /**
   * Get trending players (add/drop activity)
   * @param {string} type - 'add' or 'drop'
   * @param {number} lookbackHours - Hours to look back (default: 24)
   * @param {number} limit - Number of results (default: 25)
   * @returns {Promise<Object>} Trending players data
   */
  static async getTrendingPlayers(type = 'add', lookbackHours = 24, limit = 25) {
    try {
      const params = new URLSearchParams({
        lookback_hours: lookbackHours.toString(),
        limit: limit.toString()
      });
      
      const response = await fetch(`${SLEEPER_BASE_URL}/players/nfl/trending/${type}?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const trendingData = await response.json();
      
      return {
        status: 'success',
        data: trendingData
      };
    } catch (error) {
      console.error('Error fetching trending players:', error);
      return {
        status: 'error',
        message: 'Failed to fetch trending players',
        error: error.message
      };
    }
  }

  /**
   * Get league matchups for a specific week
   * @param {string} leagueId - League ID
   * @param {number} week - Week number
   * @returns {Promise<Object>} Matchup data
   */
  static async getMatchups(leagueId, week) {
    try {
      const response = await fetch(`${SLEEPER_BASE_URL}/league/${leagueId}/matchups/${week}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const matchups = await response.json();
      
      return {
        status: 'success',
        data: matchups
      };
    } catch (error) {
      console.error('Error fetching matchups:', error);
      return {
        status: 'error',
        message: 'Failed to fetch matchups',
        error: error.message
      };
    }
  }

  /**
   * Search for a player by name from cached players data
   * @param {string} playerName - Player name to search for
   * @returns {Promise<Object>} Matching players
   */
  static async searchPlayers(playerName) {
    try {
      const playersResponse = await this.getAllPlayers();
      if (playersResponse.status !== 'success') {
        return playersResponse;
      }
      
      const players = playersResponse.data;
      const searchTerm = playerName.toLowerCase();
      const matchingPlayers = [];
      
      Object.entries(players).forEach(([playerId, player]) => {
        if (player.search_full_name && 
            player.search_full_name.toLowerCase().includes(searchTerm)) {
          matchingPlayers.push({
            player_id: playerId,
            name: `${player.first_name} ${player.last_name}`,
            position: player.position,
            team: player.team,
            active: player.active,
            age: player.age,
            injury_status: player.injury_status
          });
        }
      });
      
      return {
        status: 'success',
        data: matchingPlayers.slice(0, 20) // Limit results
      };
    } catch (error) {
      console.error('Error searching players:', error);
      return {
        status: 'error',
        message: 'Failed to search players',
        error: error.message
      };
    }
  }
}

export default SleeperApiService;