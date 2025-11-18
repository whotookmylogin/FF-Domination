import React, { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';
import './NewsFeed.css';

const NewsFeed = ({ league }) => {
  const [newsItems, setNewsItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch real news from backend
        const response = await fetch('http://localhost:8000/news/aggregated');
        const data = await response.json();
        
        if (data.status === 'success' && data.news && data.news.length > 0) {
          setNewsItems(data.news);
        } else {
          setNewsItems([]);
          setError('No news articles available at this time.');
        }
      } catch (err) {
        console.error('Error fetching news:', err);
        setNewsItems([]);
        setError('Unable to fetch news. Please check your connection and try again.');
      } finally {
        setLoading(false);
      }
    };
    
    if (league) {
      fetchNews();
    }
  }, [league]);
  
  const filteredNews = newsItems.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'breaking') return item.urgency >= 4;
    if (filter === 'high') return item.urgency === 5;
    return true;
  });
  
  if (loading) {
    return <div className="screen-container">Loading news feed...</div>;
  }
  
  return (
    <div className="screen-container">
      <div className="screen-header">
        <h1>News Feed - {league?.name}</h1>
      </div>
      
      <div className="news-controls">
        <div className="filter-buttons">
          <button 
            className={filter === 'all' ? 'active' : ''} 
            onClick={() => setFilter('all')}
          >
            All News
          </button>
          <button 
            className={filter === 'breaking' ? 'active' : ''} 
            onClick={() => setFilter('breaking')}
          >
            Breaking (4-5)
          </button>
          <button 
            className={filter === 'high' ? 'active' : ''} 
            onClick={() => setFilter('high')}
          >
            High Urgency (5)
          </button>
        </div>
      </div>
      
      {error && (
        <div className="info-banner" style={{
          backgroundColor: '#fff3cd',
          color: '#856404',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span style={{ fontSize: '20px' }}>📰</span>
          <div>
            <strong>News Feed Status</strong>
            <div style={{ fontSize: '14px', marginTop: '5px' }}>{error}</div>
          </div>
        </div>
      )}
      
      {filteredNews.length === 0 && !error && (
        <div className="empty-state" style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📰</div>
          <h3>No News Articles Available</h3>
          <p>Check back later for the latest fantasy football news.</p>
        </div>
      )}
      
      {filteredNews.length > 0 && (
        <div className="news-grid">
          {filteredNews.map(item => (
            <NewsCard key={item.id} newsItem={item} />
          ))}
        </div>
      )}
    </div>
  );
};

export default NewsFeed;