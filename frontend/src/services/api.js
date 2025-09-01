/**
 * API service for Fantasy Football Domination App
 * Comprehensive service layer for all backend API interactions
 */

import { apiClient, withRetry, checkApiHealth } from '../config/api.js';

/**
 * Main API service class with all endpoints and data transformations
 */
class ApiService {
  /**
   * Test API connectivity and health
   * @returns {Promise<boolean>} API health status
   */
  static async testConnection() {
    return await checkApiHealth();
  }

  // ===== LEAGUE ENDPOINTS =====
  
  /**
   * Fetch league analytics from backend API
   * @param {string} leagueId - League ID to get analytics for
   * @returns {Promise<Object>} League analytics data
   */
  static async getLeagueAnalytics(leagueId) {
    return withRetry(() => apiClient.get(`/analytics/league/${leagueId}`));
  }

  /**
   * Fetch league data from backend API
   * @param {string} leagueId - League ID to get data for
   * @returns {Promise<Object>} League data
   */
  static async getLeagueData(leagueId) {
    return withRetry(() => apiClient.get(`/user/league/${leagueId}`));
  }

  /**
   * Fetch league settings and configuration
   * @param {string} leagueId - League ID
   * @returns {Promise<Object>} League settings
   */
  static async getLeagueSettings(leagueId) {
    return withRetry(() => apiClient.get(`/league/${leagueId}/settings`));
  }

  /**
   * Fetch league standings
   * @param {string} leagueId - League ID
   * @returns {Promise<Array>} League standings
   */
  static async getLeagueStandings(leagueId) {
    return withRetry(() => apiClient.get(`/league/${leagueId}/standings`));
  }

  // ===== TEAM ENDPOINTS =====
  
  /**
   * Fetch team analytics from backend API
   * @param {string} teamId - Team ID to get analytics for
   * @returns {Promise<Object>} Team analytics data
   */
  static async getTeamAnalytics(teamId) {
    return withRetry(() => apiClient.get(`/analytics/team/${teamId}`));
  }

  /**
   * Fetch user team data from backend API
   * @param {string} teamId - Team ID to get data for
   * @returns {Promise<Object>} Team data
   */
  static async getTeamData(teamId) {
    return withRetry(() => apiClient.get(`/user/team/${teamId}`));
  }

  /**
   * Fetch team strength analysis
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Team strength data
   */
  static async getTeamStrength(teamId) {
    return withRetry(() => apiClient.get(`/analytics/team/${teamId}/strength`));
  }

  /**
   * Import team data from external platform
   * @param {Object} importData - Team import configuration
   * @returns {Promise<Object>} Import result
   */
  static async importTeam(importData) {
    return withRetry(() => apiClient.post('/team/import', importData));
  }

  // ===== ROSTER ENDPOINTS =====
  
  /**
   * Fetch user roster data from backend API
   * @param {string} teamId - Team ID to get roster for
   * @returns {Promise<Object>} Roster data
   */
  static async getRoster(teamId) {
    return withRetry(() => apiClient.get(`/user/roster/${teamId}`));
  }

  /**
   * Fetch all team rosters in league
   * @param {string} leagueId - League ID
   * @returns {Promise<Array>} All team rosters
   */
  static async getAllRosters(leagueId) {
    return withRetry(() => apiClient.get(`/league/${leagueId}/rosters`));
  }

  /**
   * Update roster/lineup
   * @param {string} teamId - Team ID
   * @param {Object} lineupData - Lineup configuration
   * @returns {Promise<Object>} Update result
   */
  static async updateLineup(teamId, lineupData) {
    return withRetry(() => apiClient.put(`/team/${teamId}/lineup`, lineupData));
  }

  // ===== TRADE ENDPOINTS =====
  
  /**
   * Fetch trade suggestions for a team
   * @param {string} teamId - Team ID
   * @param {Object} filters - Trade filters and preferences
   * @returns {Promise<Array>} Trade suggestions
   */
  static async getTradeSuggestions(teamId, filters = {}) {
    return withRetry(() => apiClient.post(`/trade/suggestions/${teamId}`, filters));
  }

  /**
   * Analyze a potential trade
   * @param {Object} tradeData - Trade details
   * @returns {Promise<Object>} Trade analysis
   */
  static async analyzeTrade(tradeData) {
    return withRetry(() => apiClient.post('/trade/analyze', tradeData));
  }

