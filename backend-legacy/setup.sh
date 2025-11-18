#!/bin/bash

# Fantasy Football App Backend Setup Script
# ========================================
# This script sets up the backend environment, installs dependencies,
# and initializes the database for local development.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if running from the backend directory
if [[ ! -f "requirements.txt" ]]; then
    log_error "Please run this script from the backend directory"
    exit 1
fi

log_info "Starting Fantasy Football App Backend Setup..."

# Check Python version
log_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    log_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
log_success "Python version check passed: $(python3 --version)"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    log_warning ".env file not found. Please make sure to configure your environment variables."
else
    log_success ".env file found"
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    log_info "Creating virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
log_info "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional dependencies for development
log_info "Installing development dependencies..."
pip install python-dotenv python-multipart

# Check if Redis is running (optional)
log_info "Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        log_success "Redis is running"
    else
        log_warning "Redis is not running. Some features may not work properly."
        log_info "To start Redis: brew services start redis (macOS) or sudo systemctl start redis (Linux)"
    fi
else
    log_warning "Redis CLI not found. Install Redis for full functionality."
    log_info "macOS: brew install redis"
    log_info "Ubuntu/Debian: sudo apt-get install redis-server"
fi

# Create necessary directories
log_info "Creating necessary directories..."
mkdir -p logs
mkdir -p backups
mkdir -p data
mkdir -p temp

# Initialize Alembic (database migrations)
log_info "Initializing database migrations..."
if [[ ! -f "alembic.ini" ]]; then
    log_error "alembic.ini not found. Database migrations cannot be initialized."
    exit 1
fi

# Check if alembic versions directory exists and has migration files
if [[ -d "alembic/versions" ]] && [[ $(ls -1 alembic/versions/*.py 2>/dev/null | wc -l) -gt 0 ]]; then
    log_info "Running database migrations..."
    alembic upgrade head
    log_success "Database migrations completed"
else
    log_warning "No migration files found. Creating initial database schema..."
    # Create database tables directly using Python
    python3 -c "
import sys
sys.path.append('src')
from database.connection import create_database, check_database_connection

if create_database():
    print('Database schema created successfully')
    if check_database_connection():
        print('Database connection verified')
    else:
        print('Database connection failed')
        sys.exit(1)
else:
    print('Failed to create database schema')
    sys.exit(1)
"
fi

# Generate encryption key if not present in .env
log_info "Checking encryption key configuration..."
if [[ -f ".env" ]]; then
    if grep -q "CREDENTIAL_ENCRYPTION_KEY=generate-this" .env || ! grep -q "CREDENTIAL_ENCRYPTION_KEY=" .env; then
        log_info "Generating encryption key..."
        ENCRYPTION_KEY=$(python3 -c "
import sys
sys.path.append('src')
from config.credentials import CredentialManager
print(CredentialManager.generate_encryption_key())
")
        # Update .env file with generated key
        if grep -q "CREDENTIAL_ENCRYPTION_KEY=" .env; then
            sed -i.bak "s/CREDENTIAL_ENCRYPTION_KEY=.*/CREDENTIAL_ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
        else
            echo "CREDENTIAL_ENCRYPTION_KEY=$ENCRYPTION_KEY" >> .env
        fi
        log_success "Encryption key generated and added to .env file"
    else
        log_success "Encryption key already configured"
    fi
fi

# Create a simple test script
log_info "Creating database test script..."
cat > test_db_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Simple script to test database connection and basic functionality.
"""
import sys
import os

# Add src to path
sys.path.append('src')

from database.connection import check_database_connection, SessionLocal
from database.models import User, League
from datetime import datetime
import uuid

def test_database():
    """Test basic database operations."""
    print("Testing database connection...")
    
    if not check_database_connection():
        print("❌ Database connection failed")
        return False
    
    print("✅ Database connection successful")
    
    # Test creating a session
    try:
        db = SessionLocal()
        
        # Test query
        result = db.execute("SELECT COUNT(*) as count FROM users").fetchone()
        print(f"✅ Database query successful. Users count: {result[0] if result else 'N/A'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database operation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
EOF

# Make test script executable
chmod +x test_db_connection.py

# Run database test
log_info "Testing database connection..."
if python3 test_db_connection.py; then
    log_success "Database test passed"
else
    log_error "Database test failed"
    exit 1
fi

# Create run script for easy startup
log_info "Creating run script..."
cat > run.sh << 'EOF'
#!/bin/bash
# Quick start script for Fantasy Football Backend

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [[ -f ".env" ]]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the FastAPI server
echo "Starting Fantasy Football Backend..."
echo "API will be available at: http://localhost:${PORT:-8000}"
echo "Press Ctrl+C to stop"

cd src
python main.py
EOF

chmod +x run.sh

# Create stop script
log_info "Creating stop script..."
cat > stop.sh << 'EOF'
#!/bin/bash
# Stop all Fantasy Football backend processes

echo "Stopping Fantasy Football backend..."

# Kill any running uvicorn processes
pkill -f "uvicorn.*main:app" 2>/dev/null || true

# Kill any running Python processes related to this app
pkill -f "python.*main.py" 2>/dev/null || true

echo "Backend stopped"
EOF

chmod +x stop.sh

# Final setup verification
log_info "Running final setup verification..."

# Check if all critical files exist
CRITICAL_FILES=(
    ".env"
    "requirements.txt"
    "alembic.ini"
    "src/main.py"
    "src/database/connection.py"
    "src/database/models.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "✅ $file exists"
    else
        log_error "❌ $file is missing"
        exit 1
    fi
done

# Check if critical directories exist
CRITICAL_DIRS=(
    "alembic/versions"
    "src/database"
    "logs"
    "venv"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        log_success "✅ $dir directory exists"
    else
        log_error "❌ $dir directory is missing"
        exit 1
    fi
done

# Display setup summary
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 SETUP COMPLETED SUCCESSFULLY! 🎉${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review and configure .env file with your API keys and credentials"
echo "2. Start Redis server if you plan to use caching features"
echo "3. Run './run.sh' to start the backend server"
echo ""
echo "Available scripts:"
echo "  ./run.sh                 - Start the backend server"
echo "  ./stop.sh                - Stop the backend server"
echo "  ./test_db_connection.py  - Test database connectivity"
echo ""
echo "Database file: fantasy_football.db"
echo "Logs directory: logs/"
echo "Virtual environment: venv/"
echo ""
log_info "Setup completed in $(pwd)"
echo ""