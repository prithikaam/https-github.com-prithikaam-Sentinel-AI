import React from 'react';
import { Shield, LayoutDashboard, Cpu, Bot, LogOut, Sliders } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, user, onLogout }) {
  return (
    <div className="sidebar">
      <div className="logo-container">
        <Shield size={28} className="logo-icon" />
        <span className="logo-text">SentinelAI</span>
      </div>

      <ul className="nav-links">
        <li>
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </div>
        </li>
        <li>
          <div 
            className={`nav-item ${activeTab === 'kyber' ? 'active' : ''}`}
            onClick={() => setActiveTab('kyber')}
          >
            <Cpu size={20} />
            <span>Kyber Cryptography</span>
          </div>
        </li>
        <li>
          <div 
            className={`nav-item ${activeTab === 'assistant' ? 'active' : ''}`}
            onClick={() => setActiveTab('assistant')}
          >
            <Bot size={20} />
            <span>AI Assistant</span>
          </div>
        </li>
        <li>
          <div 
            className={`nav-item ${activeTab === 'simulator' ? 'active' : ''}`}
            onClick={() => setActiveTab('simulator')}
          >
            <Sliders size={20} />
            <span>Risk Simulator</span>
          </div>
        </li>
      </ul>

      {user && (
        <div className="sidebar-footer">
          <div className="user-badge">
            <div className="user-avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <span className="user-name">{user.username.capitalize ? user.username.capitalize() : user.username}</span>
              <span className="user-role">{user.role}</span>
            </div>
            <button 
              onClick={onLogout}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                marginLeft: 'auto'
              }}
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
