/**
 * Tests for API Service
 * Validates API configuration and service methods
 */

import ApiService from '../api';
import { apiClient } from '../../config/api';

// Mock axios
jest.mock('axios');
jest.mock('../../config/api', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
  withRetry: jest.fn(),
  checkApiHealth: jest.fn(),
}));

describe('ApiService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('transformData', () => {
    it('should transform team data correctly', () => {
      const rawTeamData = {
        team_id: '123',
        team_name: 'Test Team',
        wins: 5,
        losses: 3,
        ties: 0,
        points_for: 1234.5,
        points_against: 1100.2,
      };

      const transformed = ApiService.transformData(rawTeamData, 'team');

      expect(transformed).toEqual({
        id: '123',
        name: 'Test Team',
        wins: 5,
        losses: 3,
        ties: 0,
        pointsFor: 1234.5,
        pointsAgainst: 1100.2,
        record: '5-3',
        team_id: '123',
        team_name: 'Test Team',
        points_for: 1234.5,
        points_against: 1100.2,
      });
    });

    it('should transform player data correctly', () => {
      const rawPlayerData = {
        player_id: '456',
        player_name: 'John Doe',
        position: 'QB',
        nfl_team: 'KC',
      };

      const transformed = ApiService.transformData(rawPlayerData, 'player');

      expect(transformed).toEqual({
        id: '456',
        name: 'John Doe',
        position: 'QB',
        team: 'KC',
        player_id: '456',
        player_name: 'John Doe',
        nfl_team: 'KC',
      });
    });

    it('should return original data for unknown type', () => {
      const rawData = { test: 'data' };
      const transformed = ApiService.transformData(rawData, 'unknown');
      expect(transformed).toEqual(rawData);
    });

    it('should return null for null data', () => {
      const transformed = ApiService.transformData(null, 'team');
      expect(transformed).toBeNull();
    });
  });

  describe('handleError', () => {
    it('should return error message if present', () => {
      const error = new Error('Test error');
      const message = ApiService.handleError(error);
      expect(message).toBe('Test error');
    });

    it('should return response error message if present', () => {
      const error = {
        response: {
          data: {
            message: 'API error message',
          },
        },
      };
      const message = ApiService.handleError(error);
      expect(message).toBe('API error message');
    });

    it('should return default message for unknown error', () => {
      const error = {};
      const message = ApiService.handleError(error);
      expect(message).toBe('An unexpected error occurred. Please try again.');
    });
  });

  describe('API Methods', () => {
    const { withRetry } = require('../../config/api');

    beforeEach(() => {
      withRetry.mockImplementation((fn) => fn());
    });

    it('should call getTeamData with correct endpoint', async () => {
      const mockData = { team_name: 'Test Team' };
      apiClient.get.mockResolvedValue(mockData);

      const result = await ApiService.getTeamData('123');

      expect(apiClient.get).toHaveBeenCalledWith('/user/team/123');
      expect(result).toEqual(mockData);
    });

    it('should call getLeagueAnalytics with correct endpoint', async () => {
      const mockData = { analytics: 'data' };
      apiClient.get.mockResolvedValue(mockData);

      const result = await ApiService.getLeagueAnalytics('456');

      expect(apiClient.get).toHaveBeenCalledWith('/analytics/league/456');
      expect(result).toEqual(mockData);
    });

    it('should call getTradeSuggestions with correct endpoint and data', async () => {
      const mockData = [{ trade: 'suggestion' }];
      const filters = { position: 'QB' };
      apiClient.post.mockResolvedValue(mockData);

      const result = await ApiService.getTradeSuggestions('123', filters);

      expect(apiClient.post).toHaveBeenCalledWith('/trade/suggestions/123', filters);
      expect(result).toEqual(mockData);
    });
  });

  describe('testConnection', () => {
    const { checkApiHealth } = require('../../config/api');

    it('should return health check result', async () => {
      checkApiHealth.mockResolvedValue(true);

      const result = await ApiService.testConnection();

      expect(checkApiHealth).toHaveBeenCalled();
      expect(result).toBe(true);
    });
  });
});