#!/bin/bash

# Fantasy Football Domination App - Shutdown Script
# ==================================================
# This script cleanly stops all Fantasy Football application services
# and background processes.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

# Parse command line arguments
FORCE_KILL=false
KEEP_DOCKER=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_KILL=true
            shift
            ;;
        --keep-docker)
            KEEP_DOCKER=true
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force          Force kill all processes (SIGKILL)"
            echo "  --keep-docker    Don't stop Docker containers"
            echo "  --quiet, -q      Suppress output messages"
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

# Function to log conditionally
conditional_log() {
    if [[ "$QUIET" != "true" ]]; then
        $1 "$2"
    fi
}

# Banner
if [[ "$QUIET" != "true" ]]; then
    echo "========================================================="
    echo -e "${RED}🛑 Fantasy Football App Shutdown${NC}"
    echo "========================================================="
    echo ""
fi

conditional_log log_step "Stopping Fantasy Football application services..."

# =====================================================
# STEP 1: Stop Application Processes
# =====================================================

conditional_log log_info "Stopping application processes..."

# Function to stop process gracefully or force kill
stop_process() {
    local process_name=$1
    local search_pattern=$2
    local display_name=${3:-$process_name}
    
    local pids=$(pgrep -f "$search_pattern" 2>/dev/null || true)
    
    if [[ -n "$pids" ]]; then
        conditional_log log_info "Stopping $display_name processes..."
        
        for pid in $pids; do
            if [[ "$FORCE_KILL" == "true" ]]; then
                kill -9 $pid 2>/dev/null || true
            else
                # Try graceful shutdown first
                kill -TERM $pid 2>/dev/null || true
                
                # Wait up to 10 seconds for graceful shutdown
                for i in {1..10}; do
                    if ! kill -0 $pid 2>/dev/null; then
                        break
                    fi
                    sleep 1
                done
                
                # Force kill if still running
                if kill -0 $pid 2>/dev/null; then
                    conditional_log log_warning "Force killing $display_name process $pid"
                    kill -9 $pid 2>/dev/null || true
                fi
            fi
        done
        
        conditional_log log_success "$display_name stopped"
    else
        conditional_log log_info "No $display_name processes found"
    fi
}

# Stop specific Fantasy Football processes
stop_process "backend" "uvicorn.*main:app" "Backend API"
stop_process "frontend" "react-scripts start" "Frontend"
stop_process "celery_worker" "celery.*worker" "Celery Worker"
stop_process "celery_beat" "celery.*beat" "Celery Beat"
stop_process "news_worker" "start_news_worker" "News Worker"

# Stop any remaining Python processes from the app
stop_process "python_main" "python.*main.py" "Python Main"
stop_process "python_src" "python.*src/" "Python Source"

# =====================================================
# STEP 2: Stop Docker Services
# =====================================================

if [[ "$KEEP_DOCKER" != "true" ]]; then
    conditional_log log_step "Stopping Docker containers..."
    
    # Check if docker-compose is available and running
    if command -v docker-compose &> /dev/null; then
        if [[ -f "docker-compose.yml" ]]; then
            conditional_log log_info "Stopping Docker Compose services..."
            
            if [[ "$QUIET" == "true" ]]; then
                docker-compose down --remove-orphans > /dev/null 2>&1 || true
            else
                docker-compose down --remove-orphans || true
            fi
            
            conditional_log log_success "Docker services stopped"
        else
            conditional_log log_warning "docker-compose.yml not found, skipping Docker shutdown"
        fi
    else
        conditional_log log_warning "docker-compose not found, skipping Docker shutdown"
    fi
    
    # Stop individual containers if they exist
    conditional_log log_info "Stopping individual Fantasy Football containers..."
    
    local containers=(
        "ff_backend"
        "ff_frontend" 
        "ff_redis"
        "ff_postgres"
        "ff_celery_worker"
        "ff_celery_beat"
        "ff_news_worker"
        "ff_nginx"
        "ff_redis_commander"
        "ff_pgadmin"
        "ff_flower"
    )
    
    for container in "${containers[@]}"; do
        if docker ps -q -f name=$container > /dev/null 2>&1; then
            conditional_log log_info "Stopping container: $container"
            if [[ "$QUIET" == "true" ]]; then
                docker stop $container > /dev/null 2>&1 || true
                docker rm $container > /dev/null 2>&1 || true
            else
                docker stop $container 2>/dev/null || true
                docker rm $container 2>/dev/null || true
            fi
        fi
    done
