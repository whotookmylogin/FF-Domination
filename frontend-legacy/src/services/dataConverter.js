/**
 * Unified Data Format Converter
 * Converts data from different fantasy platforms (ESPN, Sleeper) into a standardized format
 * Ensures consistent data structure across the application
 */

class DataConverter {
  /**
   * Convert team data from any platform to unified format
   * @param {Object} rawData - Raw team data from platform
   * @param {string} platform - Platform name ('ESPN' or 'Sleeper')
   * @returns {Object} Unified team data format
   */
  static convertTeamData(rawData, platform) {
    const baseFormat = {
      team_id: null,
      team_name: null,
      platform: platform,
      owner_info: {
        user_id: null,
        username: null,
        display_name: null
      },
      record: {
        wins: 0,
        losses: 0,
        ties: 0
      },
      points: {
        points_for: 0,
        points_against: 0,
        points_decimal: 0
      },
      roster_settings: {},
      league_info: {
        league_id: null,
        league_name: null,
        season: null,
        total_teams: null
      }
    };

    switch (platform.toLowerCase()) {
      case 'espn':
        return this.convertESPNTeamData(rawData, baseFormat);
      case 'sleeper':
        return this.convertSleeperTeamData(rawData, baseFormat);
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }
  }

  /**
   * Convert ESPN team data to unified format
   */
  static convertESPNTeamData(espnData, baseFormat) {
    return {
      ...baseFormat,
      team_id: espnData.team_id || espnData.id,
      team_name: espnData.team_name || espnData.name,
      platform: 'ESPN',
      owner_info: {
        user_id: espnData.user_id || espnData.owner_id,
        username: espnData.username || 'ESPN User',
        display_name: espnData.team_name || espnData.name
      },
      record: {
        wins: espnData.wins || 0,
        losses: espnData.losses || 0,
        ties: espnData.ties || 0
      },
      points: {
        points_for: espnData.points_for || espnData.pointsFor || 0,
        points_against: espnData.points_against || espnData.pointsAgainst || 0,
        points_decimal: 0 // ESPN doesn't typically use decimal points
      },
      league_info: {
        league_id: espnData.league_id,
        league_name: espnData.league_name,
        season: espnData.season || new Date().getFullYear(),
        total_teams: espnData.total_teams || 12
      }
    };
  }

  /**
   * Convert Sleeper team data to unified format
   */
  static convertSleeperTeamData(sleeperData, baseFormat) {
    return {
      ...baseFormat,
      team_id: sleeperData.roster_id,
      team_name: sleeperData.team_name || sleeperData.display_name,
      platform: 'Sleeper',
      owner_info: {
        user_id: sleeperData.owner_id || sleeperData.user_id,
        username: sleeperData.username,
        display_name: sleeperData.display_name
      },
      record: {
        wins: sleeperData.settings?.wins || sleeperData.wins || 0,
        losses: sleeperData.settings?.losses || sleeperData.losses || 0,
        ties: sleeperData.settings?.ties || sleeperData.ties || 0
      },
      points: {
        points_for: sleeperData.settings?.fpts || sleeperData.fpts || 0,
        points_against: sleeperData.settings?.fpts_against || sleeperData.fpts_against || 0,
        points_decimal: sleeperData.settings?.fpts_decimal || sleeperData.fpts_decimal || 0
      },
      league_info: {
        league_id: sleeperData.league_id,
        league_name: sleeperData.league_name,
        season: sleeperData.season || new Date().getFullYear(),
        total_teams: sleeperData.total_rosters || 12
      }
    };
  }

  /**
   * Convert player data from any platform to unified format
   * @param {Object} rawPlayer - Raw player data from platform
   * @param {string} platform - Platform name
   * @returns {Object} Unified player data format
   */
  static convertPlayerData(rawPlayer, platform) {
    const baseFormat = {
      player_id: null,
      name: null,
      first_name: null,
      last_name: null,
      position: null,
      team: null,
      platform: platform,
      stats: {
        points_total: 0,
        projected_points: 0,
        avg_points: 0,
        games_played: 0
      },
      status: {
        injury_status: 'ACTIVE',
        active: true
      },
      metadata: {}
    };

    switch (platform.toLowerCase()) {
      case 'espn':
        return this.convertESPNPlayerData(rawPlayer, baseFormat);
      case 'sleeper':
        return this.convertSleeperPlayerData(rawPlayer, baseFormat);
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }
  }

  /**
   * Convert ESPN player data to unified format
   */
  static convertESPNPlayerData(espnPlayer, baseFormat) {
    return {
      ...baseFormat,
      player_id: espnPlayer.player_id || espnPlayer.id,
      name: espnPlayer.name || `${espnPlayer.first_name} ${espnPlayer.last_name}`,
      first_name: espnPlayer.first_name || '',
      last_name: espnPlayer.last_name || '',
      position: espnPlayer.position,
      team: espnPlayer.team,
      platform: 'ESPN',
      stats: {
        points_total: espnPlayer.total_points || espnPlayer.points || 0,
        projected_points: espnPlayer.projected_points || 0,
        avg_points: espnPlayer.avg_points || 0,
        games_played: espnPlayer.games_played || 0
      },
      status: {
        injury_status: espnPlayer.injury_status || 'ACTIVE',
        active: espnPlayer.active !== false
      },
      metadata: {
        eligibleSlots: espnPlayer.eligibleSlots,
        ownership: espnPlayer.ownership
      }
    };
  }

