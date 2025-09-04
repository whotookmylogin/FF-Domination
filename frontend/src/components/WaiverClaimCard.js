import React from 'react';
import './WaiverClaimCard.css';

const WaiverClaimCard = ({ player, onClaim, faabBudget, platform }) => {
  const getStatusColor = (status) => {
    // Ensure status is a string before calling toLowerCase
    const statusStr = String(status || 'Active');
    switch (statusStr.toLowerCase()) {
      case 'questionable': return '#FF9800';
      case 'doubtful': return '#F44336';
      case 'out': return '#F44336';
      case 'ir': return '#9C27B0';
      default: return '#4CAF50';
    }
  };

  // Handle undefined player
  if (!player) {
    return (
      <div className="card">
        <div className="player-header">
          <h3>No player data available</h3>
        </div>
        <p>No player information to display.</p>
      </div>
    );
  }

  return (
    <div className="card waiver-claim-card">
      <div className="player-header">
        <h3>{player.name || 'Unknown Player'}</h3>
        <span 
          className="injury-status" 
          style={{ color: getStatusColor(player.injuryStatus) }}
        >
          {player.injuryStatus || 'Active'}
        </span>
      </div>
      
      <div className="player-details">
        <div className="detail-item">
          <span className="detail-label">Position:</span>
          <span className="detail-value">{player.position || 'N/A'}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Team:</span>
          <span className="detail-value">{player.team || 'N/A'}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Projected Points:</span>
          <span className="detail-value">{player.projectedPoints !== undefined ? player.projectedPoints : 'N/A'}</span>
        </div>
        
        {/* Platform-specific fields */}
        {platform?.toLowerCase() === 'sleeper' ? (
          <>
            {player.age && (
              <div className="detail-item">
                <span className="detail-label">Age:</span>
                <span className="detail-value">{player.age}</span>
              </div>
            )}
            {player.yearsExp !== undefined && (
              <div className="detail-item">
                <span className="detail-label">Experience:</span>
                <span className="detail-value">{player.yearsExp} years</span>
              </div>
            )}
            {player.recommendedFAAB && (
              <div className="detail-item">
                <span className="detail-label">Recommended FAAB:</span>
                <span className="detail-value" style={{ fontWeight: 'bold', color: '#2196f3' }}>
                  {player.recommendedFAAB}
                </span>
              </div>
            )}
          </>
        ) : (
          <>
            <div className="detail-item">
              <span className="detail-label">Add Percentage:</span>
              <span className="detail-value">{player.percentOwned !== undefined ? player.percentOwned + '%' : 'N/A'}</span>
            </div>
            {player.recommendedBid !== undefined && (
              <div className="detail-item">
                <span className="detail-label">Recommended Priority:</span>
                <span className="detail-value">{player.recommendedBid}</span>
              </div>
            )}
          </>
        )}
        
        {player.bidRecommendation && (
          <div className="detail-item">
            <span className="detail-label">Recommendation:</span>
            <span className="detail-value" style={{ 
              fontWeight: 'bold',
              color: player.bidRecommendation === 'HIGH PRIORITY' || player.bidRecommendation === 'CLAIM' ? '#4CAF50' : 
                     player.bidRecommendation === 'MODERATE' || player.bidRecommendation === 'WATCH' ? '#FF9800' : '#666'
            }}>
              {player.bidRecommendation}
            </span>
          </div>
        )}
      </div>
      
      <div className="waiver-actions">
        <button 
          className="claim-btn"
          onClick={() => onClaim && onClaim(player.id || '')}
          disabled={faabBudget !== undefined && faabBudget < 1}
        >
          Claim Player
        </button>
        <div className="faab-info">
          {faabBudget !== undefined && (
            <span>FAAB: ${faabBudget}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default WaiverClaimCard;
