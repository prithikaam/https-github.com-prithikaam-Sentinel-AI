import React, { useState, useEffect } from 'react';
import { Users, ShieldAlert, CheckCircle, RefreshCw, Bot, Bell } from 'lucide-react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import AlertDetails from './AlertDetails';

// Register Chart.js modules
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Dashboard({ onAskAssistant }) {
  const [stats, setStats] = useState({
    activeAdmins: 0,
    highRiskUsers: 0,
    todayAlerts: 0,
    riskGraph: []
  });
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      // Fetch stats
      const statsRes = await fetch('http://127.0.0.1:5000/api/dashboard/stats');
      const statsData = await statsRes.json();
      setStats(statsData);

      // Fetch alerts
      const alertsRes = await fetch('http://127.0.0.1:5000/api/dashboard/alerts');
      const alertsData = await alertsRes.json();
      setAlerts(alertsData);
      
      setLoading(false);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Poll every 5 seconds for live updates
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleOverride = async (username) => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/users/override', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });
      const data = await res.json();
      alert(data.message);
      fetchDashboardData(); // Refresh
    } catch (err) {
      console.error("Override failed:", err);
    }
  };

  // Chart Configuration
  const chartData = {
    labels: stats.riskGraph.map(u => u.username),
    datasets: [
      {
        label: 'Live Risk Score (%)',
        data: stats.riskGraph.map(u => u.risk_score),
        backgroundColor: stats.riskGraph.map(u => {
          if (u.risk_score >= 70 || u.status === 'BLOCKED') return 'rgba(239, 68, 68, 0.7)'; // Red
          if (u.risk_score >= 30 || u.status === 'OTP_CHALLENGE') return 'rgba(245, 158, 11, 0.7)'; // Amber
          return 'rgba(16, 185, 129, 0.7)'; // Green
        }),
        borderColor: stats.riskGraph.map(u => {
          if (u.risk_score >= 70 || u.status === 'BLOCKED') return '#ef4444';
          if (u.risk_score >= 30 || u.status === 'OTP_CHALLENGE') return '#f59e0b';
          return '#10b981';
        }),
        borderWidth: 1,
        borderRadius: 6
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false // Hide dataset legend
      },
      tooltip: {
        callbacks: {
          label: (context) => `Risk Score: ${context.raw}%`
        }
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        grid: {
          color: 'rgba(255, 255, 255, 0.05)'
        },
        ticks: {
          color: '#9ca3af',
          font: { family: 'Outfit' }
        }
      },
      x: {
        grid: { display: false },
        ticks: {
          color: '#9ca3af',
          font: { family: 'Outfit' }
        }
      }
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div style={{ color: 'var(--text-muted)' }}>Loading SentinelAI Operations center...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>Live Security Dashboard</h1>
          <p>Continuous behavior monitoring & privileged access analytics</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.85rem', color: 'var(--success)' }}>
          <span className="pulse-dot"></span>
          <span>Operations Center Connected</span>
        </div>
      </div>

      {/* Aggregate Stats Cards */}
      <div className="stats-grid">
        <div className="glass-card stat-card">
          <div className="stat-details">
            <h3>Active Admins</h3>
            <div className="value">{stats.activeAdmins}</div>
          </div>
          <div className="stat-icon primary">
            <Users size={22} />
          </div>
        </div>

        <div className="glass-card stat-card">
          <div className="stat-details">
            <h3>High Risk Users</h3>
            <div className="value" style={{ color: stats.highRiskUsers > 0 ? 'var(--danger)' : 'white' }}>
              {stats.highRiskUsers}
            </div>
          </div>
          <div className="stat-icon danger">
            <ShieldAlert size={22} />
          </div>
        </div>

        <div className="glass-card stat-card">
          <div className="stat-details">
            <h3>Today's Active Alerts</h3>
            <div className="value" style={{ color: stats.todayAlerts > 0 ? 'var(--warning)' : 'white' }}>
              {stats.todayAlerts}
            </div>
          </div>
          <div className="stat-icon warning">
            <Bell size={22} />
          </div>
        </div>
      </div>

      {/* Core Dashboard Content */}
      <div className="dashboard-layout">
        
        {/* Left Column: Live User Registry & Risk Graph */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* User Registry Table */}
          <div className="glass-card">
            <h2 className="section-title">
              <Users size={18} color="var(--primary)" />
              Privileged Accounts Registry
            </h2>
            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Admin Name</th>
                    <th>Role</th>
                    <th>Live Risk Score</th>
                    <th>Session Status</th>
                    <th>Security Action</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.riskGraph.map((user, index) => {
                    const isHigh = user.risk_score >= 70 || user.status === 'BLOCKED';
                    const isMed = user.risk_score >= 30 && user.risk_score < 70 && user.status !== 'BLOCKED';
                    
                    return (
                      <tr key={index}>
                        <td style={{ fontWeight: 600 }}>{user.username}</td>
                        <td style={{ color: 'var(--text-muted)' }}>{user.role}</td>
                        <td>
                          <span className={`risk-badge ${isHigh ? 'high' : isMed ? 'medium' : 'low'}`}>
                            {user.risk_score}%
                          </span>
                        </td>
                        <td>
                          <span className={`status-indicator ${user.status}`}>
                            {user.status}
                          </span>
                        </td>
                        <td>
                          {(user.status === 'BLOCKED' || user.status === 'OTP_CHALLENGE' || user.risk_score >= 30) ? (
                            <button 
                              className="btn btn-secondary btn-sm"
                              onClick={() => handleOverride(user.username.toLowerCase())}
                              title="Reset security policy and re-enable active session"
                            >
                              <RefreshCw size={12} />
                              Override Block
                            </button>
                          ) : (
                            <span style={{ fontSize: '0.85rem', color: 'var(--text-dark)' }}>No Action Needed</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Risk Graph Chart.js */}
          <div className="glass-card">
            <h2 className="section-title">
              <ShieldAlert size={18} color="var(--primary)" />
              Behavioral Risk Profiler
            </h2>
            <div style={{ height: '220px', position: 'relative' }}>
              <Bar data={chartData} options={chartOptions} />
            </div>
          </div>

        </div>

        {/* Right Column: Live Security Alert Feed */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h2 className="section-title">
            <Bell size={18} color="var(--warning)" />
            Real-Time Threat Alerts
          </h2>
          <div className="alerts-list">
            {alerts.length > 0 ? (
              alerts.map((alert, index) => {
                const isCritical = alert.severity === 'CRITICAL';
                
                return (
                  <div key={index} className={`alert-item ${isCritical ? 'critical' : 'warning'}`}>
                    <ShieldAlert 
                      className={`alert-icon ${isCritical ? 'critical' : 'warning'}`} 
                      size={18} 
                    />
                    <div className="alert-body">
                      <span className="alert-desc">{alert.description}</span>
                      <div className="alert-meta">
                        <span>@{alert.username}</span>
                        <span>•</span>
                        <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                      </div>
                      {!alert.resolved && (
                        <button 
                          className="alert-explain-btn"
                          onClick={() => setSelectedAlert(alert)}
                        >
                          Explain Incident Details
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            ) : (
              <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                <CheckCircle size={32} color="var(--success)" style={{ marginBottom: '0.75rem' }} />
                <p style={{ fontSize: '0.9rem' }}>No anomalous activities detected. All administrators are operating within historical limits.</p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Modal for alert explanation details */}
      {selectedAlert && (
        <AlertDetails
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onOverride={handleOverride}
          onAskAssistant={onAskAssistant}
        />
      )}
    </div>
  );
}
