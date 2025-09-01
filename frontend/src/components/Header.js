import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBell, faCog, faChevronDown } from '@fortawesome/free-solid-svg-icons';
import './Header.css';

const Header = ({ user, selectedLeague, leagues, onLeagueChange }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showLeagueDropdown, setShowLeagueDropdown] = useState(false);

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications);
    setShowSettings(false);
    setShowProfile(false);
    setShowLeagueDropdown(false);
  };

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
    setShowNotifications(false);
    setShowProfile(false);
    setShowLeagueDropdown(false);
  };

  const handleProfileClick = () => {
    setShowProfile(!showProfile);
    setShowNotifications(false);
    setShowSettings(false);
    setShowLeagueDropdown(false);
  };

  const handleLeagueClick = () => {
    setShowLeagueDropdown(!showLeagueDropdown);
    setShowNotifications(false);
    setShowSettings(false);
    setShowProfile(false);
  };

  // Real notifications based on selected league
  const getLeagueNotifications = () => {
    if (!selectedLeague) return [];
    
    const baseNotifications = [];
    
    if (selectedLeague.platform === 'ESPN') {
      baseNotifications.push(
        {
          id: 1,
          type: 'league',
          message: `New season started in ${selectedLeague.name}`,
          time: 'Today',
          unread: true
        },
        {
          id: 2,
          type: 'roster',
          message: 'Your roster is set for Week 1',
          time: '1 day ago',
          unread: false
        }
      );
    }
    
    if (selectedLeague.platform === 'Sleeper') {
      baseNotifications.push(
        {
          id: 3,
          type: 'league',
          message: `Welcome to ${selectedLeague.name} league`,
          time: 'Today',
          unread: true
        },
        {
          id: 4,
          type: 'draft',
          message: 'Draft date set for your Sleeper league',
          time: '2 days ago',
          unread: false
        }
      );
    }
    
    // Add generic notifications
    baseNotifications.push(
      {
        id: 5,
        type: 'system',
        message: 'Fantasy Football app updated to 2025 season',
        time: '3 days ago',
        unread: false
      }
    );
    
    return baseNotifications;
  };
  
  const notifications = getLeagueNotifications();
  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-brand">
          <h1>Fantasy Football Domination</h1>
        </div>
        
        <div className="header-controls">
          {leagues && leagues.length > 0 && (
            <div className="league-dropdown">
              <button className="league-selector-btn" onClick={handleLeagueClick}>
                {selectedLeague?.name || 'Select League'}
                <FontAwesomeIcon icon={faChevronDown} className="dropdown-icon" />
              </button>
              {showLeagueDropdown && (
                <div className="league-dropdown-content show">
                  {leagues.map(league => (
                    <div 
                      key={league.id} 
                      className={`league-option ${selectedLeague?.id === league.id ? 'active' : ''}`}
                      onClick={() => {
                        onLeagueChange(league);
                        setShowLeagueDropdown(false);
                      }}
                    >
                      {league.name} <span className="league-platform">{league.platform}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          <div className="header-actions">
            {/* Notifications */}
            <div className="header-dropdown">
              <button 
                className="header-icon-btn" 
                title="Notifications"
                onClick={handleNotificationClick}
              >
                <FontAwesomeIcon icon={faBell} />
                {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
              </button>
              
              {showNotifications && (
                <div className="dropdown-menu notifications-menu">
                  <div className="dropdown-header">
                    <h3>Notifications</h3>
                    <button className="mark-all-read">Mark all as read</button>
                  </div>
                  <div className="dropdown-content">
                    {notifications.length > 0 ? notifications.map(notification => (
                      <div key={notification.id} className={`notification-item ${notification.unread ? 'unread' : ''}`}>
                        <div className="notification-type">{notification.type}</div>
                        <div className="notification-message">{notification.message}</div>
                        <div className="notification-time">{notification.time}</div>
                      </div>
                    )) : (
                      <div className="no-notifications">
                        <p>No new notifications</p>
                      </div>
                    )}
                  </div>
                  <div className="dropdown-footer">
                    <button className="view-all-btn">View All Notifications</button>
                  </div>
                </div>
              )}
            </div>
            
            {/* Settings */}
            <div className="header-dropdown">
              <button 
                className="header-icon-btn" 
                title="Settings"
                onClick={handleSettingsClick}
              >
                <FontAwesomeIcon icon={faCog} />
              </button>
              
              {showSettings && (
                <div className="dropdown-menu settings-menu">
                  <div className="dropdown-header">
                    <h3>Settings</h3>
                  </div>
                  <div className="dropdown-content">
                    <div className="setting-item">
                      <span>Theme</span>
                      <select>
                        <option>Dark</option>
                        <option>Light</option>
                        <option>Auto</option>
                      </select>
                    </div>
                    <div className="setting-item">
                      <span>Notifications</span>
                      <input type="checkbox" defaultChecked />
                    </div>
                    <div className="setting-item">
                      <span>Auto-refresh</span>
                      <input type="checkbox" defaultChecked />
                    </div>
                  </div>
                  <div className="dropdown-footer">
                    <button className="btn btn-primary">Save Settings</button>
                  </div>
                </div>
              )}
            </div>
            
            {/* Profile */}
            <div className="header-dropdown">
              <div 
                className="user-profile clickable" 
                onClick={handleProfileClick}
                title="Profile Menu"
              >
                <div className="user-avatar">
                  <FontAwesomeIcon icon={faUser} />
                </div>
                <span className="user-name">{user?.name || 'Trashy McTrash-Face'}</span>
              </div>
              
              {showProfile && (
                <div className="dropdown-menu profile-menu">
                  <div className="dropdown-header">
                    <div className="profile-info">
                      <div className="user-avatar large">
                        <FontAwesomeIcon icon={faUser} />
                      </div>
                      <div>
                        <h3>{user?.name || 'Trashy McTrash-Face'}</h3>
                        <p>{user?.email || 'user@example.com'}</p>
                      </div>
                    </div>
                  </div>
                  <div className="dropdown-content">
                    <a href="/profile" className="menu-item">My Profile</a>
                    <a href="/achievements" className="menu-item">Achievements</a>
                    <a href="/stats" className="menu-item">My Stats</a>
                    <div className="menu-divider"></div>
                    <a href="/help" className="menu-item">Help & Support</a>
                    <a href="/logout" className="menu-item logout">Sign Out</a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
