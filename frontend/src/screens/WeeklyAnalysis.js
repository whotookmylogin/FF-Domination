import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';
import './WeeklyAnalysis.css';
import './WeeklyAnalysis.additional.css';
import './WeeklyAnalysis.contrast-fix.css';

const WeeklyAnalysis = ({ league }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [matchupData, setMatchupData] = useState(null);
    const [selectedWeek, setSelectedWeek] = useState(null);
    const [multiLeagueMode, setMultiLeagueMode] = useState(false);
    const [multiLeagueData, setMultiLeagueData] = useState([]);
    const [lastRefreshTime, setLastRefreshTime] = useState(null);
    const [isManualRefresh, setIsManualRefresh] = useState(false);

    // Calculate current NFL week
    const getCurrentNFLWeek = () => {
        const today = new Date();
        const seasonStart = new Date('2025-09-04'); // 2025 NFL season starts September 4, 2025
        
        if (today < seasonStart) {
            return 1;
        }
        
        const msPerWeek = 7 * 24 * 60 * 60 * 1000;
        const weeksSinceStart = Math.floor((today - seasonStart) / msPerWeek);
        return Math.min(weeksSinceStart + 1, 18); // 18 regular season weeks
    };

    useEffect(() => {
        // Auto-detect current week on mount
        if (!selectedWeek) {
            const currentWeek = getCurrentNFLWeek();
            setSelectedWeek(currentWeek);
        }
    }, []);

    useEffect(() => {
        if (league?.leagueId && league?.userTeam?.id && selectedWeek) {
            // Load from cache first, then fetch if needed
            loadCachedData();
        }
    }, [league, selectedWeek]);

    const loadCachedData = () => {
        try {
            const cacheKey = `matchup_${league?.leagueId}_${league?.userTeam?.id}_week${selectedWeek}`;
            const cachedData = localStorage.getItem(cacheKey);
            
            if (cachedData) {
                const parsed = JSON.parse(cachedData);
                const cacheAge = Date.now() - parsed.timestamp;
                const ONE_HOUR = 60 * 60 * 1000;
                
                // Use cache if less than 1 hour old and not manual refresh
                if (cacheAge < ONE_HOUR && !isManualRefresh) {
                    setMatchupData(parsed.data);
                    setLastRefreshTime(new Date(parsed.timestamp));
                    return;
                }
            }
            
            // If no valid cache, fetch fresh data
            fetchMatchupAnalysis();
        } catch (err) {
            console.error('Error loading cached data:', err);
            fetchMatchupAnalysis();
        }
    };

    const fetchMatchupAnalysis = async (forceRefresh = false) => {
        setLoading(true);
        setError(null);
        setIsManualRefresh(forceRefresh);

        try {
            const teamId = league?.userTeam?.id || '7';
            const leagueId = league?.leagueId || '83806';
            const platform = league?.platform || 'ESPN';
            
            // Build query params
            const params = new URLSearchParams({
                week: selectedWeek,
                platform: platform
            });
            
            // Add Sleeper-specific params if needed
            if (platform === 'Sleeper' || platform === 'SLEEPER') {
                if (league?.userId) params.append('user_id', league.userId);
                if (league?.username) params.append('username', league.username);
            }
            
            const response = await fetch(
                `http://localhost:8000/matchup/weekly/${leagueId}/${teamId}?${params}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                setMatchupData(data.matchup);
                setLastRefreshTime(new Date());
                
                // Save to cache
                const cacheKey = `matchup_${leagueId}_${teamId}_week${selectedWeek}`;
                localStorage.setItem(cacheKey, JSON.stringify({
                    timestamp: Date.now(),
                    data: data.matchup
                }));
            } else {
                setError(data.message || 'Failed to fetch matchup analysis');
            }
        } catch (err) {
            console.error('Error fetching matchup analysis:', err);
            setError('Failed to load matchup analysis. Please try again.');
        } finally {
            setLoading(false);
            setIsManualRefresh(false);
        }
    };

    const fetchMultipleLeagues = async () => {
        setLoading(true);
        setError(null);

        try {
            // Example with two leagues - in production, get these from user settings
            const leagues = [
                { league_id: '83806', team_id: '7' },
                // Add second league if configured
            ];

            const response = await fetch('http://localhost:8000/matchup/multiple-leagues', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    leagues: leagues,
                    week: selectedWeek
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                setMultiLeagueData(data.data);
            } else {
                setError('Failed to fetch multi-league analysis');
            }
        } catch (err) {
            console.error('Error fetching multiple leagues:', err);
            setError('Failed to load multiple league analysis.');
        } finally {
            setLoading(false);
        }
    };

    const getAdvantageColor = (rating) => {
        if (rating >= 70) return '#059669'; // Darker green for better contrast with white text
        if (rating >= 50) return '#d97706'; // Darker amber/orange for better contrast
        return '#dc2626'; // Darker red for better contrast
    };

    const renderPlayerCard = (player) => (
        <div key={player.name} className="player-matchup-card">
            <div className="player-header">
                <div className="player-info">
                    <span className="player-name">{player.name}</span>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
                        <span className="player-position">{player.position}</span>
                        <span className="player-team">{player.team} @ {player.opponent}</span>
                    </div>
                </div>
                <div className="player-rating" style={{ backgroundColor: getAdvantageColor(player.overall_rating) }}>
                    <div className="rating-value">{player.overall_rating.toFixed(0)}</div>
                    <div className="rating-label">Match Score</div>
                </div>
            </div>
            
            <div className="player-projection">
                <span className="projection-label">Week {selectedWeek} Projection: </span>
                <strong className="projection-value">{player.projected_points.toFixed(1)} pts</strong>
            </div>

            <div className="player-factors">
                {player.weather_impact && (
                    <div className={`weather-tag ${player.weather_impact === 'favorable' || player.weather_impact === 'dome' ? 'good' : 'bad'}`}>
                        {player.weather_impact === 'dome' ? '🏟️' : player.weather_impact === 'favorable' ? '☀️' : '🌧️'} {player.weather_impact}
                    </div>
                )}
                
                {player.defense_rating && (
                    <div className={`defense-tag ${player.defense_rating > 20 ? 'good' : player.defense_rating < 10 ? 'bad' : 'neutral'}`}>
                        DEF #{player.defense_rating.toFixed(0)}
                    </div>
                )}
            </div>

            {player.advantage_factors.length > 0 && (
                <div className="advantages">
                    <strong>✅ Advantages:</strong>
                    <ul>
                        {player.advantage_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                        ))}
                    </ul>
                </div>
            )}

            {player.disadvantage_factors.length > 0 && (
                <div className="disadvantages">
                    <strong>⚠️ Concerns:</strong>
                    <ul>
                        {player.disadvantage_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                        ))}
                    </ul>
                </div>
            )}

            {player.qb_analysis && (
                <div className="qb-analysis">
                    <strong>QB Analysis:</strong> {player.qb_analysis}
                </div>
            )}
        </div>
    );

    const renderTeamAnalysis = (teamData, isOpponent = false) => (
        <div className={`team-analysis ${isOpponent ? 'opponent' : 'user'}`}>
            <div className="team-header">
                <h3>{teamData.team_name}</h3>
                <div className="projected-total">
                    <span>Projected Total:</span>
                    <strong>{teamData.projected_total.toFixed(1)} pts</strong>
                </div>
            </div>

            {teamData.strengths && teamData.strengths.length > 0 && (
                <div className="team-strengths">
                    <h4>💪 Strengths</h4>
                    <ul>
                        {teamData.strengths.map((strength, idx) => (
                            <li key={idx}>{strength}</li>
                        ))}
                    </ul>
                </div>
            )}

            {teamData.weaknesses && teamData.weaknesses.length > 0 && (
                <div className="team-weaknesses">
                    <h4>⚠️ Weaknesses</h4>
                    <ul>
                        {teamData.weaknesses.map((weakness, idx) => (
                            <li key={idx}>{weakness}</li>
                        ))}
                    </ul>
                </div>
            )}

            {teamData.weather_advantages && teamData.weather_advantages.length > 0 && (
                <div className="weather-advantages">
                    <h4>🌤️ Weather Advantages</h4>
                    <ul>
                        {teamData.weather_advantages.map((advantage, idx) => (
                            <li key={idx}>{advantage}</li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="roster-cards">
                <h4>Starting Lineup (Week {selectedWeek})</h4>
                <div className="player-cards-grid">
                    {teamData.roster_analysis?.map(player => renderPlayerCard(player))}
                </div>
            </div>
        </div>
    );

    const renderHeadToHead = (h2h) => (
        <div className="head-to-head-analysis">
            <h3>Head-to-Head Analysis</h3>
            
            <div className="projection-difference">
                <span>Projected Difference: </span>
                <strong className={h2h.projected_difference > 0 ? 'positive' : 'negative'}>
                    {h2h.projected_difference > 0 ? '+' : ''}{h2h.projected_difference.toFixed(1)} pts
                </strong>
            </div>

            <div className="overall-advantage">
                <strong>{h2h.overall_advantage}</strong>
            </div>

            {h2h.position_advantages && h2h.position_advantages.length > 0 && (
                <div className="position-advantages">
                    <h4>✅ Position Advantages</h4>
                    <ul>
                        {h2h.position_advantages.map((adv, idx) => (
                            <li key={idx}>{adv}</li>
                        ))}
                    </ul>
                </div>
            )}

            {h2h.position_disadvantages && h2h.position_disadvantages.length > 0 && (
                <div className="position-disadvantages">
                    <h4>❌ Position Disadvantages</h4>
                    <ul>
                        {h2h.position_disadvantages.map((dis, idx) => (
                            <li key={idx}>{dis}</li>
                        ))}
                    </ul>
                </div>
            )}

            {h2h.key_matchups && h2h.key_matchups.length > 0 && (
                <div className="key-matchups">
                    <h4>🔑 Key Matchups to Watch</h4>
                    {h2h.key_matchups.map((matchup, idx) => (
                        <div key={idx} className="key-matchup">
                            <strong>{matchup.player}</strong>
                            <p>{matchup.impact}</p>
                            {matchup.factors && matchup.factors.length > 0 && (
                                <ul>
                                    {matchup.factors.map((factor, fidx) => (
                                        <li key={fidx}>{factor}</li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );

    const renderAIInsights = (insights) => {
        if (!insights) return null;

        return (
            <div className="ai-insights">
                <h3>🤖 AI-Powered Insights</h3>
                
                {insights.summary && (
                    <div className="insight-summary">
                        <p>{insights.summary}</p>
                    </div>
                )}

                {insights.key_insights && insights.key_insights.length > 0 && (
                    <div className="key-insights">
                        <h4>Key Insights</h4>
                        <ul>
                            {insights.key_insights.map((insight, idx) => (
                                <li key={idx}>{insight}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {insights.injury_updates && insights.injury_updates.length > 0 && (
                    <div className="injury-updates">
                        <h4>🚑 Injury Updates</h4>
                        <ul>
                            {insights.injury_updates.map((update, idx) => (
                                <li key={idx}>{update}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {insights.recommendations && insights.recommendations.length > 0 && (
                    <div className="ai-recommendations">
                        <h4>Recommendations</h4>
                        <ul>
                            {insights.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        );
    };

    const renderRecommendations = (recommendations) => {
        if (!recommendations || recommendations.length === 0) return null;

        return (
            <div className="action-recommendations">
                <h3>📋 Action Items</h3>
                <ul>
                    {recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                    ))}
                </ul>
            </div>
        );
    };

    return (
        <div className="weekly-analysis">
            <div className="analysis-header">
                <h1>Weekly Matchup Analysis</h1>
                <div className="analysis-controls">
                    <div className="week-selector">
                        <label>Week: </label>
                        <select 
                            value={selectedWeek || ''} 
                            onChange={(e) => {
                                const week = e.target.value ? parseInt(e.target.value) : getCurrentNFLWeek();
                                setSelectedWeek(week);
                            }}
                        >
                            {[...Array(18)].map((_, i) => (
                                <option key={i + 1} value={i + 1}>
                                    Week {i + 1}
                                    {i + 1 === getCurrentNFLWeek() ? ' (Current)' : ''}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    <button 
                        className="refresh-btn"
                        onClick={() => fetchMatchupAnalysis(true)}
                        disabled={loading}
                        title={lastRefreshTime ? `Last updated: ${lastRefreshTime.toLocaleTimeString()}` : 'Refresh with latest data'}
                    >
                        {loading ? 'Loading...' : '🔄 Refresh Analysis'}
                    </button>
                    
                    {lastRefreshTime && (
                        <span className="last-refresh-time">
                            Last updated: {lastRefreshTime.toLocaleTimeString()}
                        </span>
                    )}

                    <button 
                        className="multi-league-btn"
                        onClick={() => {
                            setMultiLeagueMode(!multiLeagueMode);
                            if (!multiLeagueMode) {
                                fetchMultipleLeagues();
                            }
                        }}
                    >
                        {multiLeagueMode ? 'Single League' : 'Multiple Leagues'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <p>❌ {error}</p>
                </div>
            )}

            {loading && (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Analyzing matchup data...</p>
                </div>
            )}

            {!loading && matchupData && !multiLeagueMode && (
                <div className="matchup-content">
                    {/* Executive Summary Section */}
                    <div className="executive-summary">
                        <h2>📊 Week {selectedWeek} Executive Summary</h2>
                        <div className="summary-cards">
                            <div className="summary-card">
                                <div className="summary-label">Your Projection</div>
                                <div className="summary-value">{matchupData.user_team?.projected_total?.toFixed(1)} pts</div>
                            </div>
                            <div className="summary-card">
                                <div className="summary-label">Opponent Projection</div>
                                <div className="summary-value">{matchupData.opponent_team?.projected_total?.toFixed(1)} pts</div>
                            </div>
                            <div className={`summary-card ${matchupData.head_to_head?.projected_difference > 0 ? 'positive' : 'negative'}`}>
                                <div className="summary-label">Projected Outcome</div>
                                <div className="summary-value">
                                    {matchupData.head_to_head?.projected_difference > 0 ? 'WIN by ' : 'LOSE by '}
                                    {Math.abs(matchupData.head_to_head?.projected_difference || 0).toFixed(1)} pts
                                </div>
                            </div>
                            <div className="summary-card">
                                <div className="summary-label">Win Probability</div>
                                <div className="summary-value">
                                    {matchupData.head_to_head?.projected_difference > 0 
                                        ? Math.min(50 + Math.abs(matchupData.head_to_head?.projected_difference) * 2, 95).toFixed(0)
                                        : Math.max(50 - Math.abs(matchupData.head_to_head?.projected_difference) * 2, 5).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                        
                        {/* Quick Insights */}
                        <div className="quick-insights">
                            <h3>🎯 Key Insights</h3>
                            <ul>
                                <li>
                                    <strong>Matchup Rating:</strong> {matchupData.head_to_head?.overall_advantage || 'Even matchup'}
                                </li>
                                {matchupData.user_team?.strengths?.[0] && (
                                    <li><strong>Your Strength:</strong> {matchupData.user_team.strengths[0]}</li>
                                )}
                                {matchupData.user_team?.weaknesses?.[0] && (
                                    <li><strong>Your Weakness:</strong> {matchupData.user_team.weaknesses[0]}</li>
                                )}
                                {matchupData.recommendations?.[0] && (
                                    <li><strong>Top Recommendation:</strong> {matchupData.recommendations[0]}</li>
                                )}
                            </ul>
                        </div>
                    </div>

                    <div className="teams-comparison">
                        {renderTeamAnalysis(matchupData.user_team)}
                        <div className="vs-divider">VS</div>
                        {renderTeamAnalysis(matchupData.opponent_team, true)}
                    </div>

                    {renderHeadToHead(matchupData.head_to_head)}
                    {renderAIInsights(matchupData.ai_insights)}
                    {renderRecommendations(matchupData.recommendations)}
                </div>
            )}

            {!loading && multiLeagueMode && multiLeagueData.length > 0 && (
                <div className="multi-league-content">
                    {multiLeagueData.map((leagueData, idx) => (
                        <div key={idx} className="league-matchup-section">
                            <h2>League {leagueData.league_id}</h2>
                            {leagueData.status === 'success' ? (
                                <div className="matchup-content">
                                    <div className="teams-comparison">
                                        {renderTeamAnalysis(leagueData.matchup.user_team)}
                                        <div className="vs-divider">VS</div>
                                        {renderTeamAnalysis(leagueData.matchup.opponent_team, true)}
                                    </div>
                                    {renderHeadToHead(leagueData.matchup.head_to_head)}
                                    {renderRecommendations(leagueData.matchup.recommendations)}
                                </div>
                            ) : (
                                <div className="error-message">
                                    <p>Failed to load matchup for this league: {leagueData.message}</p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default WeeklyAnalysis;