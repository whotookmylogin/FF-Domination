import React, { useState, useEffect } from 'react';
import TradeSuggestionCard from '../components/TradeSuggestionCard';
import './TradeSuggestions.css';

const TradeSuggestions = ({ league }) => {
  const [tradeSuggestions, setTradeSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchTradeSuggestions = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // TODO: Implement real trade suggestions endpoint
        // const response = await fetch(`http://localhost:8000/trade-suggestions/${league?.id}`);
        // const data = await response.json();
        
        // For now, no mock data - just show empty state
        setTradeSuggestions([]);
        setError('Trade suggestions feature coming soon. AI analysis will be available once configured.');
      } catch (err) {
        console.error('Error fetching trade suggestions:', err);
        setTradeSuggestions([]);
        setError('Unable to load trade suggestions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    if (league) {
      fetchTradeSuggestions();
    }
  }, [league]);
  
  if (loading) {
    return <div className="screen-container">Loading trade suggestions...</div>;
  }
  
  return (
    <div className="screen-container">
      <div className="screen-header">
        <h1>Trade Suggestions - {league?.name}</h1>
      </div>
      
      <div className="instructions-card">
        <p>AI-generated trade recommendations based on projected performance and win probability analysis.</p>
        <p>Fairness scores range from 1-10 (10 being perfectly balanced). Win probability delta shows the expected change in your chances of winning the league.</p>
      </div>
      
      {error && (
        <div className="info-banner" style={{
          backgroundColor: '#e3f2fd',
          color: '#1565c0',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span style={{ fontSize: '20px' }}>ℹ️</span>
          <div>
            <strong>No Trade Suggestions Available</strong>
            <div style={{ fontSize: '14px', marginTop: '5px' }}>{error}</div>
          </div>
        </div>
      )}
      
      {tradeSuggestions.length === 0 && !error && (
        <div className="empty-state" style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤝</div>
          <h3>No Trade Suggestions Available</h3>
          <p>Check back later for AI-powered trade recommendations.</p>
        </div>
      )}
      
      {tradeSuggestions.length > 0 && (
        <div className="trade-suggestions-grid">
          {tradeSuggestions.map(suggestion => (
            <TradeSuggestionCard key={suggestion.id} suggestion={suggestion} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TradeSuggestions;