import React from 'react';
import './TradeSuggestionCard.css';

const TradeSuggestionCard = ({ suggestion }) => {
  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'high': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  // Handle undefined suggestion
  if (!suggestion) {
    return (
      <div className="card">
        <div className="trade-header">
          <h3>Trade Suggestion</h3>
        </div>
        <p>No trade suggestions available at this time.</p>
      </div>
    );
  }

  // Handle undefined riskLevel for charAt error
  const riskLevel = suggestion.riskLevel || 'medium';

  return (
    <div className="card trade-suggestion-card">
      <div className="trade-header">
        <h3>Trade Suggestion</h3>
        <span 
          className="risk-indicator" 
          style={{ color: getRiskColor(riskLevel) }}
        >
          Risk: {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)}
        </span>
      </div>
      
      <div className="trade-players">
        <div className="player-section">
          <h4>Receive</h4>
          <div className="player-info">
            <div className="player-name">{suggestion.playerIn?.name || 'Unknown Player'}</div>
            <div className="player-details">
              {suggestion.playerIn?.position || 'N/A'} - {suggestion.playerIn?.team || 'N/A'}
            </div>
            <div className="player-projection">
              Proj: {suggestion.playerIn?.projectedPoints !== undefined ? suggestion.playerIn.projectedPoints + ' pts' : 'N/A'}
            </div>
          </div>
        </div>
        
        <div className="trade-arrow">↔</div>
        
        <div className="player-section">
          <h4>Give Up</h4>
          <div className="player-info">
            <div className="player-name">{suggestion.playerOut?.name || 'Unknown Player'}</div>
            <div className="player-details">
              {suggestion.playerOut?.position || 'N/A'} - {suggestion.playerOut?.team || 'N/A'}
            </div>
            <div className="player-projection">
              Proj: {suggestion.playerOut?.projectedPoints !== undefined ? suggestion.playerOut.projectedPoints + ' pts' : 'N/A'}
            </div>
          </div>
        </div>
      </div>
      
      <div className="value-improvement">
        <span>Value Improvement: </span>
        <span className={suggestion.valueImprovement > 0 ? 'positive' : 'negative'}>
          {suggestion.valueImprovement > 0 ? '+' : ''}{suggestion.valueImprovement !== undefined ? suggestion.valueImprovement + '%' : 'N/A'}
        </span>
      </div>
      
      <div className="trade-actions">
        <button className="accept-btn">Accept Suggestion</button>
        <button className="decline-btn">Decline</button>
        <button className="counter-btn">Counter Offer</button>
      </div>
    </div>
  );
};

export default TradeSuggestionCard;
