#!/usr/bin/env python3
"""
Script to start the Celery worker for news aggregation background tasks.

Usage:
    python start_news_worker.py worker  # Start worker
    python start_news_worker.py beat    # Start scheduler
    python start_news_worker.py both    # Start both worker and scheduler
"""

import sys
import os
import subprocess
import signal
from pathlib import Path

# Add the src directory to the Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(backend_dir))

def start_worker():
    """Start the Celery worker."""
    print("Starting Celery worker for news aggregation...")
    os.system("celery -A src.news.scheduler worker --loglevel=info --concurrency=2")

def start_beat():
    """Start the Celery beat scheduler."""
    print("Starting Celery beat scheduler for news aggregation...")
    os.system("celery -A src.news.scheduler beat --loglevel=info")

def start_both():
    """Start both worker and beat scheduler."""
    print("Starting both Celery worker and beat scheduler...")
    
    # Start beat scheduler in background
    beat_process = subprocess.Popen([
        "celery", "-A", "src.news.scheduler", "beat", "--loglevel=info"
    ])
    
    try:
        # Start worker in foreground
        subprocess.run([
            "celery", "-A", "src.news.scheduler", "worker", 
            "--loglevel=info", "--concurrency=2"
        ])
    except KeyboardInterrupt:
        print("\nStopping processes...")
        beat_process.terminate()
        beat_process.wait()

def show_help():
    """Show usage information."""
    print(__doc__)

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "worker":
        start_worker()
    elif command == "beat":
        start_beat()
    elif command == "both":
        start_both()
    elif command in ["-h", "--help", "help"]:
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()