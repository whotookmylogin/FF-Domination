import React, { useState, useEffect } from 'react';
import './AITradeDiscovery.css';

const AITradeDiscovery = ({ league }) => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiConfig, setAiConfig] = useState({
    openai_key: '',
    openrouter_key: '',
    use_ai: false
  });

  const analyzeLeagueTrades = async () => {
    try {
      setLoading(true);
      setError(null);

      const requestBody = {
        league_id: league?.id || "83806"
      };

      // Add AI keys if provided
      if (aiConfig.use_ai) {
        if (aiConfig.openai_key) {
          requestBody.openai_key = aiConfig.openai_key;
        }
        if (aiConfig.openrouter_key) {
          requestBody.openrouter_key = aiConfig.openrouter_key;
        }
      }

      const response = await fetch('http://localhost:8000/ai/analyze-league-trades', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.status === 'success') {
        setTrades(data.trades);
      } else {
        setError(data.message || 'Failed to analyze trades');
      }
    } catch (err) {
      console.error('Error analyzing trades:', err);
      setError('Failed to connect to AI trade analyzer');
    } finally {
      setLoading(false);
    }
  };

  const testTradeAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8000/ai/test-trade-analysis');
      const data = await response.json();

      if (data.status === 'success') {
        // Convert the test response to the expected format
        setTrades([data.sample_trade].filter(Boolean));
      } else {
        setError(data.message || 'Test failed');
      }
    } catch (err) {
      console.error('Error testing trade analysis:', err);
      setError('Failed to test trade analyzer');
    } finally {
      setLoading(false);
    }
  };

  const formatPlayerName = (player) => {
    if (!player) return 'Unknown Player';
    return `${player.name} (${player.position}, ${player.team})`;
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

      {/* AI Configuration Panel */}
      <div className="ai-config-panel">
        <h3>AI Configuration (Optional)</h3>
        <div className="config-toggle">
          <label>
            <input
              type="checkbox"
              checked={aiConfig.use_ai}
              onChange={(e) => setAiConfig({...aiConfig, use_ai: e.target.checked})}
            />
            Enable AI Analysis (requires API key)
          </label>
        </div>
        
        {aiConfig.use_ai && (
          <div className="api-keys">
            <div className="key-input">
              <label>OpenAI API Key:</label>
              <input
                type="password"
                placeholder="sk-..."
                value={aiConfig.openai_key}
                onChange={(e) => setAiConfig({...aiConfig, openai_key: e.target.value})}
              />
            </div>
            <div className="key-input">
              <label>OpenRouter API Key:</label>
              <input
                type="password"
                placeholder="sk-or-..."
                value={aiConfig.openrouter_key}
                onChange={(e) => setAiConfig({...aiConfig, openrouter_key: e.target.value})}
              />
            </div>
            <p className="api-note">
              💡 Your API keys are never stored. Enter your own OpenAI or OpenRouter key for expert AI analysis.
            </p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <button 
          className="analyze-btn primary"
          onClick={analyzeLeagueTrades}
          disabled={loading}
        >
          {loading ? '🔍 Analyzing...' : '🚀 Analyze All League Trades'}
        </button>
        
        <button 
          className="test-btn secondary"
          onClick={testTradeAnalysis}
          disabled={loading}
        >
          🧪 Test Analysis (No AI Required)
        </button>
      </div>

      {/* Results */}
      {error && (
        <div className="error-message">
          ❌ {error}
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
            <p>Ranked by AI expert analysis and mutual benefit</p>
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
                    <h4>Team {trade.team_a_id} Gets:</h4>
                    <ul>
                      {trade.team_a_gets.map((player, i) => (
                        <li key={i} className="player-item">
                          {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                    <h4>Team {trade.team_a_id} Gives:</h4>
                    <ul>
                      {trade.team_a_gives.map((player, i) => (
                        <li key={i} className="player-item">
                          {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="trade-arrow">⚡</div>

                  <div className="team-trade">
                    <h4>Team {trade.team_b_id} Gets:</h4>
                    <ul>
                      {trade.team_b_gets.map((player, i) => (
                        <li key={i} className="player-item">
                          {formatPlayerName(player)}
                        </li>
                      ))}
                    </ul>
                    <h4>Team {trade.team_b_id} Gives:</h4>
                    <ul>
                      {trade.team_b_gives.map((player, i) => (
                        <li key={i} className="player-item">
                          {formatPlayerName(player)}
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

                {trade.ai_analysis && trade.ai_analysis !== "AI analysis not available - no API key provided" && (
                  <div className="ai-analysis">
                    <h4>🧠 AI Expert Analysis:</h4>
                    <p>{trade.ai_analysis}</p>
                  </div>
                )}

                {trade.ai_analysis === "AI analysis not available - no API key provided" && (
                  <div className="upgrade-prompt">
                    <p>💡 <strong>Want expert AI analysis?</strong> Add your OpenAI or OpenRouter API key above for detailed trade insights from our 30-year fantasy veteran AI!</p>
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
              <li>✅ Optional AI expert analysis with your API key</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AITradeDiscovery;