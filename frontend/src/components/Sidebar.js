import React from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import './Sidebar.css';

const Sidebar = ({ leagues, selectedLeague, onLeagueChange, isOpen, onClose }) => {
  const handleNavClick = () => {
    // Close menu on mobile when clicking a link
    if (window.innerWidth <= 768 && onClose) {
      onClose();
    }
  };

  return (
    <div className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <button className="sidebar-close-btn" onClick={onClose}>
        <FontAwesomeIcon icon={faTimes} />
      </button>
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
            <Link to="/" className="nav-link" onClick={handleNavClick}>🏠 Dashboard</Link>
          </li>
          
          {/* Team Management */}
          <li className="nav-section-header">
            <span className="section-title">👥 Team Management</span>
          </li>
          <li className="nav-item">
            <Link to="/team-import" className="nav-link import-link" onClick={handleNavClick}>
              ⚡ Import Team
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/team-rosters" className="nav-link roster-link" onClick={handleNavClick}>
              🏈 My Roster
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/team-rosters?view=league" className="nav-link" onClick={handleNavClick}>
              🏆 League Rosters
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/team-analysis" className="nav-link" onClick={handleNavClick}>📈 Team Analysis</Link>
          </li>
          
          {/* Trading & Transactions */}
          <li className="nav-section-header">
            <span className="section-title">🔄 Trading & Moves</span>
          </li>
          <li className="nav-item">
            <Link to="/ai-trade-discovery" className="nav-link ai-link" onClick={handleNavClick}>
              🤖 AI Trade Discovery
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/trade-suggestions" className="nav-link" onClick={handleNavClick}>💡 Trade Suggestions</Link>
          </li>
          <li className="nav-item">
            <Link to="/waiver-wire" className="nav-link" onClick={handleNavClick}>🏃 Waiver Wire</Link>
          </li>
          
          {/* League Information */}
          <li className="nav-section-header">
            <span className="section-title">🏆 League</span>
          </li>
          <li className="nav-item">
            <Link to="/expert-draft-tool" className="nav-link expert-link" onClick={handleNavClick}>
              🏆 Expert Draft Tool
            </Link>
          </li>
          
          {/* News & Updates */}
          <li className="nav-section-header">
            <span className="section-title">📰 Updates</span>
          </li>
          <li className="nav-item">
            <Link to="/news" className="nav-link" onClick={handleNavClick}>📰 News Feed</Link>
          </li>
          
          {/* Settings - Move all setup items here */}
          <li className="nav-section-header">
            <span className="section-title">⚙️ Setup</span>
          </li>
          <li className="nav-item">
            <Link to="/settings" className="nav-link" onClick={handleNavClick}>
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