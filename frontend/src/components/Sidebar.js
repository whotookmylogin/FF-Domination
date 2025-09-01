import React from 'react';
import { Link } from 'react-router-dom';
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
          {/* Core Features - Daily Use */}
          <li className="nav-section-header">
            <span className="section-title">📊 Daily Tools</span>
          </li>
          <li className="nav-item">
            <Link to="/" className="nav-link">🏠 Dashboard</Link>
          </li>
          <li className="nav-item">
            <Link to="/team-rosters" className="nav-link roster-link">
              🏈 My Roster
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/waiver-wire" className="nav-link">🏃 Waiver Wire</Link>
          </li>
          <li className="nav-item">
            <Link to="/ai-trade-discovery" className="nav-link ai-link">
              🤖 AI Trade Discovery
            </Link>
          </li>
          
          {/* League Information */}
          <li className="nav-section-header">
            <span className="section-title">🏆 League</span>
          </li>
          <li className="nav-item">
            <Link to="/team-rosters?view=league" className="nav-link">
              👥 League Rosters
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/team-analysis" className="nav-link">📈 Team Analysis</Link>
          </li>
          <li className="nav-item">
            <Link to="/trade-suggestions" className="nav-link">💡 Trade Ideas</Link>
          </li>
          
          {/* News & Updates */}
          <li className="nav-section-header">
            <span className="section-title">📰 Updates</span>
          </li>
          <li className="nav-item">
            <Link to="/news" className="nav-link">📰 News Feed</Link>
          </li>
          
          {/* Settings - Move all setup items here */}
          <li className="nav-section-header">
            <span className="section-title">⚙️ Setup</span>
          </li>
          <li className="nav-item">
            <Link to="/settings" className="nav-link">
              ⚙️ Settings
            </Link>
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
