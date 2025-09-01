import React, { useState, useEffect } from 'react';
import { aiApiClient } from '../config/api';
import './AITradeDiscovery.css';

const AITradeDiscovery = ({ league }) => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('my-team'); // 'my-team' or 'all-league'
  const [hasInitialLoad, setHasInitialLoad] = useState(false);

  // Version indicator to ensure new code is running
  console.log('✅ AITradeDiscovery v3.0 - Optimized for focus team analysis');

  const analyzeLeagueTrades = async (focusTeam = null) => {
    try {
      setLoading(true);
      setError(null);

      const requestBody = {
        league_id: league?.id || "83806",
        focus_team_id: focusTeam // Pass team ID to focus on specific team
      };

      console.log('🤖 Analyzing trades for league:', requestBody.league_id, 'Focus team:', focusTeam);

      const data = await aiApiClient.post('/ai/analyze-league-trades', requestBody);

      if (data.status === 'success') {
        console.log(`✅ Found ${data.trades?.length || 0} trade opportunities${data.from_cache ? ' (from cache)' : ' (fresh analysis)'}`);
        if (data.from_cache) {
          console.log(`📦 Results cached at: ${data.analysis_timestamp}`);
        }
        setTrades(data.trades || []);
        setHasInitialLoad(true);
      } else {
        console.error('❌ Trade analysis failed:', data.message);
        setError(data.message || 'Failed to analyze trades');
      }
    } catch (err) {
      console.error('Error analyzing trades:', err);
      setError('Failed to connect to AI trade analyzer. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Removed test functions - focusing on real functionality only

  // Auto-load trades when component mounts or league changes
  useEffect(() => {
    // Disabled auto-load to prevent timeout on page load
    // Uncomment below to re-enable once AI processing is optimized
    /*
    if (league?.id && !hasInitialLoad && !loading) {
      console.log('🎯 Auto-loading trade analysis for league:', league.name);
      // Auto-analyze for user's team on first load
      analyzeLeagueTrades(league?.userTeam?.id || '7');
    }
    */
  }, [league?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const formatPlayerName = (player) => {
    if (!player) return 'Unknown Player';
    return `${player.name} (${player.position}, ${player.team})`;
  };

  const formatAIAnalysis = (analysis) => {
    if (!analysis) return 'No analysis available';
    
    // Remove JSON formatting if present
    let cleanedAnalysis = analysis;
    
    // Check if it's wrapped in ```json blocks
    if (cleanedAnalysis.includes('```json')) {
      cleanedAnalysis = cleanedAnalysis.replace(/```json/g, '').replace(/```/g, '');
    }
    
    // Try to parse JSON if it looks like JSON
    if (cleanedAnalysis.trim().startsWith('{')) {
      try {
        const parsed = JSON.parse(cleanedAnalysis);
        // Extract the meaningful text from the JSON
        if (parsed.analysis) {
          if (typeof parsed.analysis === 'string') {
            return parsed.analysis;
          } else if (typeof parsed.analysis === 'object') {
            // Format nested JSON analysis
            let formatted = '';
            if (parsed.analysis.trade_fairness) {
              formatted += `Trade Fairness: ${parsed.analysis.trade_fairness}\n\n`;
            }
            if (parsed.analysis.team_a_playoff_chances) {
              formatted += `Impact on Your Team: ${parsed.analysis.team_a_playoff_chances}\n\n`;
            }
            if (parsed.analysis.risk_assessment) {
              formatted += `Risks to Consider: ${JSON.stringify(parsed.analysis.risk_assessment).replace(/[{}"]/g, '').replace(/,/g, ', ')}\n\n`;
            }
            if (parsed.analysis.overall_recommendation) {
              formatted += `Recommendation: ${parsed.analysis.overall_recommendation}\n`;
            }
            return formatted || cleanedAnalysis;
          }
        }
        // If we have other fields, format them nicely
        return Object.entries(parsed)
          .filter(([key]) => key !== 'fairness_score' && key !== 'confidence' && key !== 'urgency')
          .map(([key, value]) => `${key.replace(/_/g, ' ').toUpperCase()}: ${value}`)
          .join('\n\n');
      } catch (e) {
        // Not JSON, return as is
      }
    }
    
    // Return the cleaned analysis
    return cleanedAnalysis;
  };

  const getUrgencyClass = (urgency) => {
    switch (urgency) {
      case 'HIGH': return 'urgency-high';
      case 'MEDIUM': return 'urgency-medium';
      case 'LOW': return 'urgency-low';
      default: return 'urgency-medium';
    }
  };

  const getFairnessClass = (score) => {
    if (score >= 40 && score <= 60) return 'fairness-good';
    if (score > 60) return 'fairness-favors-you';
    return 'fairness-poor';
  };

  return (
    <div className="ai-trade-discovery">
      <div className="trade-discovery-header">
        <h1>🤖 AI Trade Discovery</h1>
        <p>Revolutionary multi-team trade analysis powered by 30-year fantasy expert AI</p>
      </div>

      {/* View Mode Toggle */}
      <div className="view-mode-selector">
        <h3>Trade Analysis Scope</h3>
        <div className="view-mode-buttons">
          <button 
            className={`mode-btn ${viewMode === 'my-team' ? 'active' : ''}`}
            onClick={() => setViewMode('my-team')}
          >
            🎯 My Team Trades
          </button>
          <button 
            className={`mode-btn ${viewMode === 'all-league' ? 'active' : ''}`}
            onClick={() => setViewMode('all-league')}
          >
            🏆 All League Trades
          </button>
        </div>
        <p className="mode-description">
          {viewMode === 'my-team' 
            ? `Analyzing trades specifically for ${league?.userTeam?.name || 'Trashy McTrash-Face'} (Team ${league?.userTeam?.id || '7'})`
            : 'Analyzing all possible trades across the entire league'}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <button 
          className="analyze-btn primary"
          onClick={() => analyzeLeagueTrades(viewMode === 'my-team' ? (league?.userTeam?.id || '7') : null)}
          disabled={loading}
          title="Analyze trades with AI (optimized for your team)"
        >
          {loading ? '🔍 Analyzing...' : viewMode === 'my-team' ? '🚀 Analyze My Team Trades' : '🚀 Analyze All League Trades'}
        </button>
      </div>

      {/* Results */}
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {loading && (
        <div className="loading-message" style={{
          textAlign: 'center',
          padding: '40px',
          fontSize: '1.2rem'
        }}>
          <div className="loading-spinner" style={{
            display: 'inline-block',
            animation: 'spin 1s linear infinite',
            fontSize: '2rem',
            marginBottom: '10px'
          }}>⚙️</div>
          <div>Analyzing {viewMode === 'my-team' ? 'your team\'s' : 'all league'} trade opportunities...</div>
          <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
            This may take a moment as our AI evaluates player values, bye weeks, and matchups
          </div>
        </div>
      )}

      {!loading && !error && trades.length === 0 && hasInitialLoad && (
        <div className="no-trades-message" style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🤷</div>
          <h3>No Trade Opportunities Found</h3>
          <p>The AI couldn't identify any beneficial trades at this time.</p>
          <p>Try analyzing {viewMode === 'my-team' ? 'all league trades' : 'your team trades'} instead.</p>
        </div>
      )}

      {!loading && !error && trades.length === 0 && !hasInitialLoad && (
        <div className="welcome-message" style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#e8f5e9',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🚀</div>
          <h3>Ready to Discover Trade Opportunities!</h3>
          <p>Click the "Analyze" button above to let our AI find the best trades for you.</p>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
            Our AI considers player values, bye weeks, upcoming matchups, and team needs.
          </p>
        </div>
      )}

      {loading && (
        <div className="loading-message">
          <div className="spinner"></div>
          <p>🤖 AI Expert analyzing all possible trades across your league...</p>
          <p>This may take 30-60 seconds for comprehensive analysis</p>
        </div>
      )}

      {trades.length > 0 && (
        <div className="trades-results">
          <div className="results-header">
            <h2>🎯 Trade Opportunities Found: {trades.length}</h2>
            <p>{viewMode === 'my-team' 
              ? `Trades involving ${league?.userTeam?.name || 'Trashy McTrash-Face'}, ranked by benefit to your team`
              : 'All league trades, ranked by AI expert analysis and mutual benefit'}</p>
          </div>

          <div className="trades-list">
            {trades.map((trade, index) => (
              <div key={index} className="trade-card">
                <div className="trade-header">
                  <div className="trade-number">#{index + 1}</div>
                  <div className={`urgency-badge ${getUrgencyClass(trade.urgency)}`}>
                    {trade.urgency} PRIORITY
                  </div>
                  <div className={`fairness-score ${getFairnessClass(trade.fairness_score)}`}>
                    Fairness: {trade.fairness_score}/100
                  </div>
                </div>

                <div className="trade-details">
                  <div className="team-trade">
                    <h4 style={{color: trade.team_a_id === '7' ? '#4CAF50' : '#333'}}>
                      {trade.team_a_name || `Team ${trade.team_a_id}`}
                      {trade.team_a_id === '7' && ' (YOU)'}
                    </h4>
                    <p><strong>Receives:</strong></p>
                    <ul>
                      {trade.team_a_gets.map((player, i) => (
                        <li key={i} className="player-item" style={{color: '#4CAF50'}}>
                          ➕ {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                    <p><strong>Gives Away:</strong></p>
                    <ul>
                      {trade.team_a_gives.map((player, i) => (
                        <li key={i} className="player-item" style={{color: '#f44336'}}>
                          ➖ {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="trade-arrow">⚡</div>

                  <div className="team-trade">
                    <h4 style={{color: trade.team_b_id === '7' ? '#4CAF50' : '#333'}}>
                      {trade.team_b_name || `Team ${trade.team_b_id}`}
                      {trade.team_b_id === '7' && ' (YOU)'}
                    </h4>
                    <p><strong>Receives:</strong></p>
                    <ul>
                      {trade.team_b_gets.map((player, i) => (
                        <li key={i} className="player-item" style={{color: '#4CAF50'}}>
                          ➕ {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                    <p><strong>Gives Away:</strong></p>
                    <ul>
                      {trade.team_b_gives.map((player, i) => (
                        <li key={i} className="player-item" style={{color: '#f44336'}}>
                          ➖ {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="trade-metrics">
                  <div className="metric">
                    <span className="metric-label">Team {trade.team_a_id} Improvement:</span>
                    <span className={`metric-value ${trade.team_a_improvement > 0 ? 'positive' : 'negative'}`}>
                      {trade.team_a_improvement > 0 ? '+' : ''}{trade.team_a_improvement.toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Team {trade.team_b_id} Improvement:</span>
                    <span className={`metric-value ${trade.team_b_improvement > 0 ? 'positive' : 'negative'}`}>
                      {trade.team_b_improvement > 0 ? '+' : ''}{trade.team_b_improvement.toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">AI Confidence:</span>
                    <span className="metric-value">{(trade.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>

                {/* Bye Week and Matchup Impact */}
                {(trade.bye_week_impact || trade.matchup_advantage || trade.timing_recommendation) && (
                  <div className="schedule-impact" style={{
                    backgroundColor: '#f8f9fa',
                    padding: '15px',
                    borderRadius: '6px',
                    marginTop: '15px'
                  }}>
                    {trade.bye_week_impact && (
                      <div className="bye-week-section" style={{ marginBottom: '10px' }}>
                        <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem' }}>📅 Bye Week Impact:</h4>
                        {trade.bye_week_impact.team_a && (
                          <div style={{ fontSize: '0.9rem', marginBottom: '5px' }}>
                            Team {trade.team_a_id}: {trade.bye_week_impact.team_a.improves ? '✅ Improves' : '⚠️ Worsens'} coverage
                            {trade.bye_week_impact.team_a.details && (
                              <span style={{ marginLeft: '5px', color: '#666' }}>
                                - {trade.bye_week_impact.team_a.details}
                              </span>
                            )}
                          </div>
                        )}
                        {trade.bye_week_impact.team_b && (
                          <div style={{ fontSize: '0.9rem' }}>
                            Team {trade.team_b_id}: {trade.bye_week_impact.team_b.improves ? '✅ Improves' : '⚠️ Worsens'} coverage
                          </div>
                        )}
                      </div>
                    )}
                    
                    {trade.matchup_advantage && (
                      <div className="matchup-section" style={{ marginBottom: '10px' }}>
                        <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem' }}>🎯 Matchup Advantage:</h4>
                        {trade.matchup_advantage.team_a && (
                          <div style={{ fontSize: '0.9rem', marginBottom: '5px' }}>
                            Team {trade.team_a_id}: 
                            <span style={{
                              marginLeft: '5px',
                              color: trade.matchup_advantage.team_a.strength_change > 0 ? '#28a745' : 
                                     trade.matchup_advantage.team_a.strength_change < 0 ? '#dc3545' : '#666'
                            }}>
                              {trade.matchup_advantage.team_a.strength_change > 0 ? '+' : ''}
                              {trade.matchup_advantage.team_a.strength_change} strength points
                            </span>
                            {trade.matchup_advantage.team_a.details && (
                              <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '3px' }}>
                                {trade.matchup_advantage.team_a.details}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {trade.timing_recommendation && (
                      <div className="timing-section">
                        <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem' }}>⏰ Timing Recommendation:</h4>
                        <div style={{
                          fontSize: '0.9rem',
                          padding: '8px',
                          backgroundColor: trade.timing_recommendation.includes('IMMEDIATELY') ? '#fff3cd' : '#e8f5e9',
                          borderRadius: '4px',
                          border: trade.timing_recommendation.includes('IMMEDIATELY') ? '1px solid #ffc107' : '1px solid #4caf50'
                        }}>
                          {trade.timing_recommendation}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {trade.ai_analysis && (
                  <div className="ai-analysis" style={{
                    backgroundColor: '#e3f2fd',
                    padding: '15px',
                    borderRadius: '8px',
                    marginTop: '15px',
                    borderLeft: '4px solid #2196F3'
                  }}>
                    <h4 style={{ marginTop: 0, marginBottom: '10px', color: '#1976D2' }}>
                      🧠 AI Expert Analysis for Trashy McTrash-Face:
                    </h4>
                    <div style={{ 
                      whiteSpace: 'pre-wrap', 
                      lineHeight: '1.6',
                      fontSize: '0.95rem',
                      color: '#333'
                    }}>
                      {formatAIAnalysis(trade.ai_analysis)}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {trades.length === 0 && !loading && !error && (
        <div className="no-trades">
          <h3>🔍 Ready to Discover Hidden Trade Opportunities</h3>
          <p>Click "Analyze All League Trades" to find profitable trades across your entire league that nobody else will see!</p>
          
          <div className="features-list">
            <h4>🚀 What You'll Get:</h4>
            <ul>
              <li>✅ Multi-team trade analysis (not just 1v1)</li>
              <li>✅ Real ESPN league data integration</li>
              <li>✅ Fairness scoring for every trade</li>
              <li>✅ Win probability improvement calculations</li>
              <li>✅ AI expert analysis powered by GPT-4</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AITradeDiscovery;