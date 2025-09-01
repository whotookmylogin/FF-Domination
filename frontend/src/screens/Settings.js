import React, { useState } from 'react';
import './Settings.css';

const Settings = ({ user, leagues }) => {
  const [activeTab, setActiveTab] = useState('account');
  const [settings, setSettings] = useState({
    // Account Settings
    emailNotifications: true,
    pushNotifications: true,
    
    // League Settings
    defaultLeague: leagues?.[0]?.id || '',
    autoRefresh: true,
    refreshInterval: 30, // minutes
    
    // Notification Preferences
    injuryAlerts: true,
    tradeAlerts: true,
    waiverAlerts: true,
    newsAlerts: true,
    strategicRecommendations: true,
    
    // Advanced Settings
    monitoringFrequency: 6, // hours (4x daily)
    confidenceThreshold: 70, // minimum confidence % for recommendations
    
    // API Keys (already hardcoded but shown for reference)
    openaiConfigured: true,
    openrouterConfigured: true,
    espnConfigured: true,
    sleeperConfigured: true
  });

  const handleSettingChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
    // TODO: Save to backend
  };

  const renderAccountSettings = () => (
    <div className="settings-section">
      <h3>Account Information</h3>
      <div className="settings-group">
        <div className="setting-item">
          <label>Team Name</label>
          <input 
            type="text" 
            value={user?.name || 'Trashy McTrash-Face'} 
            disabled 
            className="setting-input disabled"
          />
          <span className="setting-note">Hardcoded for this user</span>
        </div>
        
        <div className="setting-item">
          <label>Email</label>
          <input 
            type="email" 
            value={user?.email || 'user@example.com'} 
            disabled 
            className="setting-input disabled"
          />
        </div>
      </div>

      <h3>Notification Preferences</h3>
      <div className="settings-group">
        <div className="setting-item toggle">
          <label>
            <span>Email Notifications</span>
            <small>Receive important updates via email</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.emailNotifications}
            onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
          />
        </div>
        
        <div className="setting-item toggle">
          <label>
            <span>Push Notifications</span>
            <small>Browser notifications for urgent alerts</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.pushNotifications}
            onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
          />
        </div>
      </div>
    </div>
  );

  const renderLeagueSettings = () => (
    <div className="settings-section">
      <h3>League Configuration</h3>
      <div className="settings-group">
        <div className="setting-item">
          <label>Default League</label>
          <select 
            value={settings.defaultLeague}
            onChange={(e) => handleSettingChange('defaultLeague', e.target.value)}
            className="setting-input"
          >
            {leagues?.map(league => (
              <option key={league.id} value={league.id}>
                {league.name} ({league.platform})
              </option>
            ))}
          </select>
        </div>
        
        <div className="setting-item toggle">
          <label>
            <span>Auto-Refresh Data</span>
            <small>Automatically update rosters and standings</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.autoRefresh}
            onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
          />
        </div>
        
        {settings.autoRefresh && (
          <div className="setting-item">
            <label>Refresh Interval (minutes)</label>
            <input 
              type="number" 
              min="5" 
              max="120"
              value={settings.refreshInterval}
              onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
              className="setting-input"
            />
          </div>
        )}
      </div>

      <h3>Import Team</h3>
      <div className="settings-group">
        <div className="platform-cards">
          <div className="platform-card espn configured">
            <h4>ESPN</h4>
            <p>League: Sir Biffington's Revenge</p>
            <p>Team: Trashy McTrash-Face</p>
            <span className="status">✓ Configured</span>
          </div>
          
          <div className="platform-card sleeper configured">
            <h4>Sleeper</h4>
            <p>League: Patriot</p>
            <p>Team: wtml</p>
            <span className="status">✓ Configured</span>
          </div>
          
          <div className="platform-card yahoo">
            <h4>Yahoo</h4>
            <p>Not configured</p>
            <button className="btn btn-secondary" disabled>
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="settings-section">
      <h3>Alert Preferences</h3>
      <div className="settings-group">
        <div className="setting-item toggle">
          <label>
            <span>Injury Alerts</span>
            <small>Immediate notifications for player injuries</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.injuryAlerts}
            onChange={(e) => handleSettingChange('injuryAlerts', e.target.checked)}
          />
        </div>
        
        <div className="setting-item toggle">
          <label>
            <span>Trade Alerts</span>
            <small>NFL trades and fantasy trade suggestions</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.tradeAlerts}
            onChange={(e) => handleSettingChange('tradeAlerts', e.target.checked)}
          />
        </div>
        
        <div className="setting-item toggle">
          <label>
            <span>Waiver Wire Alerts</span>
            <small>Hot pickups and waiver recommendations</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.waiverAlerts}
            onChange={(e) => handleSettingChange('waiverAlerts', e.target.checked)}
          />
        </div>
        
        <div className="setting-item toggle">
          <label>
            <span>Breaking News</span>
            <small>Important NFL news affecting fantasy</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.newsAlerts}
            onChange={(e) => handleSettingChange('newsAlerts', e.target.checked)}
          />
        </div>
        
        <div className="setting-item toggle">
          <label>
            <span>Strategic Recommendations</span>
            <small>AI-powered strategic blocking and positioning advice</small>
          </label>
          <input 
            type="checkbox" 
            checked={settings.strategicRecommendations}
            onChange={(e) => handleSettingChange('strategicRecommendations', e.target.checked)}
          />
        </div>
      </div>
    </div>
  );

  const renderAdvancedSettings = () => (
    <div className="settings-section">
      <h3>News Monitoring</h3>
      <div className="settings-group">
        <div className="setting-item">
          <label>
            <span>Monitoring Frequency</span>
            <small>How often to check for news (hours)</small>
          </label>
          <select 
            value={settings.monitoringFrequency}
            onChange={(e) => handleSettingChange('monitoringFrequency', parseInt(e.target.value))}
            className="setting-input"
          >
            <option value="3">Every 3 hours (8x daily)</option>
            <option value="6">Every 6 hours (4x daily)</option>
            <option value="12">Every 12 hours (2x daily)</option>
            <option value="24">Once daily</option>
          </select>
        </div>
        
        <div className="setting-item">
          <label>
            <span>Confidence Threshold</span>
            <small>Minimum confidence for recommendations (%)</small>
          </label>
          <input 
            type="range" 
            min="50" 
            max="95" 
            step="5"
            value={settings.confidenceThreshold}
            onChange={(e) => handleSettingChange('confidenceThreshold', parseInt(e.target.value))}
            className="setting-slider"
          />
          <span className="slider-value">{settings.confidenceThreshold}%</span>
        </div>
      </div>

      <h3>API Integrations</h3>
      <div className="settings-group">
        <div className="api-status">
          <div className="api-item">
            <span className="api-name">OpenAI</span>
            <span className="api-status-badge configured">✓ Configured</span>
          </div>
          <div className="api-item">
            <span className="api-name">OpenRouter</span>
            <span className="api-status-badge configured">✓ Configured</span>
          </div>
          <div className="api-item">
            <span className="api-name">ESPN API</span>
            <span className="api-status-badge configured">✓ Configured</span>
          </div>
          <div className="api-item">
            <span className="api-name">Sleeper API</span>
            <span className="api-status-badge configured">✓ Configured</span>
          </div>
          <div className="api-item">
            <span className="api-name">Twitter/X API</span>
            <span className="api-status-badge pending">⚠ Optional</span>
          </div>
        </div>
        <p className="setting-note">
          API keys are hardcoded for this installation. Contact admin to update.
        </p>
      </div>

      <h3>Draft Tools Configuration</h3>
      <div className="settings-group">
        <div className="setting-item">
          <label>Draft Position</label>
          <input 
            type="number" 
            min="1" 
            max="12"
            defaultValue="7"
            className="setting-input"
          />
        </div>
        
        <div className="setting-item">
          <label>League Size</label>
          <select className="setting-input" defaultValue="12">
            <option value="8">8 Teams</option>
            <option value="10">10 Teams</option>
            <option value="12">12 Teams</option>
            <option value="14">14 Teams</option>
          </select>
        </div>
        
        <div className="setting-item">
          <label>Scoring Type</label>
          <select className="setting-input" defaultValue="ppr">
            <option value="standard">Standard</option>
            <option value="half-ppr">Half PPR</option>
            <option value="ppr">Full PPR</option>
          </select>
        </div>
      </div>
    </div>
  );

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>⚙️ Settings</h1>
        <p>Configure your fantasy football experience</p>
      </div>
      
      <div className="settings-container">
        <div className="settings-tabs">
          <button 
            className={`tab ${activeTab === 'account' ? 'active' : ''}`}
            onClick={() => setActiveTab('account')}
          >
            Account
          </button>
          <button 
            className={`tab ${activeTab === 'leagues' ? 'active' : ''}`}
            onClick={() => setActiveTab('leagues')}
          >
            Leagues
          </button>
          <button 
            className={`tab ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            Notifications
          </button>
          <button 
            className={`tab ${activeTab === 'advanced' ? 'active' : ''}`}
            onClick={() => setActiveTab('advanced')}
          >
            Advanced
          </button>
        </div>
        
        <div className="settings-content">
          {activeTab === 'account' && renderAccountSettings()}
          {activeTab === 'leagues' && renderLeagueSettings()}
          {activeTab === 'notifications' && renderNotificationSettings()}
          {activeTab === 'advanced' && renderAdvancedSettings()}
        </div>
        
        <div className="settings-footer">
          <button className="btn btn-primary">
            Save Changes
          </button>
          <button className="btn btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;