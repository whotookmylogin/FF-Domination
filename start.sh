#!/bin/bash

# Fantasy Football Domination App - Master Startup Script
# ========================================================
# This script provides a complete one-command startup for the entire
# Fantasy Football application stack, including dependency checks,
# backend setup, frontend setup, and background services.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
REDIS_PORT=6379
POSTGRES_PORT=5432

# Process tracking
BACKEND_PID=""
FRONTEND_PID=""
REDIS_PID=""
CELERY_PID=""
NEWS_WORKER_PID=""

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

log_detail() {
    echo -e "${CYAN}[DETAIL]${NC} $1"
}

# Cleanup function to stop all processes on exit
cleanup() {
    echo ""
    log_info "Shutting down all services..."
    
    # Kill background processes
    if [[ -n "$NEWS_WORKER_PID" ]]; then
        kill $NEWS_WORKER_PID 2>/dev/null || true
        log_detail "News worker stopped"
    fi
    
    if [[ -n "$CELERY_PID" ]]; then
        kill $CELERY_PID 2>/dev/null || true
        log_detail "Celery worker stopped"
    fi
    
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_detail "Backend server stopped"
    fi
    
    if [[ -n "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_detail "Frontend server stopped"
    fi
    
    # Stop any remaining processes
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "start_news_worker" 2>/dev/null || true
    
    log_success "All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

# Banner
echo "========================================================="
echo -e "${GREEN}🏈 Fantasy Football Domination App Startup${NC}"
echo "========================================================="
echo ""

# Parse command line arguments
SKIP_DEPS=false
SKIP_DB=false
SKIP_FRONTEND=false
SKIP_WORKERS=false
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --skip-db)
            SKIP_DB=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --skip-workers)
            SKIP_WORKERS=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-deps      Skip dependency checks"
            echo "  --skip-db        Skip database initialization"
            echo "  --skip-frontend  Skip frontend startup"
            echo "  --skip-workers   Skip background workers"
            echo "  --dev            Development mode (verbose logging)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Enable debug mode
if [[ "$DEV_MODE" == "true" ]]; then
    set -x
fi

# Check if running from correct directory
if [[ ! -f "backend/requirements.txt" ]] || [[ ! -f "frontend/package.json" ]]; then
    log_error "Please run this script from the Fantasy Football app root directory"
    log_detail "Expected structure: backend/, frontend/, start.sh"
    exit 1
fi

# =====================================================
# STEP 1: System Dependency Checks
# =====================================================

if [[ "$SKIP_DEPS" != "true" ]]; then
    log_step "Checking system dependencies..."
    
    # Check Python
    log_info "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        log_detail "Install Python 3.8+ from https://python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        log_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    log_success "Python $PYTHON_VERSION found"
    
    # Check Node.js
    log_info "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        log_detail "Install Node.js 18+ from https://nodejs.org"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    if [[ $NODE_MAJOR -lt 18 ]]; then
        log_error "Node.js 18 or higher is required. Found: $NODE_VERSION"
        exit 1
    fi
    log_success "Node.js $NODE_VERSION found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    log_success "npm $(npm --version) found"
    
    # Check Redis
    log_info "Checking Redis availability..."
    if command -v redis-server &> /dev/null; then
        # Try to start Redis if not running
        if ! redis-cli ping &> /dev/null; then
            log_info "Starting Redis server..."
            if command -v brew &> /dev/null; then
                brew services start redis &> /dev/null || true
            elif systemctl is-active --quiet redis; then
                sudo systemctl start redis &> /dev/null || true
            else
                redis-server --daemonize yes --port $REDIS_PORT &> /dev/null || true
            fi
            sleep 2
        fi
        
        if redis-cli ping &> /dev/null; then
            log_success "Redis is running on port $REDIS_PORT"
        else
            log_warning "Redis is not responding. Some features may not work."
        fi
    else
        log_warning "Redis not found. Install with: brew install redis (macOS) or sudo apt install redis-server (Ubuntu)"
    fi
    
    log_success "Dependency checks completed"
fi

# =====================================================
# STEP 2: Backend Setup and Startup
# =====================================================

log_step "Setting up backend..."

cd backend

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
log_info "Installing backend dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
log_success "Backend dependencies installed"

# Database setup
if [[ "$SKIP_DB" != "true" ]]; then
    log_info "Setting up database..."
    
    # Run existing setup script database portion
    if [[ -f "alembic.ini" ]]; then
        if [[ -d "alembic/versions" ]] && [[ $(ls -1 alembic/versions/*.py 2>/dev/null | wc -l) -gt 0 ]]; then
            log_info "Running database migrations..."
            alembic upgrade head
            log_success "Database migrations completed"
        else
            log_info "Creating database schema..."
            python3 -c "
import sys
sys.path.append('src')
from database.connection import create_database, check_database_connection

if create_database():
    if check_database_connection():
        print('Database initialized successfully')
    else:
        print('Database connection failed')
        sys.exit(1)
else:
    print('Failed to create database schema')
    sys.exit(1)
" 2>/dev/null
            log_success "Database schema created"
        fi
    else
        log_warning "No alembic configuration found, skipping database setup"
    fi
fi

# Start backend server
log_info "Starting backend server on port $BACKEND_PORT..."
cd src
nohup python3 -c "
import uvicorn
from main import app

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=$BACKEND_PORT, log_level='info')
" > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3
if kill -0 $BACKEND_PID 2>/dev/null; then
    log_success "Backend server started (PID: $BACKEND_PID)"
    log_detail "Backend available at: http://localhost:$BACKEND_PORT"
else
    log_error "Backend server failed to start"
    log_detail "Check logs/backend.log for details"
    exit 1
fi

cd ..  # Back to backend directory
cd ..  # Back to root directory

# =====================================================
# STEP 3: Frontend Setup and Startup
# =====================================================

if [[ "$SKIP_FRONTEND" != "true" ]]; then
    log_step "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing frontend dependencies..."
        npm install --silent
        log_success "Frontend dependencies installed"
    else
        log_info "Frontend dependencies already installed"
    fi
    
    # Start frontend server
    log_info "Starting frontend server on port $FRONTEND_PORT..."
    nohup npm start > /dev/null 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    log_info "Waiting for frontend to initialize..."
    for i in {1..30}; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            break
        fi
        sleep 2
        if [[ $i -eq 30 ]]; then
            log_error "Frontend server failed to start"
            exit 1
        fi
    done
    
    log_success "Frontend server started (PID: $FRONTEND_PID)"
    log_detail "Frontend available at: http://localhost:$FRONTEND_PORT"
    
    cd ..  # Back to root directory
fi

# =====================================================
# STEP 4: Background Workers
# =====================================================

if [[ "$SKIP_WORKERS" != "true" ]]; then
    log_step "Starting background workers..."
    
    cd backend
    source venv/bin/activate
    
    # Start Celery worker for background tasks
    log_info "Starting Celery worker..."
    nohup celery -A src.news.scheduler worker --loglevel=info > logs/celery.log 2>&1 &
    CELERY_PID=$!
    
    # Start news aggregation worker
    if [[ -f "start_news_worker.py" ]]; then
        log_info "Starting news aggregation worker..."
        nohup python3 start_news_worker.py > logs/news_worker.log 2>&1 &
        NEWS_WORKER_PID=$!
        log_success "News worker started (PID: $NEWS_WORKER_PID)"
    fi
    
    log_success "Background workers started"
    
    cd ..  # Back to root directory
fi

# =====================================================
# STEP 5: Final Status and Instructions
# =====================================================

echo ""
echo "========================================================="
echo -e "${GREEN}🎉 FANTASY FOOTBALL APP IS RUNNING! 🎉${NC}"
echo "========================================================="
echo ""

# Display service status
echo -e "${CYAN}Service Status:${NC}"
if [[ -n "$BACKEND_PID" ]]; then
    echo -e "  ✅ Backend API:      http://localhost:$BACKEND_PORT"
    echo -e "     └─ API Docs:      http://localhost:$BACKEND_PORT/docs"
fi

if [[ "$SKIP_FRONTEND" != "true" && -n "$FRONTEND_PID" ]]; then
    echo -e "  ✅ Frontend:         http://localhost:$FRONTEND_PORT"
fi

if redis-cli ping &> /dev/null; then
    echo -e "  ✅ Redis:            localhost:$REDIS_PORT"
else
    echo -e "  ⚠️  Redis:            Not running (optional)"
fi

if [[ -n "$CELERY_PID" ]]; then
    echo -e "  ✅ Celery Worker:    Running (PID: $CELERY_PID)"
fi

if [[ -n "$NEWS_WORKER_PID" ]]; then
    echo -e "  ✅ News Worker:      Running (PID: $NEWS_WORKER_PID)"
fi

echo ""
echo -e "${CYAN}Quick Links:${NC}"
echo -e "  📊 Main Dashboard:   http://localhost:$FRONTEND_PORT"
echo -e "  🔧 API Explorer:     http://localhost:$BACKEND_PORT/docs"
echo -e "  📰 News Feed:        http://localhost:$FRONTEND_PORT/news"
echo -e "  🤝 Trade Analysis:   http://localhost:$FRONTEND_PORT/trades"

echo ""
echo -e "${CYAN}Useful Commands:${NC}"
echo -e "  Stop all services:   ./stop.sh"
echo -e "  View logs:           tail -f backend/logs/*.log"
echo -e "  Test API:            curl http://localhost:$BACKEND_PORT/"

echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Configure your .env file with API keys"
echo -e "  2. Import your fantasy team data"
echo -e "  3. Set up notifications in the app"

echo ""
log_info "Press Ctrl+C to stop all services"
echo ""

# Health check
sleep 2
log_info "Running health checks..."

# Check backend health
if curl -s http://localhost:$BACKEND_PORT/ > /dev/null; then
    log_success "Backend health check passed"
else
    log_warning "Backend health check failed"
fi

# Check frontend health (if running)
if [[ "$SKIP_FRONTEND" != "true" ]]; then
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
        log_success "Frontend health check passed"
    else
        log_warning "Frontend health check failed"
    fi
fi

# Keep script running to monitor services
log_info "Monitoring services... (Press Ctrl+C to stop)"

# Monitor processes and restart if they crash
while true; do
    sleep 10
    
    # Check if backend is still running
    if [[ -n "$BACKEND_PID" ]] && ! kill -0 $BACKEND_PID 2>/dev/null; then
        log_warning "Backend process died, attempting restart..."
        cd backend/src
        nohup python3 -c "
import uvicorn
from main import app

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=$BACKEND_PORT, log_level='info')
" > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
        cd ../..
        log_info "Backend restarted (PID: $BACKEND_PID)"
    fi
    
    # Check if frontend is still running (if enabled)
    if [[ "$SKIP_FRONTEND" != "true" && -n "$FRONTEND_PID" ]] && ! kill -0 $FRONTEND_PID 2>/dev/null; then
        log_warning "Frontend process died, attempting restart..."
        cd frontend
        nohup npm start > /dev/null 2>&1 &
        FRONTEND_PID=$!
        cd ..
        log_info "Frontend restarted (PID: $FRONTEND_PID)"
    fi
done