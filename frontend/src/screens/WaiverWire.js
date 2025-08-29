import React, { useState, useEffect } from 'react';
import WaiverClaimCard from '../components/WaiverClaimCard';
import './WaiverWire.css';

const WaiverWire = ({ league }) => {
  const [availablePlayers, setAvailablePlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [faabBudget, setFaabBudget] = useState(100);
  
  useEffect(() => {
    // In a real implementation, this would fetch data from the waiver wire service
    const fetchAvailablePlayers = async () => {
      setLoading(true);
      
      // Mock available players
      const mockPlayers = [
        {
          id: 1,
          name: "Player X",
          position: "RB",
          team: "BUF",
          projectedPoints: 18.5,
          newsUrgency: 5,
          bidRecommendation: "CLAIM",
          recommendedBid: 15.2
        },
        {
          id: 2,
          name: "Player Y",
          position: "WR",
          team: "KC",
          projectedPoints: 16.2,
          newsUrgency: 4,
          bidRecommendation: "CLAIM",
          recommendedBid: 12.8
        },
        {
          id: 3,
          name: "Player Z",
          position: "QB",
          team: "SF",
          projectedPoints: 22.1,
          newsUrgency: 3,
          bidRecommendation: "CLAIM",
          recommendedBid: 8.5
        },
        {
          id: 4,
          name: "Player A",
          position: "TE",
          team: "DAL",
          projectedPoints: 12.8,
          newsUrgency: 2,
          bidRecommendation: "PASS",
          recommendedBid: 0
        }
      ];
      
      setAvailablePlayers(mockPlayers);
      setLoading(false);
    };
    
    if (league) {
      fetchAvailablePlayers();
    }
  }, [league]);
  
  if (loading) {
    return <div className="screen-container">Loading waiver wire data...</div>;
  }
  
  return (
    <div className="screen-container">
      <div className="screen-header">
        <h1>Waiver Wire - {league?.name}</h1>
      </div>
      
      <div className="budget-card">
        <h3>FAAB Budget: ${faabBudget}</h3>
        <p>AI recommendations are based on player projections, team needs, and news urgency.</p>
      </div>
      
      <div className="players-grid">
        {availablePlayers.map(player => (
          <WaiverClaimCard 
            key={player.id} 
            player={{
              id: player.id,
              name: player.name,
              position: player.position,
              team: player.team,
              projectedPoints: player.projectedPoints,
              injuryStatus: 'Active',
              addPercentage: player.newsUrgency * 15
            }}
            onClaim={(playerId) => console.log(`Claiming player ${playerId}`)}
            faabBudget={faabBudget}
          />
        ))}
      </div>
    </div>
  );
};

export default WaiverWire;
