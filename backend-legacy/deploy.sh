#!/bin/bash

# Deployment script for Fantasy Football Domination App

# Exit on any error
set -e

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations (if any)
echo "Running database migrations..."
# python src/database/migrate.py

# Start the application
echo "Starting the application..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Deactivate virtual environment on exit
deactivate
