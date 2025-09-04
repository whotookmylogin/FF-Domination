/**
 * Modern Player Card Component
 * Inspired by Sleeper's clean design with comprehensive player information
 * Features player images, stats, injury status, and interactive elements
 */
import React, { useState } from 'react';
import './PlayerCard.css';

const PlayerCard = ({ 
  player, 
  showStats = true, 
  showActions = false,
  compact = false,
  onClick = null,
  onAnalyze = null,
  onTrade = null
}) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  /**
   * Get player headshot URL from multiple sources
   * Prioritizes ESPN, falls back to Fantasy Nerds, then placeholder
   */
  const getPlayerImageUrl = (player) => {
    if (imageError) {
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name || 'Player')}&background=2d3748&color=ffffff&size=120&font-size=0.4`;
    }
    
    // Skip invalid ESPN IDs (negative numbers or special values)
    if (player.espn_id && player.espn_id > 0) {
      return `https://a.espncdn.com/i/headshots/nfl/players/full/${player.espn_id}.png`;
    }
    
    // Skip invalid player IDs
    if (player.player_id && player.player_id > 0) {
      return `https://www.fantasynerds.com/images/nfl/players_medium/${player.player_id}.png`;
    }
    
    // Final fallback to generated avatar
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name || 'Player')}&background=2d3748&color=ffffff&size=120&font-size=0.4`;
  };

  /**
   * Get injury status configuration
   */
  const getInjuryStatus = (status) => {
    const statusMap = {
      'ACTIVE': { label: 'Active', class: 'status-active', color: '#48bb78' },
      'QUESTIONABLE': { label: 'Q', class: 'status-questionable', color: '#ed8936' },
      'DOUBTFUL': { label: 'D', class: 'status-doubtful', color: '#dd6b20' },
      'OUT': { label: 'OUT', class: 'status-out', color: '#f56565' },
      'IR': { label: 'IR', class: 'status-ir', color: '#9f7aea' },
      'PUP': { label: 'PUP', class: 'status-pup', color: '#9f7aea' },
      'SUSPENDED': { label: 'SUSP', class: 'status-suspended', color: '#e53e3e' }
    };
    
    return statusMap[status] || statusMap['ACTIVE'];
  };

  /**
   * Get position color based on position type
   */
  const getPositionColor = (position) => {
    const positionColors = {
      'QB': '#ff6b6b',
      'RB': '#4ecdc4', 
      'WR': '#45b7d1',
      'TE': '#f9ca24',
      'K': '#6c5ce7',
      'D/ST': '#fd79a8',
      'DEF': '#fd79a8',
      'FLEX': '#fdcb6e'
    };
    
    return positionColors[position] || '#718096';
  };

  /**
   * Format player statistics for display
   */
  const formatStats = (player) => {
    const stats = [];
    
    if (player.points_total) {
      stats.push({ label: 'Points', value: player.points_total.toFixed(1) });
    }
    
    if (player.projected_points) {
      stats.push({ label: 'Proj.', value: player.projected_points.toFixed(1) });
    }
    
    if (player.avg_points) {
      stats.push({ label: 'Avg', value: player.avg_points.toFixed(1) });
    }
    
    if (player.games_played) {
      stats.push({ label: 'GP', value: player.games_played });
    }
    
    return stats;
  };

  const injuryStatus = getInjuryStatus(player.injury_status || 'ACTIVE');
  const stats = formatStats(player);
  const positionColor = getPositionColor(player.position);

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  const handleCardClick = () => {
    if (onClick) {
      onClick(player);
    }
  };

  if (compact) {
    return (
      <div 
        className={`player-card-compact ${onClick ? 'clickable' : ''}`}
        onClick={handleCardClick}
      >
        <div className="player-image-small">
          {imageLoading && <div className="loading-shimmer image-placeholder-small"></div>}
          <img 
            src={getPlayerImageUrl(player)}
            alt={player.name}
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{ display: imageLoading ? 'none' : 'block' }}
          />
        </div>
        
        <div className="player-info-compact">
          <div className="player-name-compact">{player.name}</div>
          <div className="player-team-pos">
            {player.team} • 
            <span 
              className="position-badge-small"
              style={{ backgroundColor: positionColor }}
            >
              {player.position}
            </span>
          </div>
        </div>
        
        <div className="injury-status-compact">
          <span 
            className={`injury-badge ${injuryStatus.class}`}
            style={{ backgroundColor: injuryStatus.color }}
          >
            {injuryStatus.label}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`player-card ${onClick ? 'clickable' : ''}`}
      onClick={handleCardClick}
    >
      {/* Player Header */}
      <div className="player-header">
        <div className="player-image-container">
          {imageLoading && <div className="loading-shimmer image-placeholder"></div>}
          <img 
            src={getPlayerImageUrl(player)}
            alt={player.name}
            className="player-image"
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{ display: imageLoading ? 'none' : 'block' }}
          />
          
          {/* Position Badge */}
          <div 
            className="position-badge"
            style={{ backgroundColor: positionColor }}
          >
            {player.position}
          </div>
        </div>
        
        <div className="player-info">
          <h3 className="player-name">{player.name}</h3>
          <div className="player-team">{player.team}</div>
          
          {/* Injury Status */}
          <div className="status-container">
            <span 
              className={`injury-status ${injuryStatus.class}`}
              style={{ backgroundColor: injuryStatus.color }}
            >
              {injuryStatus.label}
            </span>
          </div>
        </div>
      </div>

      {/* Player Stats */}
      {showStats && stats.length > 0 && (
        <div className="player-stats">
          {stats.map((stat, index) => (
            <div key={index} className="stat-item">
              <span className="stat-value">{stat.value}</span>
              <span className="stat-label">{stat.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      {showActions && (
        <div className="player-actions">
          {onAnalyze && (
            <button 
              className="btn btn-sm btn-secondary"
              onClick={(e) => {
                e.stopPropagation();
                onAnalyze(player);
              }}
            >
              📊 Analyze
            </button>
          )}
          {onTrade && (
            <button 
              className="btn btn-sm btn-primary"
              onClick={(e) => {
                e.stopPropagation();
                onTrade(player);
              }}
            >
              🔄 Trade
            </button>
          )}
        </div>
      )}

      {/* Additional Player Metrics */}
      {player.rank && (
        <div className="player-rank">
          <span className="rank-label">Rank:</span>
          <span className="rank-value">#{player.rank}</span>
        </div>
      )}
    </div>
  );
};

export default PlayerCard;