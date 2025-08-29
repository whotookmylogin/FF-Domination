import React, { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';
import './NewsFeed.css';

const NewsFeed = ({ league }) => {
  const [newsItems, setNewsItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    // In a real implementation, this would fetch data from the news service
    const fetchNews = async () => {
      setLoading(true);
      
      // Mock news items
      const mockNewsItems = [
        {
          id: 1,
          title: "Player X Suffers Ankle Injury, Expected to Miss 2 Weeks",
          source: "ESPN",
          urgency: 5,
          timestamp: "2023-09-15T10:30:00Z",
          summary: "Key starter Player X will be out for multiple weeks, creating an opportunity for waiver wire pickups. This affects fantasy projections for multiple teams in your league.",
          link: "https://espn.com/news/player-x-injury"
        },
        {
          id: 2,
          title: "Team Y's Starting QB Questionable for Upcoming Game",
          source: "NFL.com",
          urgency: 4,
          timestamp: "2023-09-15T08:15:00Z",
          summary: "Backup QB expected to start, affecting fantasy projections for multiple players. Consider adjusting your lineup accordingly.",
          link: "https://nfl.com/news/team-y-qb-questionable"
        },
        {
          id: 3,
          title: "Weather Conditions to Impact Sunday's Games",
          source: "Rotowire",
          urgency: 3,
          timestamp: "2023-09-14T16:45:00Z",
          summary: "Heavy rain forecast for several games, affecting passing and rushing statistics projections. Players in outdoor games may see reduced performance.",
          link: "https://rotowire.com/news/weather-impact"
        },
        {
          id: 4,
          title: "Player Z Suspension Lifted, Available Immediately",
          source: "ESPN",
          urgency: 5,
          timestamp: "2023-09-14T14:20:00Z",
          summary: "Player Z's suspension has been lifted and they're available for immediate pickup. Strong projected performance for remainder of season.",
          link: "https://espn.com/news/player-z-suspension-lifted"
        },
        {
          id: 5,
          title: "Rookie Player A Showing Strong Training Camp Performance",
          source: "NFL.com",
          urgency: 2,
          timestamp: "2023-09-13T11:05:00Z",
          summary: "Rookie Player A is impressing coaches in training camp and could see increased playing time soon. Consider stashing on your bench for future value.",
          link: "https://nfl.com/news/rookie-player-a-performance"
        }
      ];
      
      setNewsItems(mockNewsItems);
      setLoading(false);
    };
    
    if (league) {
      fetchNews();
    }
  }, [league, filter]);
  
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
      
      <div className="news-grid">
        {filteredNews.map(item => (
          <NewsCard key={item.id} newsItem={item} />
        ))}
      </div>
    </div>
  );
};

export default NewsFeed;
