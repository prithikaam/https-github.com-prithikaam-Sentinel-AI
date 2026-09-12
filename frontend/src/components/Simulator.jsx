import React, { useState } from 'react';
import { Sliders, ShieldAlert, CheckCircle, HelpCircle, Activity } from 'lucide-react';
import API_URL from '../config';

export default function Simulator() {
  const [form, setForm] = useState({
    username: 'john',
    login_hour: 9,
    location: 'Coimbatore',
    device: 'Workstation-Admin-01',
    failed_logins: 0,
    commands_count: 10,
    files_accessed: 5
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/logs/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Simulation failed:", err);
      alert("Error contacting the simulation server.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPreset = (preset) => {
    switch (preset) {
      case 'john_normal':
        setForm({
          username: 'john',
          login_hour: 9,
          location: 'Coimbatore',
          device: 'Workstation-Admin-01',
          failed_logins: 0,
          commands_count: 12,
          files_accessed: 4
        });
        break;
      case 'alice_otp':
        setForm({
          username: 'alice',
          login_hour: 11,
          location: 'Delhi', // Normal Chennai
          device: 'Unknown-Tablet', // Normal DBA-Terminal-A
          failed_logins: 1,
          commands_count: 18,
          files_accessed: 12
        });
        break;
      case 'david_block':
        setForm({
          username: 'david',
          login_hour: 2, // Normal 14:00
          location: 'Delhi', // Normal Bangalore
          device: 'Hacker-VM-01', // Normal IT-Support-Host
          failed_logins: 8,
          commands_count: 95,
          files_accessed: 5200 // Huge download!
        });
        break;
      default:
        break;
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>Insider Threat Risk Simulator</h1>
          <p>Inject custom events to test the AI Isolation Forest classifier and access control policies</p>
        </div>
      </div>

      <div className="kyber-grid">
        {/* Left Column: Form Parameters */}
        <div className="kyber-col">
          <div className="glass-card">
            <h2 className="section-title">
              <Sliders size={18} color="var(--primary)" />
              Behavioral Log Parameters
            </h2>

            {/* Quick Presets */}
            <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', width: '100%', marginBottom: '0.25rem' }}>
                Quick Presets:
              </span>
              <button className="btn btn-secondary btn-sm" onClick={() => handleQuickPreset('john_normal')}>
                John (Normal Login)
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => handleQuickPreset('alice_otp')}>
                Alice (Anomalous Device - OTP)
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => handleQuickPreset('david_block')}>
                David (Data Exfiltration - BLOCK)
              </button>
            </div>

            <form onSubmit={handleSubmit} className="login-form">
              <div className="sim-form-grid">
                <div className="form-group">
                  <label>Select Account</label>
                  <select 
                    className="form-select"
                    value={form.username} 
                    onChange={e => setForm({ ...form, username: e.target.value })}
                  >
                    <option value="john">John (Admin)</option>
                    <option value="alice">Alice (DBA)</option>
                    <option value="david">David (IT Support)</option>
                    <option value="sam">Sam (Sec Auditor)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Login Time (Hour)</label>
                  <input 
                    type="number" 
                    min="0" max="23" 
                    className="form-input"
                    value={form.login_hour}
                    onChange={e => setForm({ ...form, login_hour: parseInt(e.target.value) || 0 })}
                  />
                </div>

                <div className="form-group">
                  <label>Access Location</label>
                  <input 
                    type="text" 
                    className="form-input"
                    value={form.location}
                    onChange={e => setForm({ ...form, location: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label>Access Device</label>
                  <input 
                    type="text" 
                    className="form-input"
                    value={form.device}
                    onChange={e => setForm({ ...form, device: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label>Failed Login Attempts</label>
                  <input 
                    type="number" 
                    min="0" max="20"
                    className="form-input"
                    value={form.failed_logins}
                    onChange={e => setForm({ ...form, failed_logins: parseInt(e.target.value) || 0 })}
                  />
                </div>

                <div className="form-group">
                  <label>Commands Executed</label>
                  <input 
                    type="number" 
                    min="0"
                    className="form-input"
                    value={form.commands_count}
                    onChange={e => setForm({ ...form, commands_count: parseInt(e.target.value) || 0 })}
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label>Files Accessed / Downloaded</label>
                <input 
                  type="number" 
                  min="0"
                  className="form-input"
                  value={form.files_accessed}
                  onChange={e => setForm({ ...form, files_accessed: parseInt(e.target.value) || 0 })}
                />
              </div>

              <button className="btn" type="submit" disabled={loading} style={{ width: '100%' }}>
                <Activity size={18} />
                {loading ? 'Analyzing Behavior...' : 'Inject simulated activity log'}
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: AI Analysis Result */}
        <div className="kyber-col">
          <div className="glass-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <h2 className="section-title">
              <Activity size={18} color="var(--success)" />
              AI Real-Time Evaluation
            </h2>

            {!result ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                <HelpCircle size={48} color="var(--panel-border-hover)" style={{ marginBottom: '1rem' }} />
                <p style={{ fontSize: '0.95rem' }}>Modify parameters on the left and click Inject to evaluate how SentinelAI processes the event.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', flexGrow: 1 }}>
                
                {/* Risk Gauge Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', border: '1px solid var(--panel-border)' }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 800, color: result.risk_score >= 70 ? 'var(--danger)' : result.risk_score >= 30 ? 'var(--warning)' : 'var(--success)' }}>
                    {result.risk_score}%
                  </div>
                  <div>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Behavioral Risk Score</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.15rem' }}>
                      <span className={`status-indicator ${result.status}`}>
                        {result.status === 'BLOCKED' ? 'Blocked (High Risk)' : result.status === 'OTP_CHALLENGE' ? 'Step-up MFA Enforced' : 'Access Granted (Low Risk)'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Mitigation Policy Explainer */}
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                    Access Control Decision
                  </h4>
                  <div style={{ padding: '0.85rem', borderRadius: '8px', background: result.risk_score >= 70 ? 'var(--danger-glow)' : result.risk_score >= 30 ? 'var(--warning-glow)' : 'var(--success-glow)' }}>
                    {result.risk_score >= 70 ? (
                      <p style={{ fontSize: '0.9rem' }}>
                        🛑 <strong>Account Temporarily Locked</strong>: The user has been placed in a blocked state. A CRITICAL alarm has been dispatched to the Security Incident desk.
                      </p>
                    ) : result.risk_score >= 30 ? (
                      <p style={{ fontSize: '0.9rem' }}>
                        🔑 <strong>Step-up OTP Required</strong>: The administrator is locked in verification stage. Access to core databases is restricted until OTP `123456` is confirmed.
                      </p>
                    ) : (
                      <p style={{ fontSize: '0.9rem' }}>
                        🟢 <strong>Session Allowed</strong>: Standard access approved. No abnormal markers detected in this administrative log.
                      </p>
                    )}
                  </div>
                </div>

                {/* Isolation Forest Reasons list */}
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                    Model Explanation Highlights
                  </h4>
                  {result.reasons && result.reasons.length > 0 ? (
                    <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {result.reasons.map((r, i) => (
                        <li key={i} style={{ fontSize: '0.88rem', color: 'var(--text-main)' }}>{r}</li>
                      ))}
                    </ul>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)' }}>
                      <CheckCircle size={16} />
                      <span style={{ fontSize: '0.88rem' }}>No anomaly thresholds violated. Behavior aligns with user baseline.</span>
                    </div>
                  )}
                </div>

                {/* Helpful Tip */}
                <div style={{ marginTop: 'auto', borderTop: '1px solid var(--panel-border)', paddingTop: '1rem', fontSize: '0.8rem', color: 'var(--text-dark)' }}>
                  *Simulated logs populate the dashboard alerts list and update active statistics immediately.*
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