  /**
   * Execute/propose a trade
   * @param {Object} tradeProposal - Trade proposal details
   * @returns {Promise<Object>} Trade execution result
   */
  static async proposeTrade(tradeProposal) {
    return withRetry(() => apiClient.post('/trade/propose', tradeProposal));
  }

  /**
   * Get AI-powered trade discovery
   * @param {string} teamId - Team ID
   * @param {Object} preferences - Trade preferences
   * @returns {Promise<Array>} AI trade recommendations
   */
  static async getAITradeDiscovery(teamId, preferences = {}) {
    return withRetry(() => apiClient.post(`/ai/trade-discovery/${teamId}`, preferences));
  }

  // ===== WAIVER WIRE ENDPOINTS =====
  
  /**
   * Fetch available waiver wire players
   * @param {string} leagueId - League ID
   * @param {Object} filters - Player filters
   * @returns {Promise<Array>} Available players
   */

  /**
   * Get waiver wire recommendations
   * @param {string} teamId - Team ID
   * @returns {Promise<Array>} Waiver recommendations
   */
  static async getWaiverRecommendations(teamId) {
    return withRetry(() => apiClient.get(`/waiver/recommendations/${teamId}`));
  }

  /**
   * Submit waiver claim
   * @param {Object} claimData - Waiver claim details
   * @returns {Promise<Object>} Claim submission result
   */
  static async submitWaiverClaim(claimData) {
    return withRetry(() => apiClient.post('/waiver/claim', claimData));
  }

  // ===== PLAYER ENDPOINTS =====
  
  /**
   * Search for players
   * @param {string} query - Search query
   * @param {Object} filters - Search filters
   * @returns {Promise<Array>} Player search results
   */
  static async searchPlayers(query, filters = {}) {
    return withRetry(() => apiClient.post('/players/search', { query, ...filters }));
  }

  /**
   * Get player details and stats
   * @param {string} playerId - Player ID
   * @returns {Promise<Object>} Player details
   */
  static async getPlayerDetails(playerId) {
    return withRetry(() => apiClient.get(`/players/${playerId}`));
  }

  /**
   * Get player projections
   * @param {string} playerId - Player ID
   * @param {number} weeks - Number of weeks to project
   * @returns {Promise<Object>} Player projections
   */
  static async getPlayerProjections(playerId, weeks = 4) {
    return withRetry(() => apiClient.get(`/players/${playerId}/projections?weeks=${weeks}`));
  }

  // ===== NEWS AND UPDATES ENDPOINTS =====
  
  /**
   * Fetch latest fantasy football news
   * @param {Object} filters - News filters
   * @returns {Promise<Array>} News articles
   */
  static async getNews(filters = {}) {
    return withRetry(() => apiClient.post('/news', filters));
  }

  /**
   * Get player-specific news
   * @param {string} playerId - Player ID
   * @returns {Promise<Array>} Player news
   */
  static async getPlayerNews(playerId) {
    return withRetry(() => apiClient.get(`/news/player/${playerId}`));
  }

  /**
   * Get injury reports
   * @param {string} leagueId - League ID (optional)
   * @returns {Promise<Array>} Injury reports
   */
  static async getInjuryReports(leagueId) {
    const endpoint = leagueId ? `/news/injuries?league=${leagueId}` : '/news/injuries';
    return withRetry(() => apiClient.get(endpoint));
  }

  // ===== DRAFT ENDPOINTS =====
  
  /**
   * Get draft board and rankings
   * @param {Object} settings - Draft settings
   * @returns {Promise<Object>} Draft board data
   */
  static async getDraftBoard(settings = {}) {
    return withRetry(() => apiClient.post('/draft/board', settings));
  }

  /**
   * Get expert draft recommendations
   * @param {Object} draftState - Current draft state
   * @returns {Promise<Array>} Draft recommendations
   */
  static async getExpertDraftPicks(draftState) {
    return withRetry(() => apiClient.post('/draft/expert-picks', draftState));
  }

  /**
   * Simulate draft scenarios
   * @param {Object} scenario - Draft scenario parameters
   * @returns {Promise<Object>} Simulation results
   */
  static async simulateDraft(scenario) {
    return withRetry(() => apiClient.post('/draft/simulate', scenario));
  }

  // ===== WAIVER WIRE ENDPOINTS =====
  
