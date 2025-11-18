import React from 'react';
import './NewsCard.css';

const NewsCard = ({ newsItem }) => {
  const getUrgencyColor = (urgency) => {
    if (urgency >= 8) return '#F44336';
    if (urgency >= 5) return '#FF9800';
    return '#4CAF50';
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Handle undefined newsItem
  if (!newsItem) {
    return (
      <div className="card">
        <div className="news-header">
          <h3 className="news-title">No news available</h3>
        </div>
        <p className="news-summary">No news items to display at this time.</p>
      </div>
    );
  }

  return (
    <div className="card news-card">
      <div className="news-header">
        <h3 className="news-title">{newsItem.title || 'Untitled News'}</h3>
        <span 
          className="urgency-indicator" 
          style={{ color: getUrgencyColor(newsItem.urgency || 0) }}
        >
          Urgency: {(newsItem.urgency || 0)}/10
        </span>
      </div>
      
      <div className="news-meta">
        <span className="source">{newsItem.source || 'Unknown Source'}</span>
        <span className="timestamp">{newsItem.timestamp ? formatDate(newsItem.timestamp) : 'Unknown Time'}</span>
      </div>
      
      <p className="news-summary">{newsItem.summary || 'No summary available.'}</p>
      
      <div className="news-actions">
        <button className="read-more-btn">Read Full Article</button>
      </div>
    </div>
  );
};

export default NewsCard;
