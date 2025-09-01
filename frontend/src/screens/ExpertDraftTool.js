import React, { useState, useEffect } from 'react';
import './ExpertDraftTool.css';

const ExpertDraftTool = ({ league }) => {
  const [activeTab, setActiveTab] = useState('strategy');
  const [draftStrategy, setDraftStrategy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Draft configuration
  const [draftConfig, setDraftConfig] = useState({
    draft_position: 7,
    total_teams: 12,
    league_settings: {
      scoring_type: 'ppr',
      roster_size: 16,
      starting_lineup: {
        QB: 1,
        RB: 2,
        WR: 2,
        TE: 1,
        FLEX: 1,
        K: 1,
        DEF: 1,
        BENCH: 7
      }
    }
  });

  // AI configuration - API keys should be provided by backend
  const [aiConfig, setAiConfig] = useState({
    openai_key: '',  // Will be populated from backend/environment
    openrouter_key: '',  // Will be populated from backend/environment
    use_ai: true
  });

  // Live draft state
  const [liveState, setLiveState] = useState({
    current_round: 1,
    current_pick: 1,
    picks_made: [],
    available_players: [
      { name: 'Christian McCaffrey', position: 'RB', team: 'SF', adp: 1.2 },
      { name: 'Austin Ekeler', position: 'RB', team: 'LAC', adp: 2.1 },
      { name: 'Cooper Kupp', position: 'WR', team: 'LAR', adp: 3.5 },
      { name: 'Davante Adams', position: 'WR', team: 'LV', adp: 4.2 },
      { name: 'Stefon Diggs', position: 'WR', team: 'BUF', adp: 5.1 },
      { name: 'Travis Kelce', position: 'TE', team: 'KC', adp: 6.8 },
      { name: 'Josh Allen', position: 'QB', team: 'BUF', adp: 7.3 },
      { name: 'Jonathan Taylor', position: 'RB', team: 'IND', adp: 8.1 }
    ],
    user_roster: [],
    next_pick_in: 1
  });

  const [pickAnalysis, setPickAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const createDraftStrategy = async () => {
    try {
      setLoading(true);
      setError(null);

      const requestBody = {
        ...draftConfig
      };

      // Add AI keys (hardcoded for user)
      if (aiConfig.use_ai) {
        requestBody.openai_key = aiConfig.openai_key;
        requestBody.openrouter_key = aiConfig.openrouter_key;
      }

      const response = await fetch('http://localhost:8000/ai/draft-strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.status === 'success') {
        setDraftStrategy(data.strategy);
      } else {
        setError(data.message || 'Failed to create draft strategy');
      }
    } catch (err) {
      console.error('Error creating draft strategy:', err);
      setError('Failed to connect to draft expert');
    } finally {
      setLoading(false);
    }
  };

  const analyzePick = async (player) => {
    try {
      setLoading(true);
      
      const requestBody = {
        draft_state: liveState,
        player_under_consideration: player,
        league_settings: draftConfig.league_settings
      };

      if (aiConfig.use_ai) {
        if (aiConfig.openai_key) requestBody.openai_key = aiConfig.openai_key;
        if (aiConfig.openrouter_key) requestBody.openrouter_key = aiConfig.openrouter_key;
      }

      const response = await fetch('http://localhost:8000/ai/analyze-draft-pick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.status === 'success') {
        setPickAnalysis({ player, analysis: data.analysis });
      }
    } catch (err) {
      console.error('Error analyzing pick:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDraftRecommendations = async () => {
    try {
      setLoading(true);
      
      const requestBody = {
        draft_state: liveState,
        league_settings: draftConfig.league_settings,
        num_recommendations: 5
      };

      if (aiConfig.use_ai) {
        if (aiConfig.openai_key) requestBody.openai_key = aiConfig.openai_key;
        if (aiConfig.openrouter_key) requestBody.openrouter_key = aiConfig.openrouter_key;
      }

      const response = await fetch('http://localhost:8000/ai/draft-recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.status === 'success') {
        setRecommendations(data.recommendations);
      }
    } catch (err) {
      console.error('Error getting recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const draftPlayer = (player) => {
    // Add player to user roster
    setLiveState(prev => ({
      ...prev,
      user_roster: [...prev.user_roster, player],
      available_players: prev.available_players.filter(p => p.name !== player.name),
      current_pick: prev.current_pick + 1,
      current_round: Math.ceil((prev.current_pick + 1) / draftConfig.total_teams)
    }));
    
    // Clear current analysis
    setPickAnalysis(null);
  };

  const getGradeClass = (grade) => {
    if (['A+', 'A'].includes(grade)) return 'grade-a';
    if (['A-', 'B+'].includes(grade)) return 'grade-b';
    if (['B', 'B-'].includes(grade)) return 'grade-c';
    return 'grade-d';
  };

  const getRecommendationClass = (strength) => {
    switch (strength) {
      case 'VERY_HIGH': return 'rec-very-high';
      case 'HIGH': return 'rec-high';
      case 'MEDIUM': return 'rec-medium';
      case 'LOW': return 'rec-low';
      default: return 'rec-medium';
    }
  };

  return (
    <div className="expert-draft-tool">
      <div className="draft-header">
        <h1>🏆 Expert Draft Tool</h1>
        <p>Your 30-year fantasy veteran AI coach with 90% championship winning ratio</p>
      </div>

      {/* AI Configuration */}
      <div className="ai-config-section">
        <h3>🤖 AI Configuration</h3>
        <div className="config-toggle">
          <label>
            <input
              type="checkbox"
              checked={aiConfig.use_ai}
              onChange={(e) => setAiConfig({...aiConfig, use_ai: e.target.checked})}
            />
            Enable Expert AI Analysis (30-year veteran insights)
          </label>
        </div>
        
        {aiConfig.use_ai && (
          <div className="api-keys-grid">
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
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'strategy' ? 'active' : ''}`}
          onClick={() => setActiveTab('strategy')}
        >
          📋 Draft Strategy
        </button>
        <button 
          className={`tab-btn ${activeTab === 'live' ? 'active' : ''}`}
          onClick={() => setActiveTab('live')}
        >
          ⚡ Live Draft Assistant
        </button>
        <button 
          className={`tab-btn ${activeTab === 'config' ? 'active' : ''}`}
          onClick={() => setActiveTab('config')}
        >
          ⚙️ Draft Settings
        </button>
      </div>

      {/* Draft Settings Tab */}
      {activeTab === 'config' && (
        <div className="draft-config">
          <h3>Draft Configuration</h3>
          <div className="config-grid">
            <div className="config-item">
              <label>Draft Position:</label>
              <select 
                value={draftConfig.draft_position}
                onChange={(e) => setDraftConfig({...draftConfig, draft_position: parseInt(e.target.value)})}
              >
                {Array.from({length: 12}, (_, i) => (
                  <option key={i+1} value={i+1}>Pick {i+1}</option>
                ))}
              </select>
            </div>
            <div className="config-item">
              <label>Total Teams:</label>
              <select 
                value={draftConfig.total_teams}
                onChange={(e) => setDraftConfig({...draftConfig, total_teams: parseInt(e.target.value)})}
              >
                <option value={8}>8 Teams</option>
                <option value={10}>10 Teams</option>
                <option value={12}>12 Teams</option>
                <option value={14}>14 Teams</option>
              </select>
            </div>
            <div className="config-item">
              <label>Scoring Type:</label>
              <select 
                value={draftConfig.league_settings.scoring_type}
                onChange={(e) => setDraftConfig({
                  ...draftConfig, 
                  league_settings: {...draftConfig.league_settings, scoring_type: e.target.value}
                })}
              >
                <option value="standard">Standard</option>
                <option value="ppr">PPR</option>
                <option value="half_ppr">Half PPR</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Draft Strategy Tab */}
      {activeTab === 'strategy' && (
        <div className="draft-strategy-tab">
          <div className="strategy-header">
            <h3>🎯 Championship Draft Strategy</h3>
            <button 
              className="create-strategy-btn"
              onClick={createDraftStrategy}
              disabled={loading}
            >
              {loading ? '🧠 AI Expert Thinking...' : '🚀 Create Strategy'}
            </button>
          </div>

          {draftStrategy && (
            <div className="strategy-display">
              <div className="strategy-overview">
                <h4>📊 Recommended Strategy: {draftStrategy.strategy_name}</h4>
                <p>Optimized for {draftConfig.league_settings.scoring_type.toUpperCase()} scoring, pick #{draftConfig.draft_position}</p>
              </div>

              <div className="round-by-round">
                <h4>📅 Round-by-Round Plan</h4>
                <div className="rounds-grid">
                  {Object.entries(draftStrategy.round_by_round_plan).slice(0, 10).map(([round, plan]) => (
                    <div key={round} className="round-card">
                      <div className="round-header">
                        <span className="round-number">R{round}</span>
                        <span className="pick-number">Pick #{plan.overall_pick}</span>
                      </div>
                      <div className="target-positions">
                        <strong>Target:</strong> {plan.target_positions.join(', ')}
                      </div>
                      <div className="strategy-notes">
                        {plan.strategy_notes}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {draftStrategy.key_targets?.length > 0 && (
                <div className="key-targets">
                  <h4>🎯 Key Targets</h4>
                  <div className="targets-list">
                    {draftStrategy.key_targets.map((target, index) => (
                      <div key={index} className="target-card">
                        <div className="target-player">
                          <strong>{target.name}</strong> ({target.position})
                        </div>
                        <div className="target-rounds">
                          Rounds: {target.target_rounds.join('-')}
                        </div>
                        <div className="target-reasoning">
                          {target.reasoning}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Live Draft Assistant Tab */}
      {activeTab === 'live' && (
        <div className="live-draft-tab">
          <div className="draft-status">
            <h3>⚡ Live Draft Assistant</h3>
            <div className="status-bar">
              <div className="status-item">
                <span className="label">Round:</span>
                <span className="value">{liveState.current_round}</span>
              </div>
              <div className="status-item">
                <span className="label">Pick:</span>
                <span className="value">{liveState.current_pick}</span>
              </div>
              <div className="status-item">
                <span className="label">Your Roster:</span>
                <span className="value">{liveState.user_roster.length} players</span>
              </div>
            </div>
          </div>

          {/* Current Roster */}
          {liveState.user_roster.length > 0 && (
            <div className="current-roster">
              <h4>👥 Your Team</h4>
              <div className="roster-list">
                {liveState.user_roster.map((player, index) => (
                  <div key={index} className="roster-player">
                    <span className="player-name">{player.name}</span>
                    <span className="player-position">{player.position}</span>
                    <span className="player-team">{player.team}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="recommendations-section">
            <div className="recommendations-header">
              <h4>🎯 Expert Recommendations</h4>
              <button 
                className="get-recs-btn"
                onClick={getDraftRecommendations}
                disabled={loading}
              >
                {loading ? '🧠 Expert Analyzing...' : '🚀 Get Recommendations'}
              </button>
            </div>

            {recommendations.length > 0 && (
              <div className="recommendations-list">
                {recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-card">
                    <div className="rec-header">
                      <div className="rec-rank">#{index + 1}</div>
                      <div className="player-info">
                        <div className="player-name">{rec.player.name}</div>
                        <div className="player-details">
                          {rec.player.position} - {rec.player.team} (ADP: {rec.player.adp})
                        </div>
                      </div>
                      <div className={`rec-strength ${getRecommendationClass(rec.recommendation_strength)}`}>
                        {rec.recommendation_strength}
                      </div>
                    </div>
                    
                    <div className="rec-actions">
                      <button 
                        className="analyze-btn"
                        onClick={() => analyzePick(rec.player)}
                        disabled={loading}
                      >
                        📊 Analyze Pick
                      </button>
                      <button 
                        className="draft-btn"
                        onClick={() => draftPlayer(rec.player)}
                      >
                        ✅ Draft Player
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Pick Analysis */}
          {pickAnalysis && (
            <div className="pick-analysis">
              <h4>🧠 Expert Pick Analysis</h4>
              <div className="analysis-card">
                <div className="analysis-header">
                  <div className="player-info">
                    <strong>{pickAnalysis.player.name}</strong> ({pickAnalysis.player.position}, {pickAnalysis.player.team})
                  </div>
                  <div className={`grade ${getGradeClass(pickAnalysis.analysis.grade)}`}>
                    Grade: {pickAnalysis.analysis.grade}
                  </div>
                </div>
                <div className="analysis-content">
                  <div className="recommendation">
                    <strong>Recommendation:</strong> {pickAnalysis.analysis.recommendation}
                  </div>
                  <div className="analysis-text">
                    {pickAnalysis.analysis.analysis}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Available Players */}
          <div className="available-players">
            <h4>🏈 Available Players</h4>
            <div className="players-grid">
              {liveState.available_players.slice(0, 20).map((player, index) => (
                <div key={index} className="available-player">
                  <div className="player-info">
                    <div className="player-name">{player.name}</div>
                    <div className="player-details">{player.position} - {player.team}</div>
                    <div className="player-adp">ADP: {player.adp}</div>
                  </div>
                  <div className="player-actions">
                    <button 
                      className="analyze-btn-small"
                      onClick={() => analyzePick(player)}
                      disabled={loading}
                    >
                      📊
                    </button>
                    <button 
                      className="draft-btn-small"
                      onClick={() => draftPlayer(player)}
                    >
                      ✅
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Loading and Error States */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>🧠 30-year expert AI analyzing your draft situation...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}
    </div>
  );
};

export default ExpertDraftTool;