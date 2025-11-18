import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import NewsCard from '../components/NewsCard';
import TeamStrengthCard from '../components/TeamStrengthCard';
import TradeSuggestionCard from '../components/TradeSuggestionCard';
import WaiverClaimCard from '../components/WaiverClaimCard';
import AdvancedAnalyticsCard from '../components/AdvancedAnalyticsCard';
import IntelligentNotifications from '../components/IntelligentNotifications';
import ApiService from '../services/api';
import './Dashboard.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard = ({ league }) => {
  const [teamData, setTeamData] = useState({});
  const [roster, setRoster] = useState([]);
  const [newsItems, setNewsItems] = useState([]);
  const [tradeSuggestions, setTradeSuggestions] = useState([]);
  const [waiverClaims, setWaiverClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchRealData = async () => {
      if (!league) return;
      
      try {
        setLoading(true);
        
        // Use league context for team ID
        const teamId = league?.userTeam?.id || '7';
        const platform = league?.platform || 'ESPN';
        
        console.log(`Loading dashboard for ${platform} league: ${league?.name}, Team: ${teamId}`);
        
        // Fetch real roster data from backend using league context
        const rosterData = await ApiService.getRoster(teamId);
        
        if (rosterData.status === 'success') {
          // Set real roster data (handle double nesting)
          const realRoster = rosterData.data.data || rosterData.data;
          setRoster(realRoster);
          
          // Get team data for dashboard display
          const teamData = await ApiService.getTeamData(teamId);
          
          if (teamData.status === 'success') {
            const realTeamData = teamData.data;
            
            // Process real team data for dashboard display
            const processedTeamData = {
              overallRank: league?.userTeam?.standing || 1,
              totalTeams: league?.totalTeams || 12,
              teamName: league?.userTeam?.name || realTeamData.team_name,
              wins: league?.userTeam?.wins || realTeamData.wins || 0,
              losses: league?.userTeam?.losses || realTeamData.losses || 0,
              ties: realTeamData.ties || 0,
              pointsFor: league?.pointsFor || realTeamData.points_for || 0,
              pointsAgainst: realTeamData.points_against,
              // These would come from more detailed analytics endpoints
              projectedScore: Math.round(realTeamData.points_for / 17) || 0,
              winProbability: Math.round((realTeamData.wins / (realTeamData.wins + realTeamData.losses + realTeamData.ties)) * 100) || 0
            };
            
            setTeamData(processedTeamData);
          }
        }
        
        // Clear mock data - only use real data
        setNewsItems([]);
        setTradeSuggestions([]);
        setWaiverClaims([]);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Unable to load dashboard data. Please check your connection.');
      } finally {
        setLoading(false);
      }
    };
    
    if (league) {
      fetchRealData();
    }
  }, [league]);
  
  const weeklyTrendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
    datasets: [
      {
        label: 'Projected Points',
        data: teamData?.weeklyTrend || [],
        borderColor: 'var(--success)',
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        tension: 0.4,
        fill: true
      }
    ]
  };
  
  const weeklyTrendOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family)',
            size: 14
          }
        }
      },
      title: {
        display: true,
        text: 'Weekly Projected Points Trend',
        color: 'var(--text-primary)',
        font: {
          family: 'var(--font-family)',
          size: 16
        }
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Projected Points',
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family)',
            size: 14
          }
        },
        ticks: {
          color: 'var(--text-secondary)'
        },
        grid: {
          color: 'var(--border-color)'
        }
      },
      x: {
        ticks: {
          color: 'var(--text-secondary)'
        },
        grid: {
          color: 'var(--border-color)'
        }
      }
    }
  };
  
  if (loading) {
    return (
      <div className="loading-dashboard">
        <div className="loading-spinner"></div>
        <p>Loading your fantasy football dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-dashboard">
        <h3>Unable to Load Dashboard</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>
          Refresh Page
        </button>
      </div>
    );
  }
  
  return (
    <div className="app-container">
      <div className="dashboard-content">
        <div className="page-header">
          <h1>🏠 Dashboard</h1>
          <p>Your fantasy football command center</p>
        </div>
        
        {/* Intelligent Notifications Section */}
        <IntelligentNotifications league={league} user={roster} />

        {/* Team Overview Card */}
        <div className="modern-card team-overview">
          <div className="modern-card-header">
            <h2 className="modern-card-title">
              {teamData?.teamName || league?.name || 'My Team'}
            </h2>
            <div className="team-rank">
              Rank #{teamData?.overallRank || 'N/A'} of {teamData?.totalTeams || 12}
            </div>
          </div>
          
          <div className="team-stats-grid">
            <div className="stat-card">
              <div className="stat-label">Season Record</div>
              <div className="stat-value record">
                {teamData?.wins || 0}-{teamData?.losses || 0}-{teamData?.ties || 0}
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-label">Points For</div>
              <div className="stat-value points-for">
                {teamData?.pointsFor ? Math.round(teamData.pointsFor) : 0}
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-label">Points Against</div>
              <div className="stat-value points-against">
                {teamData?.pointsAgainst ? Math.round(teamData.pointsAgainst) : 0}
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-label">Avg Points/Week</div>
              <div className="stat-value avg-points">
                {teamData?.projectedScore || 0}
              </div>
            </div>
          </div>
        </div>

        {/* Roster Overview */}
        <div className="modern-card roster-overview">
          <div className="modern-card-header">
            <h3 className="modern-card-title">Current Roster</h3>
            <a href="/team-rosters" className="btn btn-sm btn-primary">
              View Full Roster
            </a>
          </div>
          
          <div className="roster-summary">
            {roster.length > 0 ? (
              <div className="roster-positions">
                {['QB', 'RB', 'WR', 'TE'].map(position => {
                  const players = roster.filter(p => p.position === position);
                  return (
                    <div key={position} className="position-summary">
                      <div className="position-label">{position}</div>
                      <div className="position-count">{players.length}</div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="empty-roster">
                <p>No roster data available</p>
                <button className="btn btn-primary" onClick={() => window.location.reload()}>
                  Refresh Data
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="modern-card quick-actions">
          <div className="modern-card-header">
            <h3 className="modern-card-title">Quick Actions</h3>
          </div>
          
          <div className="actions-grid">
            <a href="/ai-trade-discovery" className="action-card">
              <div className="action-icon">🤖</div>
              <div className="action-content">
                <h4>AI Trade Discovery</h4>
                <p>Find optimal trades using AI analysis</p>
              </div>
            </a>
            
            <a href="/team-rosters?view=league" className="action-card">
              <div className="action-icon">🏆</div>
              <div className="action-content">
                <h4>League Rosters</h4>
                <p>View all team rosters in your league</p>
              </div>
            </a>
            
            <a href="/expert-draft-tool" className="action-card">
              <div className="action-icon">🎯</div>
              <div className="action-content">
                <h4>Expert Draft Tool</h4>
                <p>Get AI-powered draft recommendations</p>
              </div>
            </a>
            
            <a href="/team-analysis" className="action-card">
              <div className="action-icon">📊</div>
              <div className="action-content">
                <h4>Team Analysis</h4>
                <p>Analyze your team's strengths and weaknesses</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
