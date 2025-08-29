/**
 * Team Import Component
 * Allows users to import teams from multiple fantasy platforms (ESPN, Sleeper)
 * Features platform selection, league search, and team selection
 */
import React, { useState, useEffect } from 'react';
import SleeperApiService from '../services/sleeperApi';
import ApiService from '../services/api';
import './TeamImport.css';

const TeamImport = ({ onTeamImported }) => {
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [step, setStep] = useState('platform'); // platform, search, leagues, confirm
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Platform-specific states
  const [espnLeagueId, setEspnLeagueId] = useState('');
  const [espnTeamId, setEspnTeamId] = useState('');
  const [sleeperUsername, setSleeperUsername] = useState('');
  const [sleeperUser, setSleeperUser] = useState(null);
  const [availableLeagues, setAvailableLeagues] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);

  const platforms = [
    {
      id: 'espn',
      name: 'ESPN Fantasy',
      description: 'Import from ESPN Fantasy Football',
      icon: '🏈',
      color: '#ff6b35',
      features: ['Real-time data', 'Full roster sync', 'Season stats']
    },
    {
      id: 'sleeper',
      name: 'Sleeper',
      description: 'Import from Sleeper Fantasy Football',
      icon: '😴',
      color: '#00d4ff',
      features: ['Modern interface', 'Advanced analytics', 'Social features']
    }
  ];

  const handlePlatformSelect = (platformId) => {
    setSelectedPlatform(platformId);
    setStep('search');
    setError(null);
  };

  const handleBack = () => {
    if (step === 'search') {
      setStep('platform');
      setSelectedPlatform('');
    } else if (step === 'leagues') {
      setStep('search');
    } else if (step === 'confirm') {
      setStep('leagues');
    }
    setError(null);
  };

  const handleESPNSearch = async () => {
    if (!espnLeagueId || !espnTeamId) {
      setError('Please enter both League ID and Team ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Test ESPN connection
      const teamData = await ApiService.getTeamData(espnTeamId);
      
      if (teamData.status === 'success') {
        setSelectedTeam({
          platform: 'ESPN',
          leagueId: espnLeagueId,
          teamId: espnTeamId,
          teamName: teamData.data.team_name,
          record: `${teamData.data.wins}-${teamData.data.losses}-${teamData.data.ties}`,
          pointsFor: teamData.data.points_for
        });
        setStep('confirm');
      } else {
        setError('Could not find team with that League ID and Team ID combination');
      }
    } catch (err) {
      console.error('ESPN search error:', err);
      setError('Failed to connect to ESPN. Please check your League ID and Team ID.');
    } finally {
      setLoading(false);
    }
  };

  const handleSleeperUserSearch = async () => {
    if (!sleeperUsername.trim()) {
      setError('Please enter your Sleeper username');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Get user information
      const userResponse = await SleeperApiService.getUser(sleeperUsername.trim());
      
      if (userResponse.status === 'success') {
        setSleeperUser(userResponse.data);
        
        // Get user's leagues
        const leaguesResponse = await SleeperApiService.getUserLeagues(userResponse.data.user_id);
        
        if (leaguesResponse.status === 'success' && leaguesResponse.data.length > 0) {
          setAvailableLeagues(leaguesResponse.data);
          setStep('leagues');
        } else {
          setError('No leagues found for this user in the current season');
        }
      } else {
        setError(`User not found: ${sleeperUsername}`);
      }
    } catch (err) {
      console.error('Sleeper search error:', err);
      setError('Failed to find Sleeper user. Please check the username.');
    } finally {
      setLoading(false);
    }
  };

  const handleLeagueSelect = async (league) => {
    setLoading(true);
    setError(null);

    try {
      // Get league rosters to find user's team
      const rostersResponse = await SleeperApiService.getLeagueRosters(league.id);
      const usersResponse = await SleeperApiService.getLeagueUsers(league.id);
      
      if (rostersResponse.status === 'success' && usersResponse.status === 'success') {
        // Find user's roster
        const userRoster = rostersResponse.data.find(roster => roster.owner_id === sleeperUser.user_id);
        const userInfo = usersResponse.data.find(user => user.user_id === sleeperUser.user_id);
        
        if (userRoster && userInfo) {
          setSelectedLeague(league);
          setSelectedTeam({
            platform: 'Sleeper',
            leagueId: league.id,
            teamId: userRoster.roster_id,
            userId: sleeperUser.user_id,
            teamName: userInfo.team_name || userInfo.display_name,
            record: `${userRoster.settings.wins}-${userRoster.settings.losses}-${userRoster.settings.ties}`,
            pointsFor: (userRoster.settings.fpts + userRoster.settings.fpts_decimal).toFixed(1),
            playersCount: userRoster.players.length
          });
          setStep('confirm');
        } else {
          setError('Could not find your team in this league');
        }
      } else {
        setError('Failed to load league data');
      }
    } catch (err) {
      console.error('League selection error:', err);
      setError('Failed to load league information');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    setLoading(true);
    setError(null);

    try {
      // Here you would typically save the team data to your backend
      // For now, we'll just pass it back to the parent component
      if (onTeamImported) {
        onTeamImported(selectedTeam);
      }
      
      // Reset form
      setStep('platform');
      setSelectedPlatform('');
      setSelectedTeam(null);
      setSelectedLeague(null);
      setAvailableLeagues([]);
      setSleeperUser(null);
      setEspnLeagueId('');
      setEspnTeamId('');
      setSleeperUsername('');
      
    } catch (err) {
      console.error('Import error:', err);
      setError('Failed to import team');
    } finally {
      setLoading(false);
    }
  };

  const renderPlatformSelection = () => (
    <div className="platform-selection">
      <div className="import-header">
        <h2>Import Your Fantasy Team</h2>
        <p>Choose your fantasy football platform to get started</p>
      </div>
      
      <div className="platforms-grid">
        {platforms.map(platform => (
          <div 
            key={platform.id}
            className="platform-card"
            onClick={() => handlePlatformSelect(platform.id)}
          >
            <div className="platform-icon" style={{ color: platform.color }}>
              {platform.icon}
            </div>
            <h3>{platform.name}</h3>
            <p>{platform.description}</p>
            <ul className="platform-features">
              {platform.features.map((feature, index) => (
                <li key={index}>✓ {feature}</li>
              ))}
            </ul>
            <button className="btn btn-primary">
              Import from {platform.name}
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSearchForm = () => (
    <div className="search-form">
      <div className="import-header">
        <h2>
          {selectedPlatform === 'espn' ? '🏈 ESPN Fantasy' : '😴 Sleeper'} Import
        </h2>
        <p>
          {selectedPlatform === 'espn' 
            ? 'Enter your ESPN League ID and Team ID' 
            : 'Enter your Sleeper username to find your leagues'
          }
        </p>
      </div>

      {selectedPlatform === 'espn' ? (
        <div className="espn-form">
          <div className="form-group">
            <label className="form-label">League ID</label>
            <input
              type="text"
              className="form-input"
              value={espnLeagueId}
              onChange={(e) => setEspnLeagueId(e.target.value)}
              placeholder="e.g., 83806"
            />
            <small>Find this in your ESPN league URL</small>
          </div>
          
          <div className="form-group">
            <label className="form-label">Team ID</label>
            <input
              type="text"
              className="form-input"
              value={espnTeamId}
              onChange={(e) => setEspnTeamId(e.target.value)}
              placeholder="e.g., 7"
            />
            <small>Your team number in the league (1-12)</small>
          </div>
          
          <button 
            className="btn btn-primary"
            onClick={handleESPNSearch}
            disabled={loading || !espnLeagueId || !espnTeamId}
          >
            {loading ? 'Searching...' : 'Find My Team'}
          </button>
        </div>
      ) : (
        <div className="sleeper-form">
          <div className="form-group">
            <label className="form-label">Sleeper Username</label>
            <input
              type="text"
              className="form-input"
              value={sleeperUsername}
              onChange={(e) => setSleeperUsername(e.target.value)}
              placeholder="Your Sleeper username"
            />
            <small>This is your @username on Sleeper</small>
          </div>
          
          <button 
            className="btn btn-primary"
            onClick={handleSleeperUserSearch}
            disabled={loading || !sleeperUsername.trim()}
          >
            {loading ? 'Searching...' : 'Find My Leagues'}
          </button>
        </div>
      )}
    </div>
  );

  const renderLeagueSelection = () => (
    <div className="league-selection">
      <div className="import-header">
        <h2>Select Your League</h2>
        <p>Choose which league you want to import</p>
      </div>
      
      <div className="leagues-grid">
        {availableLeagues.map(league => (
          <div 
            key={league.id}
            className="league-card"
            onClick={() => handleLeagueSelect(league)}
          >
            <div className="league-info">
              <h3>{league.name}</h3>
              <div className="league-details">
                <span className="league-teams">{league.total_rosters} Teams</span>
                <span className="league-season">{league.season} Season</span>
                <span className="league-status">{league.status}</span>
              </div>
            </div>
            <button className="btn btn-sm btn-primary">
              Select League
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderConfirmation = () => (
    <div className="import-confirmation">
      <div className="import-header">
        <h2>Confirm Team Import</h2>
        <p>Please confirm the details of your team</p>
      </div>
      
      <div className="team-preview">
        <div className="team-card-large">
          <div className="team-platform">
            <span className="platform-badge">
              {selectedTeam.platform === 'ESPN' ? '🏈' : '😴'} {selectedTeam.platform}
            </span>
          </div>
          
          <h3>{selectedTeam.teamName}</h3>
          
          <div className="team-stats">
            <div className="stat-item">
              <span className="stat-label">Record</span>
              <span className="stat-value">{selectedTeam.record}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Points For</span>
              <span className="stat-value">{selectedTeam.pointsFor}</span>
            </div>
            {selectedTeam.playersCount && (
              <div className="stat-item">
                <span className="stat-label">Players</span>
                <span className="stat-value">{selectedTeam.playersCount}</span>
              </div>
            )}
          </div>
          
          <div className="import-actions">
            <button 
              className="btn btn-primary btn-lg"
              onClick={handleConfirmImport}
              disabled={loading}
            >
              {loading ? 'Importing...' : 'Import This Team'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="team-import-page">
      <div className="page-header">
        <h1>⚡ Team Import</h1>
        <p>Connect your fantasy teams from multiple platforms</p>
      </div>

      {step !== 'platform' && (
        <button className="btn btn-secondary back-button" onClick={handleBack}>
          ← Back
        </button>
      )}

      {error && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          {error}
        </div>
      )}

      <div className="import-content">
        {step === 'platform' && renderPlatformSelection()}
        {step === 'search' && renderSearchForm()}
        {step === 'leagues' && renderLeagueSelection()}
        {step === 'confirm' && renderConfirmation()}
      </div>
    </div>
  );
};

export default TeamImport;