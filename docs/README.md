# Fantasy Football Domination App - Developer Documentation

## Overview

The Fantasy Football Domination App is an AI-powered assistant designed to help fantasy football managers make better decisions throughout their season. The application provides features such as player projections, trade analysis, waiver wire bidding, news aggregation, and team analysis.

## Architecture

The application follows a microservices architecture pattern with the following components:

### Backend Services

1. **Platform Integration Service** - Handles API interactions with ESPN and Sleeper
2. **AI Recommendation Engine** - Core machine learning models for player projections and recommendations
3. **News Aggregation Service** - Collects and processes fantasy football news from multiple sources
4. **Notification Service** - Sends push notifications to users via Firebase Cloud Messaging
5. **Trade Automation Service** - Generates and manages automated trade proposals
6. **Waiver Wire Service** - Implements automated bidding strategies for free agent acquisitions
7. **Team Analysis Service** - Provides comprehensive team evaluation and improvement suggestions

### Data Layer

1. **PostgreSQL Database** - Primary data storage for users, leagues, teams, players, trades, and news
2. **Redis Cache** - In-memory caching layer for performance optimization

### Frontend

1. **Mobile App** - React Native application for iOS and Android
2. **Web Dashboard** - React.js web interface for comprehensive analytics and management

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis

### Backend Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Set up PostgreSQL database
6. Set up Redis server
7. Configure environment variables (see below)

### Frontend Setup

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

## Environment Variables

The following environment variables need to be configured:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CREDENTIAL_ENCRYPTION_KEY` - Key for encrypting user credentials
- `ESPN_SWID_COOKIE` - ESPN authentication cookie (encrypted in database)
- `ESPN_S2_COOKIE` - ESPN authentication cookie (encrypted in database)
- `SLEEPER_API_TOKEN` - Sleeper API authentication token (encrypted in database)
- `FIREBASE_CREDENTIALS` - Firebase service account credentials for push notifications

## API Endpoints

### Platform Integration

- `GET /api/platforms/{platform}/leagues/{league_id}` - Fetch league data
- `GET /api/platforms/{platform}/leagues/{league_id}/teams` - Fetch teams in a league
- `GET /api/platforms/{platform}/leagues/{league_id}/rosters` - Fetch roster data

### AI Recommendations

- `GET /api/ai/projections/{player_id}` - Get player projections
- `POST /api/ai/trade/evaluate` - Evaluate trade fairness
- `GET /api/ai/team/{team_id}/analysis` - Get team analysis

### News

- `GET /api/news/league/{league_id}` - Get news for a specific league
- `GET /api/news/player/{player_id}` - Get news for a specific player

### Waiver Wire

- `GET /api/waiver/recommendations/{team_id}` - Get waiver wire bidding recommendations
- `POST /api/waiver/claim` - Submit a waiver claim

### Trades

- `GET /api/trade/suggestions/{team_id}` - Get trade suggestions
- `POST /api/trade/proposal` - Create a trade proposal
- `POST /api/trade/respond` - Respond to a trade proposal

## Testing

The application includes comprehensive unit tests for all services. To run tests:

```bash
cd backend
python -m pytest tests/
```

## Deployment

The application is designed to be deployed using Docker containers with Kubernetes orchestration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request
