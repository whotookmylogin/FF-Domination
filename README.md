# Fantasy Football Domination App 🏈

AI-driven fantasy football assistance to transform casual players into league champions.

## 🚀 Quick Start

**Get the entire app running in one command:**

```bash
git clone <repository-url>
cd fantasy-football-app
./start.sh
```

That's it! The script will:
- ✅ Check all dependencies (Python, Node.js, Redis)
- ✅ Set up the backend and frontend
- ✅ Initialize the database
- ✅ Start all services
- ✅ Provide health monitoring

**Access your app:**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API Docs**: http://localhost:8000/docs
- 📊 **Dashboard**: http://localhost:3000

**Stop all services:**
```bash
./stop.sh
```

## 🎯 What This App Does

The Fantasy Football Domination App leverages AI-driven analysis and automation to help fantasy football players maximize their win rate with minimal time investment. By combining real-time data aggregation, predictive analytics, and intelligent automation, users gain a 24/7 fantasy assistant that executes optimal strategies.

### ⭐ Key Features

- **🤖 AI Performance Predictions**: Proprietary AI model trained on 20+ years of fantasy data
- **📰 Real-time News Analysis**: Sub-second reaction time to breaking news with automated alerts
- **🤝 Smart Trade Suggestions**: Fairness scoring and win probability calculations for trades
- **🔗 Multi-platform Support**: Integration with ESPN and Sleeper fantasy platforms
- **📱 Push Notifications**: iOS/Android notifications for critical news and actions
- **📈 Advanced Analytics**: Player performance trends, matchup analysis, and projections
- **⚡ Automated Actions**: Set-and-forget lineup optimization and waiver claims

## 📋 System Requirements

### Required Software
- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Redis** (for caching - optional but recommended)

### Quick Installation

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
- Use WSL for Redis

## 🏗️ Alternative Setup Methods

### Option 1: One-Command Native Setup (Recommended)
```bash
./start.sh
```
- Fastest startup
- Native performance
- Automatic dependency management
- Built-in health monitoring

### Option 2: Docker Development Environment
```bash
docker-compose up
```
- Consistent environment
- Includes all services (Redis, PostgreSQL)
- Development tools included
- Easy cleanup

### Option 3: Manual Setup
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py

# Frontend (new terminal)
cd frontend
npm install
npm start
```

## 📖 Documentation

- **📘 [Development Guide](DEVELOPMENT.md)** - Detailed setup, API docs, troubleshooting
- **🏛️ [Architecture](ARCHITECTURE.md)** - System design and technical overview
- **🗺️ [MVP Roadmap](MVP_ROADMAP.md)** - Feature timeline and milestones

## 🔧 Configuration

### Quick Configuration

1. **Start the app**: `./start.sh`
2. **Configure APIs**: Edit `backend/.env` with your API keys
3. **Import teams**: Use the web interface at http://localhost:3000

### API Keys Setup

Create `backend/.env` file:

```bash
# Fantasy Platforms
ESPN_COOKIE=your_espn_cookie_here
SLEEPER_TOKEN=your_sleeper_token_here

# News APIs
ROTOWIRE_API_KEY=your_rotowire_key_here

# AI Services (optional)
OPENAI_API_KEY=your_openai_key_here

# Notifications (optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**Getting API Keys:**
- **ESPN**: Copy cookies from browser (see [Development Guide](DEVELOPMENT.md))
- **Sleeper**: No key needed - uses public API
- **RotowWire**: Sign up at [rotowire.com](https://rotowire.com)
- **OpenAI**: Get key from [platform.openai.com](https://platform.openai.com)

## 🚨 Troubleshooting

### Common Issues & Quick Fixes

**"Backend won't start"**
```bash
cd backend && source venv/bin/activate && pip install -r requirements.txt
```

**"Frontend won't start"**
```bash
cd frontend && npm install
```

**"Port already in use"**
```bash
./stop.sh --force  # Force stop all processes
./start.sh         # Restart
```

**"Redis connection failed"**
```bash
# macOS
brew services start redis

# Ubuntu
sudo systemctl start redis
```

**More help:** See the detailed [Development Guide](DEVELOPMENT.md#troubleshooting)

## 🎮 Quick Usage Guide

### 1. Import Your Fantasy Teams
- Open http://localhost:3000
- Go to "Team Import"
- Connect ESPN or Sleeper account
- Import your league data

### 2. Get AI Trade Analysis
- Navigate to "AI Trade Discovery"
- Click "Analyze League Trades"
- Review AI-powered trade suggestions

### 3. Set Up Notifications
- Go to Settings
- Configure push notifications
- Set lineup reminders
- Enable breaking news alerts

### 4. Monitor Performance
- Check the Dashboard for key insights
- Review team analytics
- Track player performance trends

## 🏃‍♂️ Development Workflow

### Making Changes
```bash
# Backend changes auto-reload
# Frontend changes hot-reload
# Just edit files and see changes instantly
```

### Running Tests
```bash
# Backend tests
cd backend && pytest tests/

# Frontend tests  
cd frontend && npm test

# Full test suite
./start.sh && pytest backend/tests/
```

### Adding Features
- Backend: Add endpoints in `backend/src/main.py`
- Frontend: Add components in `frontend/src/components/`
- Database: Create migrations with `alembic revision`

## 🤝 Contributing

### Quick Contribution Guide
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Test** your changes: `./start.sh && npm test`
4. **Commit** your changes: `git commit -m 'Add amazing feature'`
5. **Push** to branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request

### Development Standards
- Python: Follow PEP 8, use type hints
- JavaScript: Use ESLint configuration
- Tests: Write tests for new features
- Documentation: Update docs for major changes

## 📊 System Architecture

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
                         └─────────────────┘
```

## 🎯 Project Status

**Current Phase: MVP Development**

- ✅ Backend API (FastAPI)
- ✅ Frontend Dashboard (React)
- ✅ ESPN/Sleeper Integration
- ✅ AI Trade Analysis
- ✅ News Aggregation
- ✅ Push Notifications
- 🚧 Advanced Analytics (in progress)
- 📋 Mobile App (planned)

See [MVP Roadmap](MVP_ROADMAP.md) for detailed timeline.

## 📞 Support

**Need Help?**
- 📚 Check the [Development Guide](DEVELOPMENT.md)
- 🐛 Report issues on [GitHub Issues](../../issues)
- 💬 Join our community discussions
- ✉️ Email: support@fantasyapp.com

**Quick Links:**
- [API Documentation](http://localhost:8000/docs) (when running)
- [Architecture Guide](ARCHITECTURE.md)
- [Development Setup](DEVELOPMENT.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⚡ Ready to dominate your fantasy league? Run `./start.sh` and get started!**
