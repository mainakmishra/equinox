
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import ChatPage from './pages/Chat/ChatPage';
import './App.css';
import HomePage from './pages/Home/HomePage';
import AgentsPage from './pages/Agents/AgentsPage';
import SettingsPage from './pages/Settings/SettingsPage';
import NotesPage from './pages/Productivity/NotesPage';
import TodosPage from './pages/Productivity/TodosPage';
import WellnessPage from './pages/Wellness/WellnessPage';
import HealthLogPopup from './components/HealthLogPopup/HealthLogPopup';
import { getTodayHealth } from './api/healthApi';

function AppRoutes() {
  const location = useLocation();
  const [showHealthPopup, setShowHealthPopup] = useState(false);
  const [healthChecked, setHealthChecked] = useState(false);

  // Check if user has logged health today (only on signed-in pages, not on home)
  useEffect(() => {
    const isSignedIn = localStorage.getItem('signedIn') === 'true';
    const isHomePage = location.pathname === '/';
    const isWellnessPage = location.pathname === '/wellness';

    // Only check if signed in, not on home page, not on wellness page, and not already checked
    if (isSignedIn && !isHomePage && !isWellnessPage && !healthChecked) {
      getTodayHealth()
        .then(log => {
          if (!log) {
            setShowHealthPopup(true);
          }
          setHealthChecked(true);
        })
        .catch(() => {
          // On error (including 404), show popup
          setShowHealthPopup(true);
          setHealthChecked(true);
        });
    }
  }, [location.pathname, healthChecked]);

  const handlePopupClose = () => {
    setShowHealthPopup(false);
  };

  const handleHealthLogged = () => {
    setHealthChecked(true);
  };

  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:email/:threadId" element={<ChatPage />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/notes" element={<NotesPage />} />
        <Route path="/todos" element={<TodosPage />} />
        <Route path="/wellness" element={<WellnessPage />} />
      </Routes>

      {showHealthPopup && (
        <HealthLogPopup
          onClose={handlePopupClose}
          onLogged={handleHealthLogged}
        />
      )}
    </>
  );
}


function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
