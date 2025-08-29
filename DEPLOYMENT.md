# Fantasy Football Domination App - Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## Deployment Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd FantasyFootball
   ```

2. Navigate to the backend directory:
   ```
   cd backend
   ```

3. Run the deployment script:
   ```
   ./deploy.sh
   ```

   This script will:
   - Create a virtual environment if it doesn't exist
   - Install all required dependencies
   - Start the application server

## Environment Variables

The application requires the following environment variables:

- `ESPN_COOKIE` - ESPN authentication cookie for accessing ESPN fantasy football data
- `SLEEPER_TOKEN` - Sleeper API bearer token for accessing Sleeper fantasy football data
- `FIREBASE_SERVER_KEY` - Firebase server key for push notifications
- `DATABASE_URL` - PostgreSQL database connection string

## Manual Deployment

If you prefer to deploy manually, follow these steps:

1. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```
   export ESPN_COOKIE="your_espn_cookie"
   export SLEEPER_TOKEN="your_sleeper_token"
   export FIREBASE_SERVER_KEY="your_firebase_key"
   export DATABASE_URL="postgresql://user:password@localhost/dbname"
   ```

4. Start the application:
   ```
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

## Testing

Run the test suite to ensure everything is working correctly:

```
python -m pytest tests/
```

## Monitoring

The application includes built-in logging and monitoring. Check the logs for any errors or warnings.

## Troubleshooting

If you encounter issues:

1. Verify all environment variables are set correctly
2. Check that all dependencies are installed
3. Ensure the database is accessible and properly configured
4. Check the application logs for error messages
