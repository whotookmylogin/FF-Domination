from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Fantasy Football Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Fantasy Football Mock API Running"}

@app.get("/api/teams")
def get_teams():
    return {"teams": [
        {"id": 1, "name": "Team Alpha", "owner": "John Doe"},
        {"id": 2, "name": "Team Beta", "owner": "Jane Smith"}
    ]}

@app.get("/api/players")
def get_players():
    return {"players": [
        {"id": 1, "name": "Patrick Mahomes", "position": "QB", "team": "KC"},
        {"id": 2, "name": "Christian McCaffrey", "position": "RB", "team": "SF"}
    ]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)