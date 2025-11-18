import React, { useState, useEffect } from 'react';
import './IntelligentNotifications.css';

const IntelligentNotifications = ({ league, user }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, urgent, strategic
  
  useEffect(() => {
    if (league?.userTeam?.id && league?.id) {
      fetchIntelligentNotifications();
      // Refresh every 30 minutes
      const interval = setInterval(fetchIntelligentNotifications, 30 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [league]);
  
  const fetchIntelligentNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8000/news/intelligent-notifications/${league.userTeam.id}?league_id=${league.id}`
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setNotifications(data.data || []);
        }
      } else {
        // Fallback to advanced monitoring endpoint
        const advancedResponse = await fetch('http://localhost:8000/news/advanced/monitor');
        if (advancedResponse.ok) {
          const advancedData = await advancedResponse.json();
          // Convert to notification format
          const convertedNotifs = convertToNotifications(advancedData.data || []);
          setNotifications(convertedNotifs);
        }
      }
    } catch (err) {
      console.error('Error fetching notifications:', err);
      setError('Unable to fetch notifications');
    } finally {
      setLoading(false);
    }
  };
  
  const convertToNotifications = (newsItems) => {
    return newsItems.map((item, index) => ({
      id: `news_${index}`,
      type: getNotificationType(item.impact_level),
      priority: getPriority(item.impact_level),
      title: item.title,
      message: item.strategic_analysis || item.content.substring(0, 200),
      timestamp: item.timestamp,
      confidence: `${(item.fantasy_relevance_score * 10)}%`,
      source: item.source,
      actions: item.recommendation ? [{
        action: item.recommendation,
        description: getActionDescription(item.recommendation)
      }] : []
    }));
  };
  
  const getNotificationType = (impactLevel) => {
    switch (impactLevel) {
      case 'critical': return 'injury_alert';
      case 'high': return 'waiver_opportunity';
      case 'medium': return 'value_change';
      default: return 'lineup_change';
    }
  };
  
  const getPriority = (impactLevel) => {
    switch (impactLevel) {
      case 'critical': return 'URGENT';
      case 'high': return 'HIGH';
      case 'medium': return 'MEDIUM';
      default: return 'LOW';
    }
  };
  
  const getActionDescription = (recommendation) => {
    const descriptions = {
      'pickup_immediate': 'Add this player immediately',
      'pickup_strategic': 'Add to block opponents',
      'trade_target': 'Target for trade',
      'trade_away': 'Trade while value is high',
      'hold': 'Monitor situation',
      'drop_candidate': 'Consider dropping',
      'opponent_recommendation': 'Suggest to opponent for strategic advantage'
    };
    return descriptions[recommendation] || 'Take action';
  };
  
  const handleAction = async (notification, action) => {
    console.log('Handling action:', action, 'for notification:', notification);
    // TODO: Implement action handling (e.g., navigate to waiver wire, trade screen, etc.)
  };
  
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'URGENT': return '#dc3545';
      case 'HIGH': return '#fd7e14';
      case 'MEDIUM': return '#ffc107';
      case 'LOW': return '#28a745';
      default: return '#6c757d';
    }
  };
  
  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'URGENT': return '🚨';
      case 'HIGH': return '⚠️';
      case 'MEDIUM': return '📢';
      case 'LOW': return 'ℹ️';
      default: return '📌';
    }
  };
  
  const filteredNotifications = notifications.filter(notif => {
    if (filter === 'all') return true;
    if (filter === 'urgent') return notif.priority === 'URGENT' || notif.priority === 'HIGH';
    if (filter === 'strategic') return notif.type === 'strategic_block' || notif.type === 'opponent_weakness';
    return true;
  });
  
  if (loading) {
    return (
      <div className="intelligent-notifications loading">
        <div className="loading-spinner">⏳</div>
        <p>Analyzing news and generating recommendations...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="intelligent-notifications error">
        <p>{error}</p>
        <button onClick={fetchIntelligentNotifications}>Retry</button>
      </div>
    );
  }
  
  return (
    <div className="intelligent-notifications">
      <div className="notifications-header">
        <h3>🧠 Intelligent Notifications</h3>
        <p className="subtitle">AI-powered insights checking 4x daily across all sources</p>
        
        <div className="notification-filters">
          <button 
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({notifications.length})
          </button>
          <button 
            className={`filter-btn ${filter === 'urgent' ? 'active' : ''}`}
            onClick={() => setFilter('urgent')}
          >
            Urgent ({notifications.filter(n => n.priority === 'URGENT' || n.priority === 'HIGH').length})
          </button>
          <button 
            className={`filter-btn ${filter === 'strategic' ? 'active' : ''}`}
            onClick={() => setFilter('strategic')}
          >
            Strategic ({notifications.filter(n => n.type === 'strategic_block' || n.type === 'opponent_weakness').length})
          </button>
        </div>
      </div>
      
      <div className="notifications-list">
        {filteredNotifications.length === 0 ? (
          <div className="no-notifications">
            <p>No new notifications at this time.</p>
            <p className="hint">We're monitoring training camps, signings, and injuries 24/7</p>
          </div>
        ) : (
          filteredNotifications.map(notification => (
            <div 
              key={notification.id} 
              className={`notification-card priority-${notification.priority.toLowerCase()}`}
              style={{ borderLeftColor: getPriorityColor(notification.priority) }}
            >
              <div className="notification-header">
                <span className="priority-icon">{getPriorityIcon(notification.priority)}</span>
                <h4>{notification.title}</h4>
                <span className="notification-time">
                  {new Date(notification.timestamp).toLocaleTimeString()}
                </span>
              </div>
              
              <div className="notification-body">
                <p>{notification.message}</p>
                
                {notification.confidence && (
                  <div className="confidence-score">
                    Confidence: <strong>{notification.confidence}</strong>
                  </div>
                )}
                
                {notification.source && (
                  <div className="notification-source">
                    Source: {notification.source}
                  </div>
                )}
              </div>
              
              {notification.actions && notification.actions.length > 0 && (
                <div className="notification-actions">
                  {notification.actions.map((action, idx) => (
                    <button
                      key={idx}
                      className="action-btn"
                      onClick={() => handleAction(notification, action)}
                    >
                      {action.description}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      <div className="notifications-footer">
        <p className="monitoring-status">
          Monitoring: ESPN, NFL.com, Rotoworld, FantasyPros, Sleeper, X/Twitter experts
        </p>
        <p className="last-check">
          Next check in: {getNextCheckTime()}
        </p>
      </div>
    </div>
  );
  
  function getNextCheckTime() {
    const now = new Date();
    const nextCheck = new Date(now);
    
    // Check every 6 hours (4x daily)
    const checkHours = [0, 6, 12, 18];
    const currentHour = now.getHours();
    
    let nextHour = checkHours.find(h => h > currentHour);
    if (!nextHour) {
      nextHour = checkHours[0];
      nextCheck.setDate(nextCheck.getDate() + 1);
    }
    
    nextCheck.setHours(nextHour, 0, 0, 0);
    
    const timeDiff = nextCheck - now;
    const hours = Math.floor(timeDiff / (1000 * 60 * 60));
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }
};

export default IntelligentNotifications;