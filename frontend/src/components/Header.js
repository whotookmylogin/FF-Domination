import React, { useState, useEffect, useCallback } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUser, 
  faBell, 
  faCog, 
  faChevronDown, 
  faBars, 
  faTimes,
  faExclamationTriangle,
  faInfoCircle,
  faNewspaper,
  faUserInjured,
  faExchangeAlt,
  faTimes as faTimesCircle,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';
import { 
  getNotifications, 
  markNotificationAsRead, 
  deleteNotification, 
  clearAllNotifications,
  checkBreakingNewsForRoster 
} from '../services/api.js';
import './Header.css';

const Header = ({ user, selectedLeague, leagues, onLeagueChange, onMenuToggle, isMobileMenuOpen }) => {
  // UI state
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showLeagueDropdown, setShowLeagueDropdown] = useState(false);
  
  // Notification state
  const [notifications, setNotifications] = useState([]);
  const [notificationLoading, setNotificationLoading] = useState(false);
  const [notificationError, setNotificationError] = useState(null);

  /**
   * Get appropriate icon for notification type
   * @param {string} type - Notification type
   * @returns {Object} FontAwesome icon
   */
  const getNotificationIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'injury':
        return faUserInjured;
      case 'waiver':
      case 'waivers':
        return faExchangeAlt;
      case 'news':
        return faNewspaper;
      case 'warning':
        return faExclamationTriangle;
      case 'trade':
        return faExchangeAlt;
      default:
        return faInfoCircle;
    }
  };

  /**
   * Fetch notifications from API
   */
  const fetchNotifications = useCallback(async () => {
    if (!user?.id) return;
    
    setNotificationLoading(true);
    setNotificationError(null);
    
    try {
      const response = await getNotifications(user.id);
      // Handle different response structures
      const notificationData = response.notifications || response.data || response || [];
      // Ensure it's always an array
      setNotifications(Array.isArray(notificationData) ? notificationData : []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setNotificationError('Failed to load notifications');
      setNotifications([]);
    } finally {
      setNotificationLoading(false);
    }
  }, [user?.id]);

  /**
   * Mark individual notification as read
   * @param {string} notificationId - ID of notification to mark as read
   */
  const handleMarkAsRead = useCallback(async (notificationId) => {
    try {
      await markNotificationAsRead(notificationId);
      // Update local state
      setNotifications(prev => 
        prev.map(notification => 
          notification.id === notificationId 
            ? { ...notification, read: true, unread: false }
            : notification
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
      setNotificationError('Failed to mark notification as read');
    }
  }, []);

  /**
   * Delete individual notification
   * @param {string} notificationId - ID of notification to delete
   */
  const handleDeleteNotification = useCallback(async (notificationId) => {
    try {
      await deleteNotification(notificationId);
      // Remove from local state
      setNotifications(prev => prev.filter(notification => notification.id !== notificationId));
    } catch (error) {
      console.error('Error deleting notification:', error);
      setNotificationError('Failed to delete notification');
    }
  }, []);

  /**
   * Mark all notifications as read
   */
  const handleMarkAllAsRead = useCallback(async () => {
    if (!user?.id) return;
    
    try {
      await clearAllNotifications(user.id);
      // Update local state
      setNotifications(prev => 
        prev.map(notification => ({ ...notification, read: true, unread: false }))
      );
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      setNotificationError('Failed to mark all notifications as read');
    }
  }, [user?.id]);

  /**
   * Format notification time for display
   * @param {string|Date} timestamp - Notification timestamp
   * @returns {string} Formatted time string
   */
  const formatNotificationTime = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  // Fetch notifications on component mount and user change
  useEffect(() => {
    if (user?.id) {
      fetchNotifications();
    }
  }, [user?.id, fetchNotifications]); // eslint-disable-line react-hooks/exhaustive-deps

  // Check for breaking news related to roster
  const checkBreakingNews = useCallback(async () => {
    if (!user?.id || !selectedLeague) return;
    
    try {
      const response = await checkBreakingNewsForRoster(user.id, {
        league_id: selectedLeague.id,
        team_id: selectedLeague.team_id || selectedLeague.teamId,
        platform: selectedLeague.platform || 'espn'
      });
      
      // If new notifications were created, refresh the notification list
      if (response.notifications_created > 0) {
        fetchNotifications();
      }
    } catch (error) {
      console.error('Error checking breaking news:', error);
    }
  }, [user?.id, selectedLeague, fetchNotifications]);

  // Auto-refresh notifications every 30 seconds
  useEffect(() => {
    if (!user?.id) return;
    
    const interval = setInterval(() => {
      fetchNotifications();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [user?.id, fetchNotifications]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Check for breaking news every 2 minutes
  useEffect(() => {
    if (!user?.id || !selectedLeague) return;
    
    // Initial check
    checkBreakingNews();
    
    const interval = setInterval(() => {
      checkBreakingNews();
    }, 120000); // 2 minutes

    return () => clearInterval(interval);
  }, [user?.id, selectedLeague, checkBreakingNews]); // eslint-disable-line react-hooks/exhaustive-deps

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

  // Calculate unread count from API notifications (ensure notifications is an array)
  const unreadCount = Array.isArray(notifications) 
    ? notifications.filter(n => !n.read && n.unread !== false).length 
    : 0;

  return (
    <header className="header">
      <div className="header-content">
        <button className="mobile-menu-toggle" onClick={onMenuToggle}>
          <FontAwesomeIcon icon={isMobileMenuOpen ? faTimes : faBars} />
        </button>
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
                    {Array.isArray(notifications) && notifications.length > 0 && unreadCount > 0 && (
                      <button 
                        className="mark-all-read"
                        onClick={handleMarkAllAsRead}
                      >
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div className="dropdown-content">
                    {notificationLoading ? (
                      <div className="notification-loading">
                        <FontAwesomeIcon icon={faSpinner} spin />
                        <span>Loading notifications...</span>
                      </div>
                    ) : notificationError ? (
                      <div className="notification-error">
                        <FontAwesomeIcon icon={faExclamationTriangle} />
                        <span>{notificationError}</span>
                        <button onClick={fetchNotifications} className="retry-btn">
                          Retry
                        </button>
                      </div>
                    ) : Array.isArray(notifications) && notifications.length > 0 ? (
                      notifications.map(notification => (
                        <div 
                          key={notification.id} 
                          className={`notification-item ${!notification.read && notification.unread !== false ? 'unread' : ''}`}
                          onClick={() => !notification.read && handleMarkAsRead(notification.id)}
                        >
                          <div className="notification-icon">
                            <FontAwesomeIcon icon={getNotificationIcon(notification.type)} />
                          </div>
                          <div className="notification-content">
                            <div className="notification-header">
                              {notification.title && (
                                <div className="notification-title">{notification.title}</div>
                              )}
                              <div className="notification-type">{notification.type || 'Info'}</div>
                            </div>
                            <div className="notification-message">
                              {notification.message || notification.content || 'No message'}
                            </div>
                            {notification.url && (
                              <a 
                                href={notification.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="notification-link"
                                onClick={(e) => e.stopPropagation()}
                              >
                                Read Article →
                              </a>
                            )}
                            <div className="notification-time">
                              {formatNotificationTime(notification.timestamp || notification.created_at || notification.time)}
                            </div>
                          </div>
                          <div className="notification-actions">
                            <button 
                              className="delete-notification"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteNotification(notification.id);
                              }}
                              title="Delete notification"
                            >
                              <FontAwesomeIcon icon={faTimesCircle} />
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="no-notifications">
                        <FontAwesomeIcon icon={faBell} />
                        <p>No new notifications</p>
                      </div>
                    )}
                  </div>
                  {Array.isArray(notifications) && notifications.length > 0 && (
                    <div className="dropdown-footer">
                      <button 
                        className="view-all-btn"
                        onClick={() => {
                          // TODO: Implement view all notifications page
                          console.log('View all notifications');
                        }}
                      >
                        View All Notifications
                      </button>
                    </div>
                  )}
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
