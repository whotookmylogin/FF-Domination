import React, { useState, useEffect } from 'react';
import TradeSuggestionCard from '../components/TradeSuggestionCard';
import './TradeSuggestions.css';

const TradeSuggestions = ({ league }) => {
  const [tradeSuggestions, setTradeSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // In a real implementation, this would fetch data from the trade suggestion engine
    const fetchTradeSuggestions = async () => {
      setLoading(true);
      
      // Mock trade suggestions
      const mockSuggestions = [
        {
          id: 1,
          playerIn: {
            name: "Player C",
            position: "QB",
            team: "Team X",
            projectedPoints: 18.2
          },
          playerOut: {
            name: "Player A",
            position: "RB",
            team: "Team Y",
            projectedPoints: 12.5
          },
          valueImprovement: 2.1,
          riskLevel: "medium"
        },
        {
          id: 2,
          playerIn: {
            name: "Player F",
            position: "WR",
            team: "Team Z",
            projectedPoints: 11.3
          },
          playerOut: {
            name: "Player E",
            position: "TE",
            team: "Team Y",
            projectedPoints: 8.1
          },
          valueImprovement: -1.2,
          riskLevel: "high"
        },
        {
          id: 3,
          playerIn: {
            name: "Player H",
            position: "DEF",
            team: "Team W",
            projectedPoints: 8.5
          },
          playerOut: {
            name: "Player G",
            position: "K",
            team: "Team Y",
            projectedPoints: 7.2
          },
          valueImprovement: 0.8,
          riskLevel: "low"
        }
      ];
      
      setTradeSuggestions(mockSuggestions);
      setLoading(false);
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
      
      <div className="trade-suggestions-grid">
        {tradeSuggestions.map(suggestion => (
          <TradeSuggestionCard key={suggestion.id} suggestion={suggestion} />
        ))}
      </div>
    </div>
  );
};

export default TradeSuggestions;
