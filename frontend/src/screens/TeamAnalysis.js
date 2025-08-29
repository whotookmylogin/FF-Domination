import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import './TeamAnalysis.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const TeamAnalysis = ({ league }) => {
  const [teamAnalysis, setTeamAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // In a real implementation, this would fetch data from the team analyzer service
    const fetchTeamAnalysis = async () => {
      setLoading(true);
      
      // Mock team analysis data
      const mockAnalysis = {
        overallStrength: 78,
        injuryRisk: 6.2,
        benchQuality: 65,
        startersPerformance: 98.5,
        positionalStrengths: {
          QB: 8.5,
          RB: 7.2,
          WR: 8.1,
          TE: 5.8,
          K: 7.5,
          DEF: 6.9
        },
        positionalDepth: {
          QB: { count: 2, quality: 'GOOD' },
          RB: { count: 5, quality: 'EXCELLENT' },
          WR: { count: 6, quality: 'EXCELLENT' },
          TE: { count: 2, quality: 'FAIR' },
          K: { count: 2, quality: 'GOOD' },
          DEF: { count: 2, quality: 'GOOD' }
        },
        recommendations: [
          "Weak at TE position - target available tight ends on waiver wire",
          "High injury risk - consider adding depth at key positions",
          "Bench quality is average - add players with high upside potential"
        ]
      };
      
      setTeamAnalysis(mockAnalysis);
      setLoading(false);
    };
    
    if (league) {
      fetchTeamAnalysis();
    }
  }, [league]);
  
  const positionalStrengthData = {
    labels: Object.keys(teamAnalysis?.positionalStrengths || {}),
    datasets: [
      {
        label: 'Positional Strength',
        data: Object.values(teamAnalysis?.positionalStrengths || {}),
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
  };
  
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
  
  if (loading) {
    return <div className="screen-container">Loading team analysis...</div>;
  }
  
  return (
    <div className="screen-container">
      <div className="screen-header">
        <h1>Team Analysis - {league?.name}</h1>
      </div>
      
      <div className="analysis-grid">
        <div className="analysis-card">
          <h3>Overall Team Strength</h3>
          <p className="metric-value">{teamAnalysis?.overallStrength}/100</p>
        </div>
        
        <div className="analysis-card">
          <h3>Injury Risk</h3>
          <p className="metric-value">{teamAnalysis?.injuryRisk.toFixed(1)}/10</p>
        </div>
        
        <div className="analysis-card">
          <h3>Bench Quality</h3>
          <p className="metric-value">{teamAnalysis?.benchQuality}/100</p>
        </div>
        
        <div className="analysis-card">
          <h3>Starters Performance</h3>
          <p className="metric-value">{teamAnalysis?.startersPerformance.toFixed(1)} pts</p>
        </div>
      </div>
      
      <div className="analysis-card">
        <h2>Positional Strength Analysis</h2>
        <div className="chart-container">
          <Bar data={positionalStrengthData} options={positionalStrengthOptions} />
        </div>
      </div>
      
      <div className="analysis-card">
        <h2>AI Recommendations</h2>
        <ul className="recommendations-list">
          {teamAnalysis?.recommendations.map((rec, index) => (
            <li key={index} className="recommendation-item">{rec}</li>
          ))}
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
            {Object.entries(teamAnalysis?.positionalDepth || {}).map(([position, depth]) => (
              <tr key={position}>
                <td>{position}</td>
                <td>{depth.count}</td>
                <td>{depth.quality}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TeamAnalysis;
