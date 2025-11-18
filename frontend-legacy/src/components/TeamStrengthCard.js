import React from 'react';
import './TeamStrengthCard.css';

const TeamStrengthCard = ({ teamStrength }) => {
  const getStrengthColor = (strength) => {
    if (strength >= 80) return '#4CAF50';
    if (strength >= 60) return '#8BC34A';
    if (strength >= 40) return '#FF9800';
    return '#F44336';
  };

  const getStrengthLabel = (strength) => {
    if (strength >= 80) return 'Elite';
    if (strength >= 60) return 'Strong';
    if (strength >= 40) return 'Average';
    return 'Weak';
  };

  // Handle undefined teamStrength
  if (!teamStrength) {
    return (
      <div className="card">
        <div className="strength-header">
          <h3>Team Strength Analysis</h3>
        </div>
        <p>No team strength data available.</p>
      </div>
    );
  }

  return (
    <div className="card team-strength-card">
      <div className="strength-header">
        <h3>{teamStrength.name || 'Unknown Team'} Strength Analysis</h3>
        <div className="rank-info">
          Rank: {teamStrength.rank !== undefined ? teamStrength.rank : 'N/A'}/{teamStrength.totalTeams !== undefined ? teamStrength.totalTeams : 'N/A'}
        </div>
      </div>
      
      <div className="overall-strength">
        <div className="strength-value" style={{ color: getStrengthColor(teamStrength.strength) }}>
          {teamStrength.strength !== undefined ? teamStrength.strength + '%' : 'N/A'}
        </div>
        <div className="strength-label" style={{ color: getStrengthColor(teamStrength.strength) }}>
          {teamStrength.strength !== undefined ? getStrengthLabel(teamStrength.strength) : 'N/A'}
        </div>
      </div>
      
      <div className="strength-details">
        <div className="strengths-section">
          <h4>Strengths</h4>
          <ul>
            {teamStrength.strengths && teamStrength.strengths.length > 0 ? (
              teamStrength.strengths.map((strength, index) => (
                <li key={index}>{strength}</li>
              ))
            ) : (
              <li>No strengths data available</li>
            )}
          </ul>
        </div>
        
        <div className="weaknesses-section">
          <h4>Weaknesses</h4>
          <ul>
            {teamStrength.weaknesses && teamStrength.weaknesses.length > 0 ? (
              teamStrength.weaknesses.map((weakness, index) => (
                <li key={index}>{weakness}</li>
              ))
            ) : (
              <li>No weaknesses data available</li>
            )}
          </ul>
        </div>
      </div>
      
      <div className="improvement-suggestions">
        <h4>Improvement Suggestions</h4>
        <p>Focus on addressing weaknesses through trades or waiver wire pickups.</p>
      </div>
    </div>
  );
};

export default TeamStrengthCard;
