# Hardcoded User Data Documentation

This document lists all hardcoded user-specific data in the Fantasy Football Domination app. This data is specific to the user and has been hardcoded per their request to ensure the app functions correctly without requiring manual configuration.

## Frontend Hardcoded Data

### 1. User Information (App.js)
- **Location**: `/frontend/src/App.js`
- **Data**: 
  ```javascript
  const hardcodedUser = {
    id: '7',
    name: 'Trashy McTrash-Face',
    email: 'user@example.com',
    teamId: '7',
    sleeperUsername: 'wtml',
    sleeperUserId: '473578493909659648'
  };
  ```

### 2. League Information (App.js)
- **Location**: `/frontend/src/App.js`
- **ESPN League**:
  ```javascript
  {
    id: '83806',
    name: 'Sir Biffington\'s Revenge',
    platform: 'ESPN',
    season: 2025,
    currentWeek: 1,
    userTeam: {
      id: '7',
      name: 'Trashy McTrash-Face',
      wins: 0,
      losses: 0,
      standing: 1
    },
    record: '0-0',
    pointsFor: 0,
    pointsAgainst: 0,
    standing: 'TBD',
    totalTeams: 12
  }
  ```

- **Sleeper League**:
  ```javascript
  {
    id: '1181027706916478976',
    name: 'Patriot',
    platform: 'Sleeper',
    season: 2025,
    currentWeek: 1,
    userTeam: {
      id: '473578493909659648',
      name: 'wtml',
      wins: 0,
      losses: 0,
      standing: 1
    },
    record: '0-0',
    pointsFor: 0,
    pointsAgainst: 0,
    standing: 'TBD',
    totalTeams: 12,
    sleeperUsername: 'wtml',
    sleeperUserId: '473578493909659648'
  }
  ```

### 3. AI API Keys (ExpertDraftTool.js)
- **Location**: `/frontend/src/screens/ExpertDraftTool.js`
- **Data**:
  ```javascript
  const [aiConfig, setAiConfig] = useState({
    openai_key: 'YOUR_OPENAI_KEY_HERE',  // Replace with actual key
    openrouter_key: 'YOUR_OPENROUTER_KEY_HERE',  // Replace with actual key
    use_ai: true
  });
  ```

## Backend Hardcoded Data (.env file)

### 1. ESPN Platform Credentials
- **Location**: `/backend/.env`
- **Data**:
  ```
  ESPN_SWID={CF45D352-1A81-42CD-8C8F-793913E37FAD}
  ESPN_S2=AEBJygKX4kS%2Bg8GnRLNm0Iwd6TZh1KHswvEPy%2BHgfdht90xJeTkV6LFNbxT3vEQQWAG70Z3YKvJf4sb2SUvjzxDubFz76owEdryp2JnHFW1X9uUnHS2P9LYlYzO5UXma7SQik0iYp1hPNAX2yt3RAS1ok4m4WalDsOb7CIn1yVSzFN5fcY5%2BPsUzG5KTFYf4scKpcl6Lj2jqeIBcEX3HdLVBUDlmc4IHLeb2YvaVlIIk6k%2BlKlmEr9EBZphXolqMdPe%2F%2F4r1fW3bP9UrJEc4MvJ4eyAnKabTTSKauDTRyxDGOw%3D%3D
  ESPN_LEAGUE_ID=83806
  ESPN_TEAM_ID=7
  ESPN_SEASON_YEAR=2025
  ```

### 2. Sleeper Platform Configuration
- **Location**: `/backend/.env`
- **Data**:
  ```
  SLEEPER_USERNAME=wtml
  SLEEPER_USER_ID=473578493909659648
  SLEEPER_LEAGUE_ID=1181027706916478976
  ```

### 3. AI/ML API Keys
- **Location**: `/backend/.env`
- **Data**:
  ```
  OPENAI_API_KEY=YOUR_OPENAI_KEY_HERE
  OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY_HERE
  ```

## Important Notes

1. **Security**: These API keys and credentials should be kept secure and not shared publicly. Consider using environment variables or a secure credential management system in production.

2. **Updates**: When the 2025 season progresses, the hardcoded records (wins/losses) in App.js will need to be updated to reflect actual game results, or preferably, fetched dynamically from the ESPN/Sleeper APIs.

3. **Maintenance**: If any of these credentials expire or need to be updated, they must be changed in the locations specified above.

4. **Purpose**: This hardcoding was done per user request to ensure the app functions without requiring manual configuration each time. In a production environment, this data would typically be stored securely and fetched dynamically.

## Everything Else

All other data in the application is pulled dynamically from the appropriate sources:
- ESPN API for ESPN league data
- Sleeper API for Sleeper league data
- Backend endpoints for aggregated data
- Real-time updates when available

No other mock or placeholder data remains in the application.