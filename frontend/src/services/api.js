// API service for Fantasy Football Domination App

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  /**
   * Fetch league analytics from backend API
   * @param {string} leagueId - League ID to get analytics for
   * @returns {Promise<Object>} League analytics data
   */
  static async getLeagueAnalytics(leagueId) {
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/league/${leagueId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching league analytics:', error);
      throw error;
    }
  }

  /**
   * Fetch team analytics from backend API
   * @param {string} teamId - Team ID to get analytics for
   * @returns {Promise<Object>} Team analytics data
   */
  static async getTeamAnalytics(teamId) {
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/team/${teamId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching team analytics:', error);
      throw error;
    }
  }

  /**
   * Fetch user roster data from backend API
   * @param {string} teamId - Team ID to get roster for
   * @returns {Promise<Object>} Roster data
   */
  static async getRoster(teamId) {
    try {
      const response = await fetch(`${API_BASE_URL}/user/roster/${teamId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching roster data:', error);
      throw error;
    }
  }

  /**
   * Fetch user team data from backend API
   * @param {string} teamId - Team ID to get data for
   * @returns {Promise<Object>} Team data
   */
  static async getTeamData(teamId) {
    try {
      const response = await fetch(`${API_BASE_URL}/user/team/${teamId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching team data:', error);
      throw error;
    }
  }

  /**
   * Fetch user league data from backend API
   * @param {string} leagueId - League ID to get data for
   * @returns {Promise<Object>} League data
   */
  static async getLeagueData(leagueId) {
    try {
      const response = await fetch(`${API_BASE_URL}/user/league/${leagueId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching league data:', error);
      throw error;
    }
  }
}

export default ApiService;
