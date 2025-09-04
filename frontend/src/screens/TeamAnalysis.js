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
        // Use the new ESPN team analytics endpoint
        const teamId = league?.userTeam?.id || '7';
        const leagueId = league?.id || '83806';
        const response = await fetch(`http://localhost:8000/analytics/espn/team/${teamId}?league_id=${leagueId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
          setTeamAnalysis(data);
          setError(null);
        } else {
          setTeamAnalysis(null);
          setError(data.message || 'Unable to load team analysis.');
        }
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
        backgroundColor: Object.values(teamAnalysis.positionalStrengths || {}).map(strength => {
          if (strength >= 8) return 'rgba(76, 175, 80, 0.6)';  // Green for strong
          if (strength >= 6) return 'rgba(255, 193, 7, 0.6)';  // Yellow for average
          if (strength >= 4) return 'rgba(255, 152, 0, 0.6)';  // Orange for below average
          return 'rgba(244, 67, 54, 0.6)';  // Red for weak
        }),
        borderColor: Object.values(teamAnalysis.positionalStrengths || {}).map(strength => {
          if (strength >= 8) return 'rgba(76, 175, 80, 1)';
          if (strength >= 6) return 'rgba(255, 193, 7, 1)';
          if (strength >= 4) return 'rgba(255, 152, 0, 1)';
          return 'rgba(244, 67, 54, 1)';
        }),
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
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          color: '#64b5f6',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          border: '1px solid rgba(33, 150, 243, 0.3)'
        }}>
          <span style={{ fontSize: '20px' }}>📊</span>
          <div>
            <strong>Analysis In Progress</strong>
            <div style={{ fontSize: '14px', marginTop: '5px', opacity: 0.9 }}>{error}</div>
          </div>
        </div>
      )}
      
      {!teamAnalysis && !error && (
        <div className="empty-state" style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          border: '1px solid var(--border-color)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📈</div>
          <h3 style={{ color: 'var(--text-primary)' }}>No Analysis Data Available</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Team analysis will be available once the season progresses.</p>
        </div>
      )}
      
      {teamAnalysis && (
        <>
          <div className="analysis-grid">
            <div className="analysis-card">
              <h3 style={{ color: 'var(--text-primary)' }}>Overall Team Strength</h3>
              <p className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
                {Number(teamAnalysis.overallStrength).toFixed(0)}/100
              </p>
            </div>
            
            <div className="analysis-card">
              <h3 style={{ color: 'var(--text-primary)' }}>Injury Risk</h3>
              <p className="metric-value" style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold', 
                color: Number(teamAnalysis.injuryRisk) > 7 ? '#f44336' : 
                       Number(teamAnalysis.injuryRisk) > 4 ? '#ff9800' : '#4caf50' 
              }}>
                {Number(teamAnalysis.injuryRisk).toFixed(1)}/10
              </p>
            </div>
            
            <div className="analysis-card">
              <h3 style={{ color: 'var(--text-primary)' }}>Bench Quality</h3>
              <p className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
                {Number(teamAnalysis.benchQuality).toFixed(0)}/100
              </p>
            </div>
            
            <div className="analysis-card">
              <h3 style={{ color: 'var(--text-primary)' }}>Starters Performance</h3>
              <p className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
                {Number(teamAnalysis.startersPerformance).toFixed(1)} pts
              </p>
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
            <h2 style={{ color: 'var(--text-primary)' }}>Positional Depth</h2>
            <table style={{ width: '100%', color: 'var(--text-primary)' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Position</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Player Count</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Depth Quality</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(teamAnalysis.positionalDepth || {}).map(([position, depth]) => (
                  <tr key={position} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <td style={{ padding: '10px' }}>{position}</td>
                    <td style={{ padding: '10px' }}>{depth.count}</td>
                    <td>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        backgroundColor: 
                          depth.quality === 'EXCELLENT' ? '#4caf50' :
                          depth.quality === 'GOOD' ? '#8bc34a' :
                          depth.quality === 'FAIR' ? '#ffeb3b' :
                          depth.quality === 'POOR' ? '#ff9800' :
                          depth.quality === 'CRITICAL' ? '#f44336' : '#9e9e9e',
                        color: 
                          depth.quality === 'FAIR' ? '#333' : 'white'
                      }}>
                        {depth.quality}
                      </span>
                    </td>
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