fi

# =====================================================
# STEP 3: Clean Up Ports
# =====================================================

conditional_log log_step "Cleaning up ports..."

# Function to kill processes on specific ports
cleanup_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [[ -n "$pid" ]]; then
        conditional_log log_info "Freeing port $port ($service_name)"
        if [[ "$FORCE_KILL" == "true" ]]; then
            kill -9 $pid 2>/dev/null || true
        else
            kill -TERM $pid 2>/dev/null || true
            sleep 2
            # Force kill if still there
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null || true
            fi
        fi
    fi
}

# Clean up common ports
cleanup_port 3000 "Frontend"
cleanup_port 8000 "Backend API"
cleanup_port 6379 "Redis"
cleanup_port 5432 "PostgreSQL"
cleanup_port 5555 "Flower"
cleanup_port 8080 "pgAdmin"
cleanup_port 8081 "Redis Commander"

# =====================================================
# STEP 4: Clean Up Temporary Files
# =====================================================

conditional_log log_step "Cleaning up temporary files..."

# Remove PID files
if [[ -f "backend/app.pid" ]]; then
    rm -f backend/app.pid
    conditional_log log_info "Removed backend PID file"
fi

if [[ -f "frontend/app.pid" ]]; then
    rm -f frontend/app.pid
    conditional_log log_info "Removed frontend PID file"
fi

# Clean up log files if they're too large (over 100MB)
if [[ -d "backend/logs" ]]; then
    find backend/logs -name "*.log" -size +100M -exec truncate -s 0 {} \; 2>/dev/null || true
    conditional_log log_info "Truncated large log files"
fi

# Remove temporary development files
rm -f .DS_Store 2>/dev/null || true
rm -rf **/.DS_Store 2>/dev/null || true

# =====================================================
# STEP 5: Verification
# =====================================================

conditional_log log_step "Verifying shutdown..."

# Check if any processes are still running
still_running=false

# Check for application processes
for pattern in "uvicorn.*main:app" "react-scripts start" "celery.*worker" "celery.*beat" "start_news_worker"; do
    if pgrep -f "$pattern" > /dev/null 2>&1; then
        conditional_log log_warning "Some $pattern processes may still be running"
        still_running=true
    fi
done

# Check if ports are free
for port in 3000 8000 6379 5432; do
    if lsof -i:$port > /dev/null 2>&1; then
        conditional_log log_warning "Port $port may still be in use"
        still_running=true
    fi
done

# =====================================================
# STEP 6: Final Status
# =====================================================

if [[ "$QUIET" != "true" ]]; then
    echo ""
    if [[ "$still_running" == "true" ]]; then
        echo "========================================================="
        echo -e "${YELLOW}⚠️  PARTIAL SHUTDOWN COMPLETED${NC}"
        echo "========================================================="
        echo ""
        echo -e "${YELLOW}Some processes or ports may still be in use.${NC}"
        echo "Use --force flag to force kill all processes:"
        echo "  ./stop.sh --force"
        echo ""
        echo "Or check manually:"
        echo "  ps aux | grep -E '(uvicorn|react-scripts|celery)'"
        echo "  lsof -i :3000"
        echo "  lsof -i :8000"
    else
        echo "========================================================="
        echo -e "${GREEN}✅ SHUTDOWN COMPLETED SUCCESSFULLY${NC}"
        echo "========================================================="
        echo ""
        echo -e "${GREEN}All Fantasy Football services have been stopped.${NC}"
        echo ""
        echo "To start the application again:"
        echo "  ./start.sh"
    fi
    
    echo ""
fi

# Exit with appropriate code
if [[ "$still_running" == "true" ]]; then
    exit 1
else
    exit 0
fi