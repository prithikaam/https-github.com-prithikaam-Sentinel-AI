import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import KyberVisualizer from './components/KyberVisualizer';
import Assistant from './components/Assistant';
import Simulator from './components/Simulator';
import Login from './components/Login';

// Prototype Helper: Capitalize user names in UI
String.prototype.capitalize = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [assistantQuery, setAssistantQuery] = useState('');

  // Check if session token exists
  useEffect(() => {
    const token = localStorage.getItem('sentinel_token');
    const storedUser = localStorage.getItem('sentinel_user');
    if (token && storedUser) {
      setIsLoggedIn(true);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    const storedUser = localStorage.getItem('sentinel_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_user');
    setIsLoggedIn(false);
    setUser(null);
    setActiveTab('dashboard');
  };

  // Switch tabs and pre-fill AI Assistant chat box
  const handleAskAssistant = (query) => {
    setAssistantQuery(query);
    setActiveTab('assistant');
    // Invalidate query after rendering so user can chat normally
    setTimeout(() => {
      setAssistantQuery('');
    }, 100);
  };

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="app-container">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        user={user} 
        onLogout={handleLogout} 
      />
      <div className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard onAskAssistant={handleAskAssistant} />
        )}
        {activeTab === 'kyber' && (
          <KyberVisualizer />
        )}
        {activeTab === 'assistant' && (
          <Assistant initialQuery={assistantQuery} />
        )}
        {activeTab === 'simulator' && (
          <Simulator />
        )}
      </div>
    </div>
  );
}
