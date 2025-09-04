import React, { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';
import './NewsFeed.css';

const NewsFeed = ({ league }) => {
  const [newsItems, setNewsItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  
  const getCacheKey = () => {
    if (league && league.id && league.team_id) {
      return `news_feed_${league.id}_${league.team_id}`;
    }
    return 'news_feed_aggregated';
  };

  const loadFromCache = () => {
    const cacheKey = getCacheKey();
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      const cacheAge = Date.now() - timestamp;
      // Cache valid for 5 minutes
      if (cacheAge < 5 * 60 * 1000) {
        setNewsItems(data);
        setLastUpdated(new Date(timestamp));
        return true;
      }
    }
    return false;
  };

  const saveToCache = (data) => {
    const cacheKey = getCacheKey();
    const cacheData = {
      data,
      timestamp: Date.now()
    };
    localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    setLastUpdated(new Date());
  };

  const fetchNews = async (forceRefresh = false) => {
    // Try cache first unless forcing refresh
    if (!forceRefresh && loadFromCache()) {
      setLoading(false);
      return;
    }

    setError(null);
    if (forceRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
      
      try {
        // Try to fetch personalized news first
        let data;
        if (league && league.id && league.team_id) {
          const platform = league.platform || 'espn';
          const personalizedUrl = `http://localhost:8000/news/personalized/${league.team_id}?league_id=${league.id}&platform=${platform}`;
          
          try {
            const personalizedResponse = await fetch(personalizedUrl);
            data = await personalizedResponse.json();
          } catch (personalizedError) {
            console.log('Falling back to aggregated news');
            // Fallback to aggregated news
            const response = await fetch('http://localhost:8000/news/aggregated');
            data = await response.json();
          }
        } else {
          // No league info, fetch aggregated news
          const response = await fetch('http://localhost:8000/news/aggregated');
          data = await response.json();
        }
        
        let newsData = [];
        if (data.status === 'success' && data.data && data.data.length > 0) {
          newsData = data.data;
        } else if (data.news && data.news.length > 0) {
          // Fallback for old API format
          newsData = data.news;
        } else {
          setError('No news articles available at this time.');
        }
        
        setNewsItems(newsData);
        if (newsData.length > 0) {
          saveToCache(newsData);
        }
      } catch (err) {
        console.error('Error fetching news:', err);
        setNewsItems([]);
        setError('Unable to fetch news. Please check your connection and try again.');
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
  };

  const handleRefresh = () => {
    fetchNews(true);
  };
    
  useEffect(() => {
    if (league) {
      fetchNews();
    }
  }, [league]);
  
  const filteredNews = newsItems.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'breaking') return (item.urgency_score || item.urgency) >= 4;
    if (filter === 'high') return (item.urgency_score || item.urgency) === 5;
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
        <div className="refresh-section">
          {lastUpdated && (
            <span className="last-updated">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button 
            className={`refresh-button ${refreshing ? 'loading' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/>
              </svg> Refreshing...</>
            ) : (
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/>
              </svg> Refresh</>
            )}
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