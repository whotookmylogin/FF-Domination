# Fantasy Football Frontend API Configuration

This document explains the API configuration and setup for the Fantasy Football frontend application.

## Overview

The frontend uses a robust API configuration system that provides:
- Dynamic environment-based URL configuration
- Comprehensive error handling and retry logic
- Request/response interceptors
- Authentication header management
- Health checking capabilities

## File Structure

```
frontend/
├── src/
│   ├── config/
│   │   └── api.js              # Main API configuration
│   └── services/
│       ├── api.js              # API service with all endpoints
│       └── __tests__/
│           └── api.test.js     # API service tests
├── .env                        # Environment variables
├── .env.example               # Environment template
└── API_SETUP.md               # This documentation
```

## Configuration Files

### 1. Environment Variables (`.env`)

The `.env` file contains all configuration for the API:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEV_API_URL=http://localhost:8000
REACT_APP_PRODUCTION_API_URL=https://your-production-api.com
REACT_APP_API_TIMEOUT=30000
REACT_APP_API_RETRY_ATTEMPTS=3
REACT_APP_API_RETRY_DELAY=1000

# Feature Flags
REACT_APP_ENABLE_DRAFT_TOOL=true
REACT_APP_ENABLE_TRADE_ANALYZER=true
REACT_APP_ENABLE_AI_FEATURES=true

# Debug Settings
REACT_APP_DEBUG_MODE=true
REACT_APP_DEBUG_API_REQUESTS=true
```

### 2. API Configuration (`src/config/api.js`)

This file contains:
- **Dynamic URL Resolution**: Automatically selects the correct API URL based on environment
- **Axios Instance**: Pre-configured with timeouts, headers, and interceptors
- **Request Interceptors**: Add authentication tokens and logging
- **Response Interceptors**: Handle errors and data transformation
- **Retry Logic**: Automatically retry failed requests with exponential backoff
- **Health Checking**: Test API connectivity

Key functions:
```javascript
import { apiClient, withRetry, checkApiHealth } from './config/api.js';

// Test API health
const isHealthy = await checkApiHealth();

// Make API request with retry
const data = await withRetry(() => apiClient.get('/endpoint'));
```

### 3. API Service (`src/services/api.js`)

Comprehensive service layer with organized endpoints:

#### League Endpoints
- `getLeagueAnalytics(leagueId)`
- `getLeagueData(leagueId)`
- `getLeagueSettings(leagueId)`
- `getLeagueStandings(leagueId)`

#### Team Endpoints  
- `getTeamAnalytics(teamId)`
- `getTeamData(teamId)`
- `getTeamStrength(teamId)`
- `importTeam(importData)`

#### Roster Endpoints
- `getRoster(teamId)`
- `getAllRosters(leagueId)`
- `updateLineup(teamId, lineupData)`

#### Trade Endpoints
- `getTradeSuggestions(teamId, filters)`
- `analyzeTrade(tradeData)`
- `proposeTrade(tradeProposal)`
- `getAITradeDiscovery(teamId, preferences)`

#### Waiver Wire Endpoints
- `getWaiverWirePlayers(leagueId, filters)`
- `getWaiverRecommendations(teamId)`
- `submitWaiverClaim(claimData)`

#### Player Endpoints
- `searchPlayers(query, filters)`
- `getPlayerDetails(playerId)`
- `getPlayerProjections(playerId, weeks)`

#### News Endpoints
- `getNews(filters)`
- `getPlayerNews(playerId)`
- `getInjuryReports(leagueId)`

#### Draft Endpoints
- `getDraftBoard(settings)`
- `getExpertDraftPicks(draftState)`
- `simulateDraft(scenario)`

#### Analytics Endpoints
- `getAdvancedAnalytics(teamId)`
- `getMatchupAnalysis(teamId, week)`
- `getPlayoffScenarios(teamId)`

#### Utility Methods
- `transformData(data, type)` - Convert API responses to frontend format
- `handleError(error)` - Generate user-friendly error messages
- `testConnection()` - Check API health

## Usage Examples

### Basic API Call
```javascript
import ApiService from './services/api';