  /**
   * Get waiver wire free agents
   * @param {string} leagueId - League ID
   * @param {string} position - Position filter (optional)
   * @param {number} size - Number of players to return (default 50)
   * @returns {Promise<Object>} Free agents with recommendations
   */
  static async getWaiverWirePlayers(leagueId, position = null, size = 50) {
    let endpoint = `/waiver-wire/${leagueId}?size=${size}`;
    if (position) {
      endpoint += `&position=${position}`;
    }
    return withRetry(() => apiClient.get(endpoint));
  }

  /**
   * Get enhanced waiver wire analysis with personalized recommendations
   * @param {string} leagueId - League ID
   * @param {string} teamId - Team ID to analyze for
   * @param {string} platform - Platform (espn or sleeper)
   * @param {number} currentWeek - Current NFL week
   * @returns {Promise<Object>} Enhanced waiver analysis with recommendations
   */
  static async getEnhancedWaiverAnalysis(leagueId, teamId, platform = 'espn', currentWeek = 1) {
    const endpoint = `/waiver-wire/${leagueId}/enhanced-analysis?team_id=${teamId}&platform=${platform}&current_week=${currentWeek}`;
    return withRetry(() => apiClient.get(endpoint));
  }

  /**
   * Compare waiver wire player with roster player
   * @param {Object} comparisonData - Player comparison data
   * @returns {Promise<Object>} Player comparison analysis
   */
  static async compareWaiverPlayers(comparisonData) {
    return withRetry(() => apiClient.post('/waiver-wire/compare-players', comparisonData));
  }

  // ===== ANALYTICS ENDPOINTS =====
  
  /**
   * Get advanced team analytics
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Advanced analytics
   */
  static async getAdvancedAnalytics(teamId) {
    return withRetry(() => apiClient.get(`/analytics/advanced/${teamId}`));
  }

  /**
   * Get matchup analysis
   * @param {string} teamId - Team ID
   * @param {number} week - Week number (optional)
   * @returns {Promise<Object>} Matchup analysis
   */
  static async getMatchupAnalysis(teamId, week) {
    const endpoint = week ? `/analytics/matchup/${teamId}?week=${week}` : `/analytics/matchup/${teamId}`;
    return withRetry(() => apiClient.get(endpoint));
  }

  /**
   * Get playoff scenarios
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Playoff scenarios
   */
  static async getPlayoffScenarios(teamId) {
    return withRetry(() => apiClient.get(`/analytics/playoffs/${teamId}`));
  }

  // ===== UTILITY METHODS =====
  
  /**
   * Transform API response data to frontend format
   * @param {Object} data - Raw API data
   * @param {string} type - Data type for transformation
   * @returns {Object} Transformed data
   */
  static transformData(data, type) {
    if (!data) return null;
    
    switch (type) {
      case 'team':
        return {
          id: data.team_id || data.id,
          name: data.team_name || data.name,
          wins: data.wins || 0,
          losses: data.losses || 0,
          ties: data.ties || 0,
          pointsFor: data.points_for || data.pointsFor || 0,
          pointsAgainst: data.points_against || data.pointsAgainst || 0,
          record: `${data.wins || 0}-${data.losses || 0}${data.ties ? `-${data.ties}` : ''}`,
          ...data
        };
        
      case 'player':
        return {
          id: data.player_id || data.id,
          name: data.player_name || data.name,
          position: data.position,
          team: data.nfl_team || data.team,
          ...data
        };
        
      default:
        return data;
    }
  }

  /**
   * Handle API errors with user-friendly messages
   * @param {Error} error - API error
   * @returns {string} User-friendly error message
   */
  static handleError(error) {
    if (error.message) {
      return error.message;
    }
    
    if (error.response && error.response.data && error.response.data.message) {
      return error.response.data.message;
    }
    
    return 'An unexpected error occurred. Please try again.';
  }
}

// Export individual methods for direct import
export const getWaiverWirePlayers = ApiService.getWaiverWirePlayers;
export const getEnhancedWaiverAnalysis = ApiService.getEnhancedWaiverAnalysis;
export const compareWaiverPlayers = ApiService.compareWaiverPlayers;
export const getLeagueAnalytics = ApiService.getLeagueAnalytics;
export const getLeagueData = ApiService.getLeagueData;
export const getUserRoster = ApiService.getUserRoster;
export const getUserProfile = ApiService.getUserProfile;
export const getTradeRecommendations = ApiService.getTradeRecommendations;

export default ApiService;