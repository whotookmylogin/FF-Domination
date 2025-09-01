# Fantasy Football Domination App - Development Guide

A comprehensive guide for developers to set up, run, and contribute to the Fantasy Football Domination App.

## 🚀 Quick Start

### One-Command Startup

```bash
./start.sh
```

That's it! This command will:
- Check all dependencies
- Set up the backend (Python/FastAPI)
- Set up the frontend (React)
- Initialize the database
- Start background workers
- Provide real-time health monitoring

### Alternative Quick Start Options

```bash
# Skip dependency checks (if you know they're installed)
./start.sh --skip-deps

# Skip frontend (backend only)
./start.sh --skip-frontend

# Development mode with verbose logging
./start.sh --dev

# Skip background workers
./start.sh --skip-workers
```

### Stopping the Application

```bash
./stop.sh
```

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - Backend API server
- **Node.js 18+** - Frontend development server
- **npm 8+** - Package manager
- **Redis** - Caching and background tasks (optional but recommended)

### Optional Software
- **Docker** - For containerized deployment
- **PostgreSQL** - Production database (SQLite used for development)

### Installation Commands

**macOS (using Homebrew):**
```bash
brew install python3 node redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm redis-server
```

**Windows:**
- Download Python from [python.org](https://python.org)
- Download Node.js from [nodejs.org](https://nodejs.org)
- Install Redis using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/)

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Background    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Workers       │
│   Port: 3000    │    │   Port: 8000    │    │   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│     Redis       │◄─────────────┘
                         │   (Cache/Queue) │
                         │   Port: 6379    │
                         └─────────────────┘
                                  │
                         ┌─────────────────┐
                         │   SQLite DB     │
                         │ (Development)   │
                         └─────────────────┘
```

### Directory Structure

```
fantasy-football-app/
├── backend/                 # Python FastAPI backend
│   ├── src/                 # Source code
│   │   ├── ai/             # AI/ML models and analysis
│   │   ├── analytics/      # Advanced analytics
│   │   ├── database/       # Database models and connections
│   │   ├── news/           # News aggregation service
│   │   ├── notifications/  # Push notification system
│   │   ├── platforms/      # ESPN/Sleeper integrations
│   │   ├── trade/          # Trade suggestion engine
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── setup.sh           # Backend setup script
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── screens/        # Main app screens
│   │   ├── services/       # API integration
│   │   └── styles/         # CSS and design system
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── docs/                   # Additional documentation
├── start.sh                # Master startup script
├── stop.sh                 # Shutdown script
├── docker-compose.yml      # Docker services
└── README.md               # Main documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./fantasy_football.db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Fantasy Platform API Keys
ESPN_COOKIE=your_espn_cookie_here
SLEEPER_TOKEN=your_sleeper_token_here

# News API Keys
ROTOWIRE_API_KEY=your_rotowire_key_here

# AI/ML API Keys (optional)
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_KEY=your_openrouter_key_here

# Notification Services (optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
SECRET_KEY=your-secret-key-here
CREDENTIAL_ENCRYPTION_KEY=auto-generated-by-setup
```

### Getting API Keys

#### ESPN Integration
1. Log into your ESPN fantasy account
2. Open browser developer tools (F12)
3. Go to Application/Storage tab
4. Copy the `espn_s2` and `SWID` cookie values

#### Sleeper Integration
- No API key required - uses public API

#### News APIs
- **RotowWire**: Sign up at [rotowire.com](https://rotowire.com) for API access

#### AI Services (Optional)
- **OpenAI**: Get key from [platform.openai.com](https://platform.openai.com)
- **OpenRouter**: Alternative AI provider at [openrouter.ai](https://openrouter.ai)

## 🔗 API Documentation

### Backend API Endpoints

The backend provides a comprehensive REST API documented with FastAPI's automatic OpenAPI documentation.

**Access API Documentation:**
- Interactive Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

### Core Endpoints

#### Fantasy Data
```bash
# Get league analytics
GET /analytics/league/{league_id}

# Get user team data
GET /user/team/{team_id}

# Get team roster
GET /user/roster/{team_id}
```

#### AI Analysis
```bash
# Analyze all possible trades
POST /ai/analyze-league-trades
{
  "league_id": "83806",
  "openai_key": "optional_key"
}

# Generate draft strategy
POST /ai/draft-strategy
{
  "league_settings": {...},
  "draft_position": 7
}
```

#### News & Notifications
```bash
# Get aggregated news
GET /news/aggregated

# Get breaking news
GET /news/breaking?min_urgency=4

# Send notification
POST /notifications/send
{
  "user_id": "user123",
  "title": "Trade Alert",
  "message": "New trade opportunity!"
}
```

### Frontend API Integration

The frontend uses Axios for API calls with a centralized configuration:

```javascript
// src/config/api.js
const API_BASE_URL = 'http://localhost:8000';

// src/services/api.js
export const fetchLeagueAnalytics = async (leagueId) => {
  const response = await axios.get(`${API_BASE_URL}/analytics/league/${leagueId}`);
  return response.data;
};
```

## 🧪 Testing

### Running Tests

**Backend Tests:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=src
```

**Frontend Tests:**
```bash
cd frontend
npm test
npm run test:coverage
```

**Integration Tests:**
```bash
# Start the application first
./start.sh

# Run integration tests
cd backend
pytest tests/integration/ -v
```

### Test Structure

```
backend/tests/
├── unit/                   # Unit tests for individual components
│   ├── ai/                # AI module tests
│   ├── analytics/         # Analytics tests
│   ├── platforms/         # Platform integration tests
│   └── ...
├── integration/           # Integration tests
│   └── test_platform_integration.py
└── fixtures/              # Test data and fixtures

frontend/src/services/__tests__/
├── api.test.js            # API service tests
└── ...
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Backend Won't Start
**Error:** `ModuleNotFoundError` or import errors
**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error:** Database connection failed
**Solution:**
```bash
# Reset database
rm -f backend/fantasy_football.db
cd backend && python3 -c "
import sys
sys.path.append('src')
from database.connection import create_database
create_database()
"
```

#### 2. Frontend Won't Start
**Error:** `npm: command not found`
**Solution:** Install Node.js from [nodejs.org](https://nodejs.org)

**Error:** Port 3000 already in use
**Solution:**
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Or start on different port
cd frontend && PORT=3001 npm start
```

#### 3. Redis Connection Issues
**Error:** Redis connection refused
**Solution:**
```bash
# macOS
brew services start redis

# Ubuntu/Debian
sudo systemctl start redis

# Manual start
redis-server --daemonize yes
```

#### 4. API Integration Issues
**Error:** ESPN data not loading
**Solution:**
1. Check ESPN cookies in `.env` file
2. Ensure you're logged into ESPN
3. Update cookies if they've expired

**Error:** News not loading
**Solution:**
1. Verify RotowWire API key
2. Check rate limiting
3. Test news endpoints directly

#### 5. Background Workers Not Starting
**Error:** Celery worker failed
**Solution:**
```bash
cd backend
source venv/bin/activate

# Check Celery status
celery -A src.news.scheduler status

# Restart worker
celery -A src.news.scheduler worker --loglevel=info
```

### Debugging Tools

#### View Logs
```bash
# Backend logs
tail -f backend/logs/backend.log

# Frontend logs
# Check browser console or terminal where npm start is running

# Worker logs
tail -f backend/logs/celery.log
tail -f backend/logs/news_worker.log
```

#### Check Service Status
```bash
# Check if services are running
ps aux | grep -E "(python|node|redis|celery)"

# Check port usage
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :6379  # Redis
```

#### Database Debugging
```bash
# Connect to SQLite database
cd backend
sqlite3 fantasy_football.db

# List tables
.tables

# Check users table
SELECT * FROM users LIMIT 5;
```

### Performance Issues

#### Slow API Responses
1. Check Redis connection for caching
2. Monitor database query performance
3. Verify API rate limiting

#### High Memory Usage
1. Monitor Python process memory
2. Check for memory leaks in workers
3. Restart workers if needed

#### Frontend Loading Issues
1. Check network tab in browser dev tools
2. Verify API endpoints are responsive
3. Check for JavaScript console errors

## 🔄 Development Workflow

### Making Changes

1. **Backend Changes:**
   ```bash
   # Make your changes in backend/src/
   
   # Run tests
   cd backend && pytest tests/
   
   # The server will auto-reload with uvicorn
   ```

2. **Frontend Changes:**
   ```bash
   # Make your changes in frontend/src/
   
   # Changes will hot-reload automatically
   # Run tests
   cd frontend && npm test
   ```

### Adding New Features

1. **Backend API Endpoint:**
   ```python
   # Add to backend/src/main.py
   @app.get("/new-endpoint")
   def new_feature():
       return {"message": "New feature"}
   ```

2. **Frontend Component:**
   ```javascript
   // Create frontend/src/components/NewComponent.js
   import React from 'react';
   
   const NewComponent = () => {
       return <div>New Component</div>;
   };
   
   export default NewComponent;
   ```

3. **Database Changes:**
   ```bash
   # Create migration
   cd backend
   alembic revision --autogenerate -m "Add new table"
   
   # Apply migration
   alembic upgrade head
   ```

### Code Quality

#### Linting and Formatting
```bash
# Frontend
cd frontend
npm run lint
npm run format

# Backend (manual)
cd backend
source venv/bin/activate
black src/
flake8 src/
```

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 📊 Monitoring and Logging

### Application Logs
- Backend: `backend/logs/backend.log`
- Celery: `backend/logs/celery.log` 
- News Worker: `backend/logs/news_worker.log`

### Health Checks
- Backend Health: http://localhost:8000/
- Frontend Health: http://localhost:3000/
- Redis Health: `redis-cli ping`

### Performance Monitoring
- API Response Times: Built into FastAPI docs
- Database Queries: SQLAlchemy logging
- Memory Usage: `htop` or Activity Monitor

## 📚 Additional Resources

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Redis Documentation](https://redis.io/docs/)

### Fantasy Football APIs
- [ESPN API Guide](https://github.com/cwendt94/espn-api)
- [Sleeper API Documentation](https://docs.sleeper.app/)

### AI/ML Resources
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

## 🤝 Contributing

### Code Standards
- Python: Follow PEP 8, use type hints
- JavaScript: Use ESLint configuration
- Git: Use conventional commit messages

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request with detailed description

### Issue Reporting
- Use GitHub Issues
- Include detailed reproduction steps
- Provide environment information
- Include relevant logs

---

Need help? Check the [main README](README.md) or open an issue on GitHub.