try {
  const teamData = await ApiService.getTeamData('123');
  console.log('Team:', teamData);
} catch (error) {
  const errorMessage = ApiService.handleError(error);
  console.error('Error:', errorMessage);
}
```

### Data Transformation
```javascript
// Transform raw API response to frontend format
const rawTeamData = await ApiService.getTeamData('123');
const transformedData = ApiService.transformData(rawTeamData, 'team');

// Now use consistent field names (id, name, pointsFor, etc.)
console.log(`Team: ${transformedData.name} (${transformedData.record})`);
```

### Health Check
```javascript
const isApiHealthy = await ApiService.testConnection();
if (!isApiHealthy) {
  // Show offline mode or fallback data
  console.warn('API is not available, using cached data');
}
```

### Trade Analysis
```javascript
const tradeData = {
  givePlayers: ['player1', 'player2'],
  receivePlayers: ['player3'],
  fromTeam: 'team1',
  toTeam: 'team2'
};

const analysis = await ApiService.analyzeTrade(tradeData);
console.log('Trade analysis:', analysis);
```

## Error Handling

The API configuration includes comprehensive error handling:

### Network Errors
- Connection timeouts
- Network unavailable
- DNS resolution failures

### HTTP Errors
- 401 Unauthorized - Automatically clears auth tokens
- 403 Forbidden - Access denied
- 404 Not Found - Resource not found
- 429 Too Many Requests - Rate limiting
- 500 Server Error - Backend issues

### Retry Logic
- Automatically retries requests that fail due to network issues
- Uses exponential backoff to avoid overwhelming the server
- Skips retry for client errors (4xx) except 408 and 429
- Configurable retry attempts and delays

## Authentication

The API configuration supports authentication via Bearer tokens:

```javascript
// Tokens are automatically added to requests if present
localStorage.setItem('authToken', 'your-jwt-token');
// or
sessionStorage.setItem('authToken', 'your-jwt-token');

// Token is automatically included in Authorization header
```

## Development vs Production

The API automatically detects the environment:

### Development
- Uses `http://localhost:8000` by default
- Enables request/response logging
- Shows detailed error messages

### Production  
- Uses configured production URL
- Disables debug logging
- Uses secure HTTPS connections

## Testing

Run the API service tests:

```bash
npm test src/services/__tests__/api.test.js
```

## Configuration Validation

The system validates configuration on startup:
- Checks required environment variables
- Tests API connectivity
- Falls back to mock data if API is unavailable

## Best Practices

1. **Always use the ApiService**: Don't make direct fetch/axios calls
2. **Handle errors gracefully**: Use ApiService.handleError() for consistent messaging  
3. **Transform data**: Use ApiService.transformData() for consistent field names
4. **Check health**: Test connectivity before making critical requests
5. **Use environment variables**: Don't hardcode API URLs or configuration

## Troubleshooting

### API Connection Issues
1. Check if backend is running on the configured port
2. Verify CORS settings on the backend
3. Check network connectivity
4. Review browser console for detailed error messages

### Authentication Issues
1. Verify token is stored correctly
2. Check token expiration
3. Ensure backend accepts Bearer token format

### Environment Configuration
1. Verify `.env` file exists and has correct values
2. Restart development server after changing environment variables
3. Check that variable names start with `REACT_APP_`

## Deployment Considerations

### Production Environment Variables
1. Set `REACT_APP_PRODUCTION_API_URL` to your production API
2. Disable debug mode: `REACT_APP_DEBUG_MODE=false`  
3. Configure appropriate timeouts and retry settings
4. Ensure HTTPS is used for all API calls

### Build Process
The configuration is bundled into the build, so environment variables must be set at build time, not runtime.

## Future Enhancements

Potential improvements to the API configuration:
- WebSocket support for real-time updates
- Offline caching with Service Worker
- GraphQL support
- Request/response transformation plugins
- Advanced authentication (OAuth, refresh tokens)
- Metrics and monitoring integration