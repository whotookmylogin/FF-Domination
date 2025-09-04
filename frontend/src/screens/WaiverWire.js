import React, { useState, useEffect, useCallback } from 'react';
import WaiverClaimCard from '../components/WaiverClaimCard';
import { getWaiverWirePlayers, getEnhancedWaiverAnalysis } from '../services/api';
import './WaiverWire.css';

const WaiverWire = ({ league }) => {
  const [availablePlayers, setAvailablePlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [faabBudget, setFaabBudget] = useState(100);
  const [positionFilter, setPositionFilter] = useState('');
  const [personalizedRecommendations, setPersonalizedRecommendations] = useState(null);
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [currentWeek, setCurrentWeek] = useState(1);
  
  const fetchAvailablePlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
      
    try {
        // Use current league context
        const leagueId = league?.id;
        const platform = league?.platform;
        const teamId = league?.userTeam?.id || '1'; // Get user's team ID from league context
        
        console.log('WaiverWire - Current league:', league?.name, 'ID:', leagueId, 'Platform:', platform);
        
        if (!leagueId || !platform) {
          setError('No league selected');
          setAvailablePlayers([]);
          setLoading(false);
          return;
        }
        
        // For Sleeper leagues, fetch with platform-specific parameters
        let waiverData;
        let enhancedAnalysis = null;
        
        if (platform?.toLowerCase() === 'sleeper') {
          console.log('Sleeper league detected - fetching Sleeper waiver data');
          
          // Get user ID for Sleeper from league context
          const userId = league?.userId || null;
          
          // Fetch Sleeper waiver data with platform parameter
          waiverData = await getWaiverWirePlayers(
            leagueId, 
            positionFilter || null,
            50,  // size
            'sleeper',  // platform
            userId  // user_id for Sleeper
          );
          
          // Enhanced analysis can be added later for Sleeper
          // For now, just set basic recommendations
        } else {
          // Fetch both standard waiver data and enhanced analysis for ESPN
          [waiverData, enhancedAnalysis] = await Promise.all([
            getWaiverWirePlayers(leagueId, positionFilter || null),
            getEnhancedWaiverAnalysis(leagueId, teamId, platform, currentWeek)
          ]);
        }
        
        const data = waiverData;
        
        // Process enhanced recommendations
        if (enhancedAnalysis.status === 'success') {
          setPersonalizedRecommendations(enhancedAnalysis);
        }
        
        if (data.status === 'success' && data.free_agents) {
          // Format the data for display - handle both ESPN and Sleeper formats
          const formattedPlayers = data.free_agents.map((player, index) => {
            const basePlayer = {
              id: player.player_id || index,
              name: player.name,
              position: player.position,
              team: player.team,
              projectedPoints: player.projected_points || 0,
              newsUrgency: Math.min(5, Math.max(1, Math.floor(player.recommendation_score / 20))),
              bidRecommendation: player.bid_recommendation,
              percentOwned: player.percent_owned || 0,
              injuryStatus: player.injury_status || 'Active'
            };
            
            // Add platform-specific fields
            if (platform?.toLowerCase() === 'sleeper') {
              basePlayer.recommendedFAAB = player.recommended_faab;
              basePlayer.age = player.age;
              basePlayer.yearsExp = player.years_exp;
              basePlayer.depthChart = player.depth_chart_position;
            } else {
              basePlayer.recommendedBid = player.recommended_bid;
            }
            
            return basePlayer;
          });
          
          setAvailablePlayers(formattedPlayers);
        } else {
          // No mock data - show empty state
          setAvailablePlayers([]);
          setError('No waiver wire players available at this time. Please check your league settings.');
        }
      } catch (error) {
        console.error('Error fetching waiver wire data:', error);
        // No mock data on error
        setAvailablePlayers([]);
        setError('Failed to load waiver wire data. Please try again later.');
      }
      
    setLoading(false);
  }, [league, positionFilter, currentWeek]);
  
  useEffect(() => {
    if (league) {
      fetchAvailablePlayers();
    }
  }, [league, fetchAvailablePlayers]);
  
  if (loading) {
    return (
      <div className="screen-container">
        <div className="loading-state">
          <div className="loading-spinner">⏳</div>
          <h3>Loading waiver wire data for {league?.name}...</h3>
        </div>
      </div>
    );
  }
  
  // If no players available, show empty state
  if (!loading && availablePlayers.length === 0 && !error) {
    return (
      <div className="screen-container">
        <div className="screen-header">
          <h1>Waiver Wire - {league?.name}</h1>
        </div>
        <div className="info-banner" style={{
          backgroundColor: '#f5f5f5',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          padding: '20px',
          marginTop: '20px',
          textAlign: 'center'
        }}>
          <h3 style={{ color: '#333', marginBottom: '12px' }}>No Players Available</h3>
          <p style={{ color: '#666', lineHeight: '1.6' }}>
            There are currently no free agents available in the waiver wire.
            Check back after waivers process or when new players become available.
          </p>
        </div>
        
        <div style={{
          marginTop: '30px',
          padding: '20px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px'
        }}>
          <h4 style={{ marginBottom: '12px', color: '#333' }}>Coming Soon:</h4>
          <ul style={{ color: '#666', lineHeight: '1.8' }}>
            <li>• Real-time FAAB budget tracking</li>
            <li>• Sleeper waiver wire recommendations</li>
            <li>• Automated bid suggestions based on league settings</li>
            <li>• Integration with Sleeper's transaction system</li>
          </ul>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="screen-container">
        <div className="screen-header">
          <h1>Waiver Wire - {league?.name}</h1>
        </div>
        <div className="info-banner" style={{
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '8px',
          padding: '16px',
          marginTop: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{ fontSize: '1.5rem' }}>⚠️</span>
          <div>
            <strong>Waiver Wire Status</strong>
            <div style={{ marginTop: '4px', fontSize: '0.95rem', opacity: 0.9 }}>
              {error}
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  const handleClaimPlayer = async (playerId) => {
    try {
      // Show confirmation dialog
      const playerInfo = availablePlayers.find(p => p.id === playerId);
      if (!playerInfo) {
        alert('Player not found');
        return;
      }
      
      const confirmMessage = `Are you sure you want to claim ${playerInfo.name} (${playerInfo.position})?`;
      if (!window.confirm(confirmMessage)) {
        return;
      }
      
      // Make API call to claim player
      const response = await fetch(`http://localhost:8000/waiver-wire/claim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          league_id: league?.id || '83806',
          team_id: league?.userTeam?.id || '7',
          player_id: playerId,
          bid_amount: playerInfo.recommendedBid || 0
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Successfully submitted waiver claim for ${playerInfo.name}! ${result.message || ''}`);
        
        // Refresh the waiver wire list
        fetchAvailablePlayers();
      } else {
        const error = await response.json();
        alert(`Failed to claim player: ${error.detail || error.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error claiming player:', error);
      alert('Failed to claim player. Please try again.');
    }
  };
  
  return (
    <div className="screen-container">
      <div className="screen-header">
        <h1>Waiver Wire - {league?.name}</h1>
      </div>
      
      <div className="budget-card">
        <h3>FAAB Budget: ${faabBudget}</h3>
        <p>AI recommendations are based on player projections, team needs, and ownership percentage.</p>
        {personalizedRecommendations && (
          <button 
            className="toggle-recommendations"
            onClick={() => setShowRecommendations(!showRecommendations)}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: showRecommendations ? '#28a745' : '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {showRecommendations ? '👁️ Hide' : '👁️ Show'} Personalized Recommendations
          </button>
        )}
      </div>
      
      {showRecommendations && personalizedRecommendations && (personalizedRecommendations.team_needs || personalizedRecommendations.injury_concerns?.length > 0 || personalizedRecommendations.bye_week_alerts?.length > 0) && (
        <div className="team-needs-analysis" style={{
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h3 style={{ marginTop: 0, color: 'var(--text-primary)' }}>📊 Your Team Needs Analysis</h3>
          
          {personalizedRecommendations.team_needs.immediate?.length > 0 && (
            <div className="need-category" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#dc3545' }}>🚨 Immediate Needs (This Week):</h4>
              <ul style={{ margin: '5px 0', color: 'var(--text-secondary)' }}>
                {personalizedRecommendations.team_needs.immediate.map((need, idx) => (
                  <li key={idx}>
                    <strong style={{ color: 'var(--text-primary)' }}>{need.position}</strong>: {need.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {personalizedRecommendations.team_needs.upcoming?.length > 0 && (
            <div className="need-category" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#ffc107' }}>⚠️ Position Needs (Upcoming):</h4>
              <ul style={{ margin: '5px 0', color: 'var(--text-secondary)' }}>
                {personalizedRecommendations.team_needs.upcoming.map((need, idx) => (
                  <li key={idx}>
                    <strong style={{ color: 'var(--text-primary)' }}>{need.position}</strong>: {need.reason}
                    {need.priority && (
                      <span style={{ 
                        marginLeft: '8px',
                        backgroundColor: need.priority === 'high' ? '#dc3545' : need.priority === 'medium' ? '#ffc107' : '#28a745',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '0.75rem',
                        textTransform: 'uppercase'
                      }}>
                        {need.priority}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {personalizedRecommendations.team_needs.season_long?.length > 0 && (
            <div className="need-category" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#17a2b8' }}>📈 Season-Long Improvements:</h4>
              <ul style={{ margin: '5px 0', color: 'var(--text-secondary)' }}>
                {personalizedRecommendations.team_needs.season_long.map((need, idx) => (
                  <li key={idx}>
                    <strong style={{ color: 'var(--text-primary)' }}>{need.position}</strong>: {need.reason}
                    {need.priority && (
                      <span style={{ 
                        marginLeft: '8px',
                        backgroundColor: need.priority === 'high' ? '#dc3545' : need.priority === 'medium' ? '#ffc107' : '#28a745',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '0.75rem',
                        textTransform: 'uppercase'
                      }}>
                        {need.priority}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Show a message when there are no immediate needs but display position status */}
          {personalizedRecommendations.team_needs.immediate?.length === 0 && 
           personalizedRecommendations.team_needs.upcoming?.length === 0 &&
           personalizedRecommendations.team_needs.season_long?.length === 0 && (
            <div className="no-needs-message" style={{
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: '6px',
              padding: '12px',
              marginBottom: '15px',
              color: 'var(--text-primary)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.2rem' }}>✅</span>
                <span><strong>Your roster looks solid!</strong> No immediate position needs identified.</span>
              </div>
            </div>
          )}
          
          {personalizedRecommendations.bye_week_alerts?.length > 0 && (
            <div className="bye-week-alerts" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#ffc107' }}>📅 Upcoming Bye Weeks:</h4>
              <ul style={{ margin: '5px 0', color: 'var(--text-secondary)' }}>
                {personalizedRecommendations.bye_week_alerts.map((alert, idx) => (
                  <li key={idx} style={{ color: 'var(--text-secondary)' }}>
                    Week {alert.week}: {alert.position} ({alert.affected_players} player{alert.affected_players > 1 ? 's' : ''})
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {personalizedRecommendations.injury_concerns?.length > 0 && (
            <div className="injury-alerts" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#ff6b6b' }}>🏥 Injury Concerns:</h4>
              <ul style={{ margin: '5px 0', color: 'var(--text-secondary)' }}>
                {personalizedRecommendations.injury_concerns.map((injury, idx) => (
                  <li key={idx}>
                    <strong style={{ color: 'var(--text-primary)' }}>{injury.player_name}</strong> ({injury.position}): {injury.status}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {showRecommendations && personalizedRecommendations && personalizedRecommendations.recommendations && (
        <div className="personalized-recommendations" style={{
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          border: '1px solid rgba(76, 175, 80, 0.3)',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          color: 'var(--text-primary)'
        }}>
          <h3 style={{ marginTop: 0, color: 'var(--accent)' }}>🎯 Top Personalized Waiver Recommendations</h3>
          <div className="recommendations-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '15px',
            marginTop: '15px'
          }}>
            {personalizedRecommendations.recommendations.slice(0, 6).map((rec, idx) => (
              <div key={idx} className="recommendation-card" style={{
                backgroundColor: 'var(--card-bg)',
                padding: '15px',
                borderRadius: '6px',
                border: rec.priority === 'critical' ? '2px solid #dc3545' : 
                        rec.priority === 'high' ? '2px solid #ffc107' : '1px solid var(--border-color)',
                color: 'var(--text-primary)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, color: 'var(--text-primary)' }}>{rec.player_name}</h4>
                  <span style={{
                    backgroundColor: rec.priority === 'critical' ? '#dc3545' : 
                                    rec.priority === 'high' ? '#ffc107' : 
                                    rec.priority === 'medium' ? '#17a2b8' : '#6c757d',
                    color: 'white',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    textTransform: 'uppercase'
                  }}>
                    {rec.priority}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '5px' }}>
                  {rec.position} • {rec.type.replace('_', ' ')}
                </div>
                <p style={{ marginTop: '10px', marginBottom: '10px', color: 'var(--text-secondary)' }}>{rec.reasoning}</p>
                {rec.drop_candidate && (
                  <div style={{
                    backgroundColor: '#fff3cd',
                    padding: '8px',
                    borderRadius: '4px',
                    fontSize: '0.9rem',
                    color: '#856404'  // Amber text for drop warning
                  }}>
                    💱 Drop: {rec.drop_candidate.name} ({rec.drop_candidate.position})
                  </div>
                )}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginTop: '10px',
                  fontSize: '0.85rem'
                }}>
                  <span>Confidence: {rec.confidence_score}%</span>
                  <span>Timeline: {rec.timeline}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="position-filter">
        <label>Filter by Position: </label>
        <select value={positionFilter} onChange={(e) => setPositionFilter(e.target.value)}>
          <option value="">All Positions</option>
          <option value="QB">QB</option>
          <option value="RB">RB</option>
          <option value="WR">WR</option>
          <option value="TE">TE</option>
          <option value="K">K</option>
          <option value="DEF">DEF</option>
        </select>
      </div>
      
      <div className="players-grid">
        {availablePlayers.length === 0 ? (
          <div className="empty-state" style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '40px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '12px',
            marginTop: '20px',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🏃</div>
            <h3 style={{ color: 'var(--text-primary)' }}>No Waiver Wire Players Available</h3>
            <p style={{ color: 'var(--text-secondary)' }}>Check back later for available free agents in {league?.name}.</p>
          </div>
        ) : (
          availablePlayers.map(player => (
          <WaiverClaimCard 
            key={player.id} 
            player={player}  // Pass all player data
            platform={league?.platform}
            onClaim={handleClaimPlayer}
            faabBudget={faabBudget}
          />
          )))}
      </div>
    </div>
  );
};

export default WaiverWire;