  /**
   * Convert Sleeper player data to unified format
   */
  static convertSleeperPlayerData(sleeperPlayer, baseFormat) {
    return {
      ...baseFormat,
      player_id: sleeperPlayer.player_id,
      name: `${sleeperPlayer.first_name || ''} ${sleeperPlayer.last_name || ''}`.trim(),
      first_name: sleeperPlayer.first_name || '',
      last_name: sleeperPlayer.last_name || '',
      position: sleeperPlayer.position,
      team: sleeperPlayer.team,
      platform: 'Sleeper',
      stats: {
        points_total: 0, // Sleeper doesn't provide season totals in player endpoint
        projected_points: 0,
        avg_points: 0,
        games_played: 0
      },
      status: {
        injury_status: sleeperPlayer.injury_status || 'ACTIVE',
        active: sleeperPlayer.active !== false
      },
      metadata: {
        age: sleeperPlayer.age,
        height: sleeperPlayer.height,
        weight: sleeperPlayer.weight,
        years_exp: sleeperPlayer.years_exp,
        college: sleeperPlayer.college
      }
    };
  }

  /**
   * Convert league data from any platform to unified format
   * @param {Object} rawLeague - Raw league data from platform
   * @param {string} platform - Platform name
   * @returns {Object} Unified league data format
   */
  static convertLeagueData(rawLeague, platform) {
    const baseFormat = {
      league_id: null,
      name: null,
      platform: platform,
      season: null,
      status: null,
      settings: {
        total_teams: null,
        playoff_week_start: null,
        regular_season_length: null,
        scoring_type: 'standard'
      },
      roster_positions: [],
      scoring_settings: {}
    };

    switch (platform.toLowerCase()) {
      case 'espn':
        return this.convertESPNLeagueData(rawLeague, baseFormat);
      case 'sleeper':
        return this.convertSleeperLeagueData(rawLeague, baseFormat);
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }
  }

  /**
   * Convert ESPN league data to unified format
   */
  static convertESPNLeagueData(espnLeague, baseFormat) {
    return {
      ...baseFormat,
      league_id: espnLeague.league_id || espnLeague.id,
      name: espnLeague.name || espnLeague.league_name,
      platform: 'ESPN',
      season: espnLeague.season || espnLeague.year,
      status: espnLeague.status || 'active',
      settings: {
        total_teams: espnLeague.total_teams || espnLeague.size || 12,
        playoff_week_start: espnLeague.playoff_week_start || 15,
        regular_season_length: espnLeague.regular_season_length || 14,
        scoring_type: espnLeague.scoring_type || 'standard'
      },
      roster_positions: espnLeague.roster_positions || [],
      scoring_settings: espnLeague.scoring_settings || {}
    };
  }

  /**
   * Convert Sleeper league data to unified format
   */
  static convertSleeperLeagueData(sleeperLeague, baseFormat) {
    return {
      ...baseFormat,
      league_id: sleeperLeague.league_id,
      name: sleeperLeague.name,
      platform: 'Sleeper',
      season: sleeperLeague.season,
      status: sleeperLeague.status,
      settings: {
        total_teams: sleeperLeague.total_rosters,
        playoff_week_start: sleeperLeague.settings?.playoff_week_start || 15,
        regular_season_length: sleeperLeague.settings?.playoff_week_start - 1 || 14,
        scoring_type: sleeperLeague.scoring_settings ? 'custom' : 'standard'
      },
      roster_positions: sleeperLeague.roster_positions || [],
      scoring_settings: sleeperLeague.scoring_settings || {}
    };
  }

  /**
   * Convert roster data from any platform to unified format
   * @param {Array} rawRoster - Raw roster data from platform
   * @param {string} platform - Platform name
   * @returns {Array} Unified roster data format
   */
  static convertRosterData(rawRoster, platform) {
    if (!Array.isArray(rawRoster)) {
      return [];
    }

    return rawRoster.map(player => this.convertPlayerData(player, platform));
  }

  /**
   * Merge data from multiple platforms for the same entity
   * @param {Array} dataArray - Array of data objects from different platforms
   * @returns {Object} Merged data with platform-specific information preserved
   */
  static mergeMultiPlatformData(dataArray) {
    if (!Array.isArray(dataArray) || dataArray.length === 0) {
      return null;
    }

    if (dataArray.length === 1) {
      return dataArray[0];
    }

    // Use the first item as base and merge others
    const merged = { ...dataArray[0] };
    merged.platforms = {};

    dataArray.forEach(data => {
      merged.platforms[data.platform.toLowerCase()] = {
        ...data,
        last_updated: new Date().toISOString()
      };
    });

    return merged;
  }

  /**
   * Validate converted data structure
   * @param {Object} data - Converted data object
   * @param {string} dataType - Type of data ('team', 'player', 'league', 'roster')
   * @returns {boolean} True if valid, throws error if invalid
   */
  static validateConvertedData(data, dataType) {
    const requiredFields = {
      team: ['team_id', 'team_name', 'platform'],
      player: ['player_id', 'name', 'position', 'platform'],
      league: ['league_id', 'name', 'platform', 'season'],
      roster: [] // Array validation handled separately
    };

    if (dataType === 'roster') {
      return Array.isArray(data);
    }

    const required = requiredFields[dataType];
    if (!required) {
      throw new Error(`Unknown data type: ${dataType}`);
    }

    for (const field of required) {
      if (!data[field]) {
        throw new Error(`Missing required field '${field}' in ${dataType} data`);
      }
    }

    return true;
  }
}

export default DataConverter;