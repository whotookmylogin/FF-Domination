import React from 'react';
import './NewsCard.css';

const NewsCard = ({ newsItem }) => {
  const getUrgencyColor = (urgency) => {
    if (urgency >= 4) return '#F44336';  // High urgency (4-5)
    if (urgency >= 3) return '#FF9800';  // Medium urgency (3)
    return '#4CAF50';  // Low urgency (1-2)
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

  const handleReadMore = () => {
    if (newsItem.url || newsItem.link) {
      window.open(newsItem.url || newsItem.link, '_blank', 'noopener,noreferrer');
    } else {
      console.log('No article URL available');
    }
  };

  const getRelevanceColor = (score) => {
    if (score >= 8) return '#4CAF50';
    if (score >= 5) return '#2196F3';
    if (score >= 3) return '#FF9800';
    return '#9E9E9E';
  };

  // Format bullet points if present
  const formatBulletPoints = (text) => {
    if (!text) return 'No summary available.';
    
    // Check if it's already formatted with bullet points
    if (text.includes('•')) {
      return text.split('•')
        .filter(point => point.trim())
        .map(point => `• ${point.trim()}`)
        .join('\n');
    }
    
    // Otherwise return as is
    return text;
  };

  const summaryContent = newsItem.enhanced_tldr || newsItem.tldr || newsItem.summary;

  return (
    <div className="card news-card">
      <div className="news-header">
        <h3 className="news-title">{newsItem.title || 'Untitled News'}</h3>
      </div>
      
      {summaryContent && (
        <div className="tldr-section">
          <div className="tldr-content" style={{ whiteSpace: 'pre-line' }}>
            {formatBulletPoints(summaryContent)}
          </div>
          
          {newsItem.personalized_summary && (
            <div className="personalized-impact">
              <strong>Impact on Your Team:</strong>
              <span>{newsItem.personalized_summary}</span>
              {newsItem.affected_players && newsItem.affected_players.length > 0 && (
                <div className="affected-players">
                  <em>Affects: {newsItem.affected_players.join(', ')}</em>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      <div className="news-actions">
        <button 
          className="read-more-btn"
          onClick={handleReadMore}
          style={{
            cursor: newsItem.url || newsItem.link ? 'pointer' : 'not-allowed',
            opacity: newsItem.url || newsItem.link ? 1 : 0.5
          }}
        >
          Read Full Article →
        </button>
      </div>
    </div>
  );
};

export default NewsCard;
