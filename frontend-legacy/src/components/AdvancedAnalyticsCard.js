import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';
import './AdvancedAnalyticsCard.css';

const AdvancedAnalyticsCard = ({ leagueId, teamId }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!leagueId && !teamId) return;
      
      setLoading(true);
      setError(null);
      
      try {
        let data;
        if (leagueId) {
          data = await ApiService.getLeagueAnalytics(leagueId);
        } else if (teamId) {
          data = await ApiService.getTeamAnalytics(teamId);
        }
        setAnalyticsData(data);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching analytics data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [leagueId, teamId]);

  if (loading) {
    return <div className="card">Loading advanced analytics...</div>;
  }

  if (error) {
    return <div className="card error">Error: {error}</div>;
  }

  if (!analyticsData) {
    return <div className="card">No analytics data available</div>;
  }

  return (
    <div className="card advanced-analytics-card">
      <h3>Advanced Analytics</h3>
      
      {analyticsData.league_projections && (
        <div className="analytics-section">
          <h4>League Projections</h4>
          <p>Total Teams: {analyticsData.league_projections.total_teams}</p>
          <p>Average Wins: {analyticsData.league_projections.average_wins?.toFixed(2)}</p>
          <p>Win Variance: {analyticsData.league_projections.win_variance?.toFixed(2)}</p>
        </div>
      )}
      
      {analyticsData.roster_analysis && (
        <div className="analytics-section">
          <h4>Roster Analysis</h4>
          <p>Total Players: {analyticsData.roster_analysis.total_players}</p>
          <p>Bench Strength: {analyticsData.roster_analysis.bench_strength}</p>
          
          <h5>Position Distribution</h5>
          <ul>
            {Object.entries(analyticsData.roster_analysis.position_distribution || {}).map(([position, count]) => (
              <li key={position}>{position}: {count}</li>
            ))}
          </ul>
        </div>
      )}
      
      {analyticsData.player_projections && (
        <div className="analytics-section">
          <h4>Top Projected Players</h4>
          <ul>
            {analyticsData.player_projections.slice(0, 3).map((player, index) => (
              <li key={player.player_id}>
                #{index + 1} {player.player_name} ({player.position}) - {player.projected_points?.toFixed(1)} pts
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {analyticsData.optimization_suggestions && (
        <div className="analytics-section suggestions">
          <h4>Optimization Suggestions</h4>
          <ul>
            {analyticsData.optimization_suggestions.map((suggestion, index) => (
              <li key={index} className={`suggestion priority-${suggestion.priority?.toLowerCase()}`}>
                {suggestion.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AdvancedAnalyticsCard;
