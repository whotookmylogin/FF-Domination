import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './screens/Dashboard';
import TeamAnalysis from './screens/TeamAnalysis';
import TradeSuggestions from './screens/TradeSuggestions';
import WaiverWire from './screens/WaiverWire';
import NewsFeed from './screens/NewsFeed';
import AITradeDiscovery from './screens/AITradeDiscovery';
import ExpertDraftTool from './screens/ExpertDraftTool';
import TeamRosters from './screens/TeamRosters';
import TeamImport from './screens/TeamImport';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import './styles/App.css';

function App() {
  const [user, setUser] = useState(null);
  const [leagues, setLeagues] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchRealData = async () => {
      try {
        setLoading(true);
        
        // Fetch user team data from backend
        const response = await fetch('http://localhost:8000/user/team/7');
        const data = await response.json();
        
        if (data.status === 'success') {
          // Set user data from real ESPN data
          const realUser = {
            id: data.data.user_id,
            name: data.data.team_name,
            email: 'user@example.com'
          };
          
          // Set leagues data with real team info
          const realLeagues = [
            {
              id: '83806',
              name: data.data.team_name,
              platform: 'ESPN',
              season: 2024,
              currentWeek: 18,
              record: `${data.data.wins}-${data.data.losses}-${data.data.ties}`,
              pointsFor: data.data.points_for,
              pointsAgainst: data.data.points_against
            }
          ];
          
          setUser(realUser);
          setLeagues(realLeagues);
          setSelectedLeague(realLeagues[0]);
        } else {
          setError('Failed to fetch league data');
        }
      } catch (err) {
        setError('Error connecting to backend API');
        console.error('Error fetching real data:', err);
        
        // Fallback to mock data if API fails
        const mockUser = {
          id: 'user123',
          name: 'Fantasy Manager',
          email: 'user@example.com'
        };
        
        const mockLeagues = [
          {
            id: 'league1',
            name: 'Championship Chasers',
            platform: 'ESPN',
            season: 2025,
            currentWeek: 1
          }
        ];
        
        setUser(mockUser);
        setLeagues(mockLeagues);
        setSelectedLeague(mockLeagues[0]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRealData();
  }, []);

  const handleTeamImported = (teamData) => {
    console.log('Team imported:', teamData);
    // Here you would typically update your app state with the new team
    // For now, we'll just log it and potentially refresh the leagues
    
    // You could add the imported team to the leagues array
    const newLeague = {
      id: teamData.leagueId,
      name: teamData.teamName,
      platform: teamData.platform,
      season: 2024,
      currentWeek: 18,
      record: teamData.record,
      pointsFor: teamData.pointsFor
    };
    
    // Add to leagues if not already present
    const existingLeague = leagues.find(l => l.id === newLeague.id && l.platform === newLeague.platform);
    if (!existingLeague) {
      setLeagues(prev => [...prev, newLeague]);
      setSelectedLeague(newLeague);
    }
  };
  
  return (
    <Router>
      <div className="app-container">
        <Header user={user} selectedLeague={selectedLeague} leagues={leagues} onLeagueChange={setSelectedLeague} />
        <div className="app-layout">
          <Sidebar leagues={leagues} selectedLeague={selectedLeague} onLeagueChange={setSelectedLeague} />
          <main className="app-content">
            <Routes>
              <Route path="/" element={<Dashboard league={selectedLeague} />} />
              <Route path="/team-analysis" element={<TeamAnalysis league={selectedLeague} />} />
              <Route path="/team-rosters" element={<TeamRosters league={selectedLeague} />} />
              <Route path="/team-import" element={<TeamImport onTeamImported={handleTeamImported} />} />
              <Route path="/trade-suggestions" element={<TradeSuggestions league={selectedLeague} />} />
              <Route path="/ai-trade-discovery" element={<AITradeDiscovery league={selectedLeague} />} />
              <Route path="/expert-draft-tool" element={<ExpertDraftTool league={selectedLeague} />} />
              <Route path="/waiver-wire" element={<WaiverWire league={selectedLeague} />} />
              <Route path="/news" element={<NewsFeed league={selectedLeague} />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
