import React, { useState, useEffect } from 'react';
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
  
  useEffect(() => {
    const fetchAvailablePlayers = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Use current league context
        const leagueId = league?.id;
        const platform = league?.platform;
        const teamId = league?.teamId || '1'; // Get user's team ID from league context
        
        if (!leagueId || !platform) {
          setError('No league selected');
          setAvailablePlayers([]);
          setLoading(false);
          return;
        }
        
        // Fetch both standard waiver data and enhanced analysis
        const [waiverData, enhancedAnalysis] = await Promise.all([
          getWaiverWirePlayers(leagueId, positionFilter || null),
          getEnhancedWaiverAnalysis(leagueId, teamId, platform, currentWeek)
        ]);
        
        const data = waiverData;
        
        // Process enhanced recommendations
        if (enhancedAnalysis.status === 'success' && enhancedAnalysis.recommendations) {
          setPersonalizedRecommendations(enhancedAnalysis);
        }
        
        if (data.status === 'success' && data.free_agents) {
          // Format the data for display
          const formattedPlayers = data.free_agents.map((player, index) => ({
            id: player.player_id || index,
            name: player.name,
            position: player.position,
            team: player.team,
            projectedPoints: player.projected_points || 0,
            newsUrgency: Math.min(5, Math.max(1, Math.floor(player.recommendation_score / 20))),
            bidRecommendation: player.bid_recommendation,
            recommendedBid: player.recommended_bid,
            percentOwned: player.percent_owned || 0,
            injuryStatus: player.injury_status || 'Active'
          }));
          
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
    };
    
    if (league) {
      fetchAvailablePlayers();
    }
  }, [league, positionFilter]);
  
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
      
      {showRecommendations && personalizedRecommendations && personalizedRecommendations.team_needs && (
        <div className="team-needs-analysis" style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h3 style={{ marginTop: 0 }}>📊 Your Team Needs Analysis</h3>
          
          {personalizedRecommendations.team_needs.immediate?.length > 0 && (
            <div className="need-category" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#dc3545' }}>🚨 Immediate Needs (This Week):</h4>
              <ul style={{ margin: '5px 0' }}>
                {personalizedRecommendations.team_needs.immediate.map((need, idx) => (
                  <li key={idx}>
                    <strong>{need.position}</strong>: {need.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {personalizedRecommendations.bye_week_alerts?.length > 0 && (
            <div className="bye-week-alerts" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#ffc107' }}>📅 Upcoming Bye Weeks:</h4>
              <ul style={{ margin: '5px 0' }}>
                {personalizedRecommendations.bye_week_alerts.map((alert, idx) => (
                  <li key={idx}>
                    Week {alert.week}: {alert.position} ({alert.affected_players} player{alert.affected_players > 1 ? 's' : ''})
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {personalizedRecommendations.injury_concerns?.length > 0 && (
            <div className="injury-alerts" style={{ marginBottom: '15px' }}>
              <h4 style={{ color: '#ff6b6b' }}>🏥 Injury Concerns:</h4>
              <ul style={{ margin: '5px 0' }}>
                {personalizedRecommendations.injury_concerns.map((injury, idx) => (
                  <li key={idx}>
                    <strong>{injury.player_name}</strong> ({injury.position}): {injury.status}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {showRecommendations && personalizedRecommendations && personalizedRecommendations.recommendations && (
        <div className="personalized-recommendations" style={{
          backgroundColor: '#e8f5e9',
          border: '1px solid #4caf50',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          color: '#333'  // Fix white text on light background
        }}>
          <h3 style={{ marginTop: 0, color: '#2e7d32' }}>🎯 Top Personalized Waiver Recommendations</h3>
          <div className="recommendations-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '15px',
            marginTop: '15px'
          }}>
            {personalizedRecommendations.recommendations.slice(0, 6).map((rec, idx) => (
              <div key={idx} className="recommendation-card" style={{
                backgroundColor: 'white',
                padding: '15px',
                borderRadius: '6px',
                border: rec.priority === 'critical' ? '2px solid #dc3545' : 
                        rec.priority === 'high' ? '2px solid #ffc107' : '1px solid #dee2e6',
                color: '#333'  // Fix white text on white background
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, color: '#333' }}>{rec.player_name}</h4>
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
                <p style={{ marginTop: '10px', marginBottom: '10px', color: '#333' }}>{rec.reasoning}</p>
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
        </select>
      </div>
      
      <div className="players-grid">
        {availablePlayers.length === 0 ? (
          <div className="empty-state" style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '40px',
            backgroundColor: '#f8f9fa',
            borderRadius: '12px',
            marginTop: '20px',
            color: '#333'  // Fix white text on light background
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🏃</div>
            <h3>No Waiver Wire Players Available</h3>
            <p>Check back later for available free agents in {league?.name}.</p>
          </div>
        ) : (
          availablePlayers.map(player => (
          <WaiverClaimCard 
            key={player.id} 
            player={{
              id: player.id,
              name: player.name,
              position: player.position,
              team: player.team,
              projectedPoints: player.projectedPoints,
              injuryStatus: player.injuryStatus || 'Active',
              addPercentage: player.percentOwned || (player.newsUrgency * 15)
            }}
            onClaim={(playerId) => console.log(`Claiming player ${playerId}`)}
            faabBudget={faabBudget}
            recommendedBid={player.recommendedBid}
            bidRecommendation={player.bidRecommendation}
          />
          )))}
      </div>
    </div>
  );
};

export default WaiverWire;