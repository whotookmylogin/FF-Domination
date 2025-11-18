import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import './TeamAnalysis.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const TeamAnalysis = ({ league }) => {
  const [teamAnalysis, setTeamAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchTeamAnalysis = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // TODO: Implement real team analysis endpoint
        // const teamId = league?.userTeam?.id || '7';
        // const response = await fetch(`http://localhost:8000/analytics/team/${teamId}`);
        // const data = await response.json();
        
        // For now, no mock data - just show empty state
        setTeamAnalysis(null);
        setError('Team analysis data is being calculated. Check back soon for detailed insights.');
      } catch (err) {
        console.error('Error fetching team analysis:', err);
        setTeamAnalysis(null);
        setError('Unable to load team analysis. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    if (league) {
      fetchTeamAnalysis();
    }
  }, [league]);
  
  if (loading) {
    return <div className="screen-container">Analyzing your team...</div>;
  }
  
  const positionalStrengthData = teamAnalysis ? {
    labels: Object.keys(teamAnalysis.positionalStrengths || {}),
    datasets: [
      {
        label: 'Positional Strength',
        data: Object.values(teamAnalysis.positionalStrengths || {}),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1
      }
    ]
  } : null;
  
  const positionalStrengthOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Positional Strength Analysis'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        title: {
          display: true,
          text: 'Strength Score (0-10)'
        }
      }
    }
  };
  
  return (
    <div className="screen-container">
      <div className="screen-header">
        <h1>Team Analysis - {league?.userTeam?.name || league?.name}</h1>
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
          <span style={{ fontSize: '20px' }}>📊</span>
          <div>
            <strong>Analysis In Progress</strong>
            <div style={{ fontSize: '14px', marginTop: '5px' }}>{error}</div>
          </div>
        </div>
      )}
      
      {!teamAnalysis && !error && (
        <div className="empty-state" style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📈</div>
          <h3>No Analysis Data Available</h3>
          <p>Team analysis will be available once the season progresses.</p>
        </div>
      )}
      
      {teamAnalysis && (
        <>
          <div className="analysis-grid">
            <div className="analysis-card">
              <h3>Overall Team Strength</h3>
              <p className="metric-value">{teamAnalysis.overallStrength}/100</p>
            </div>
            
            <div className="analysis-card">
              <h3>Injury Risk</h3>
              <p className="metric-value">{teamAnalysis.injuryRisk.toFixed(1)}/10</p>
            </div>
            
            <div className="analysis-card">
              <h3>Bench Quality</h3>
              <p className="metric-value">{teamAnalysis.benchQuality}/100</p>
            </div>
            
            <div className="analysis-card">
              <h3>Starters Performance</h3>
              <p className="metric-value">{teamAnalysis.startersPerformance.toFixed(1)} pts</p>
            </div>
          </div>
          
          {positionalStrengthData && (
            <div className="analysis-card">
              <h2>Positional Strength Analysis</h2>
              <div className="chart-container">
                <Bar data={positionalStrengthData} options={positionalStrengthOptions} />
              </div>
            </div>
          )}
          
          <div className="analysis-card">
            <h2>AI Recommendations</h2>
            <ul className="recommendations-list">
              {teamAnalysis.recommendations?.map((rec, index) => (
                <li key={index} className="recommendation-item">{rec}</li>
              )) || <li>No recommendations available at this time.</li>}
            </ul>
          </div>
          
          <div className="analysis-card">
            <h2>Positional Depth</h2>
            <table>
              <thead>
                <tr>
                  <th>Position</th>
                  <th>Player Count</th>
                  <th>Depth Quality</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(teamAnalysis.positionalDepth || {}).map(([position, depth]) => (
                  <tr key={position}>
                    <td>{position}</td>
                    <td>{depth.count}</td>
                    <td>{depth.quality}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default TeamAnalysis;