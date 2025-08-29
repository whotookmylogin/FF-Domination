import React from 'react';
import './Sidebar.css';

const Sidebar = ({ leagues, selectedLeague, onLeagueChange }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Fantasy Football Domination</h2>
      </div>
      
      {/* Current League Indicator */}
      {selectedLeague && (
        <div className="current-league-indicator">
          <div className="indicator-header">
            <span className="viewing-text">You are viewing</span>
            <div className="league-badge">
              <span className="league-name">{selectedLeague.name}</span>
              <span className="league-platform">{selectedLeague.platform}</span>
              <span className="league-record">{selectedLeague.record}</span>
            </div>
          </div>
        </div>
      )}
      
      <div className="league-selector">
        <h3>Your Leagues</h3>
        <ul className="league-list">
          {leagues && leagues.length > 0 ? (
            leagues.map((league) => (
              <li 
                key={league.id}
                className={`league-item ${selectedLeague && selectedLeague.id === league.id ? 'selected' : ''}`}
                onClick={() => onLeagueChange(league)}
              >
                <div className="league-name">{league.name || 'Unknown League'}</div>
                <div className="league-platform">{league.platform || 'Unknown Platform'}</div>
              </li>
            ))
          ) : (
            <li className="league-item">No leagues available</li>
          )}
        </ul>
      </div>
      
      <nav className="sidebar-nav">
        <ul>
          {/* Main Dashboard */}
          <li className="nav-section-header">
            <span className="section-title">📊 Overview</span>
          </li>
          <li className="nav-item">
            <a href="/" className="nav-link">🏠 Dashboard</a>
          </li>
          
          {/* Team Management */}
          <li className="nav-section-header">
            <span className="section-title">👥 Team Management</span>
          </li>
          <li className="nav-item">
            <a href="/team-import" className="nav-link import-link">
              ⚡ Import Team
            </a>
          </li>
          <li className="nav-item">
            <a href="/team-rosters" className="nav-link roster-link">
              🏈 My Roster
            </a>
          </li>
          <li className="nav-item">
            <a href="/team-rosters?view=league" className="nav-link">
              🏆 League Rosters
            </a>
          </li>
          <li className="nav-item">
            <a href="/team-analysis" className="nav-link">📈 Team Analysis</a>
          </li>
          
          {/* Trading & Transactions */}
          <li className="nav-section-header">
            <span className="section-title">🔄 Trading & Moves</span>
          </li>
          <li className="nav-item">
            <a href="/ai-trade-discovery" className="nav-link ai-link">
              🤖 AI Trade Discovery
            </a>
          </li>
          <li className="nav-item">
            <a href="/trade-suggestions" className="nav-link">💡 Trade Suggestions</a>
          </li>
          <li className="nav-item">
            <a href="/waiver-wire" className="nav-link">🏃 Waiver Wire</a>
          </li>
          
          {/* Draft Tools */}
          <li className="nav-section-header">
            <span className="section-title">🏆 Draft Tools</span>
          </li>
          <li className="nav-item">
            <a href="/expert-draft-tool" className="nav-link expert-link">
              🏆 Expert Draft Tool
            </a>
          </li>
          
          {/* Information */}
          <li className="nav-section-header">
            <span className="section-title">📰 Information</span>
          </li>
          <li className="nav-item">
            <a href="/news" className="nav-link">📰 News Feed</a>
          </li>
        </ul>
      </nav>
      
      <div className="sidebar-footer">
        <p>Fantasy Football Domination v1.0</p>
      </div>
    </div>
  );
};

export default Sidebar;
