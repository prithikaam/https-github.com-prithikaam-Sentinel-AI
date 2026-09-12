import React, { useState } from 'react';
import { Shield, Key, Cpu, HelpCircle, User, ArrowRight, RefreshCw } from 'lucide-react';
import API_URL from '../config';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('john');
  const [password, setPassword] = useState('password123');
  const [status, setStatus] = useState('idle'); // idle, handshaking, otp_pending, blocked, error
  const [errorMsg, setErrorMsg] = useState('');
  
  // Simulated OTP state
  const [otp, setOtp] = useState('');
  
  // Custom behavior tuning parameters for login simulation
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loginHour, setLoginHour] = useState(new Date().getHours());
  const [location, setLocation] = useState('Coimbatore');
  const [device, setDevice] = useState('Workstation-Admin-01');
  const [failedLogins, setFailedLogins] = useState(0);

  // Kyber progress tracking
  const [kyberSteps, setKyberSteps] = useState([
    { label: 'Query Kyber Public Key from Server', status: 'pending' },
    { label: 'Generate shared secret & encapsulate ciphertext', status: 'pending' },
    { label: 'Encrypt credentials and transmit packet', status: 'pending' }
  ]);

  const updateKyberStep = (idx, stepStatus) => {
    setKyberSteps(prev => {
      const nextSteps = [...prev];
      nextSteps[idx].status = stepStatus;
      return nextSteps;
    });
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return;

    setStatus('handshaking');
    setErrorMsg('');
    setKyberSteps([
      { label: 'Query Kyber Public Key from Server', status: 'active' },
      { label: 'Generate shared secret & encapsulate ciphertext', status: 'pending' },
      { label: 'Encrypt credentials and transmit packet', status: 'pending' }
    ]);

    try {
      // 1. Initial Handshake Request (Get Kyber Public Key)
      const initRes = await fetch(`${API_URL}/api/auth/login-init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });

      if (!initRes.ok) {
        const errorData = await initRes.json();
        throw new Error(errorData.error || 'Server rejected login handshake initialization');
      }

      const initData = await initRes.ok ? await initRes.json() : null;
      updateKyberStep(0, 'done');
      updateKyberStep(1, 'active');

      // 2. Perform Local Kyber Encapsulation Simulation (producing Ciphertext & Shared Secret)
      // In the real system, we'd do this client-side using JavaScript Kyber library.
      // To run natively without heavy packages, we simulate the output values matching the keygen.
      await new Promise(resolve => setTimeout(resolve, 800)); // Animation pause
      
      const validHex = "0".repeat(1024);
      const mockCiphertext = {
        u: [validHex, validHex],
        v: validHex
      };
      
      updateKyberStep(1, 'done');
      updateKyberStep(2, 'active');

      // 3. Complete Login (Transmit Credentials + Kyber Ciphertext + Activity Metrics)
      await new Promise(resolve => setTimeout(resolve, 800)); // Animation pause

      const loginRes = await fetch(`${API_URL}/api/auth/login-complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          password,
          ciphertext: mockCiphertext,
          login_hour: loginHour,
          location,
          device,
          failed_logins: failedLogins
        })
      });

      const loginData = await loginRes.json();

      if (!loginRes.ok && loginRes.status !== 403) {
        throw new Error(loginData.error || 'Invalid credentials');
      }

      updateKyberStep(2, 'done');

      // Handle server risk routing decision
      if (loginData.status === 'BLOCKED') {
        setStatus('blocked');
        setErrorMsg(`Access Blocked: Risk Score is too high (${loginData.risk_score}%). System admin has locked the account. Reasons: ${loginData.reasons.join(', ')}`);
      } else if (loginData.status === 'OTP_CHALLENGE') {
        setStatus('otp_pending');
      } else if (loginData.status === 'ACTIVE') {
        // Successful login, save JWT
        localStorage.setItem('sentinel_token', loginData.token);
        localStorage.setItem('sentinel_user', JSON.stringify({ username, role: username === 'john' ? 'Administrator' : username === 'alice' ? 'Database Administrator' : 'IT Support' }));
        onLoginSuccess();
      }

    } catch (err) {
      console.error(err);
      setStatus('error');
      setErrorMsg(err.message || 'Failed to establish connection with security center.');
    }
  };

  const handleOtpVerify = async (e) => {
    e.preventDefault();
    if (!otp) return;

    try {
      const res = await fetch(`${API_URL}/api/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, otp })
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || 'Incorrect OTP code');
      }

      // Successful OTP validation
      localStorage.setItem('sentinel_token', data.token);
      localStorage.setItem('sentinel_user', JSON.stringify({ username, role: username === 'alice' ? 'Database Administrator' : 'Administrator' }));
      onLoginSuccess();
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  return (
    <div className="login-container">
      <div className="glass-card login-card">
        
        <div className="login-header">
          <div style={{ display: 'inline-flex', padding: '0.75rem', borderRadius: '12px', background: 'var(--primary-glow)', color: 'var(--primary)', marginBottom: '0.5rem' }}>
            <Shield size={36} />
          </div>
          <h2>SentinelAI Gateway</h2>
          <p>Quantum-Safe Privileged access control portal</p>
        </div>

        {/* Status Error Display */}
        {errorMsg && (
          <div className={status === 'blocked' ? 'login-error' : 'login-error'}>
            {errorMsg}
          </div>
        )}

        {status === 'handshaking' ? (
          /* Cryptographic Handshake Visualizer card */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: '1rem 0' }}>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Cpu size={14} className="logo-icon" />
              Establishing post-quantum tunnel...
            </h4>
            <div className="kyber-step-flow">
              {kyberSteps.map((step, idx) => (
                <div key={idx} className={`step-flow-item ${step.status}`}>
                  <div className="step-flow-title" style={{ fontSize: '0.85rem' }}>{step.label}</div>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
              <RefreshCw size={24} className="logo-icon" style={{ animation: 'spin 2s linear infinite' }} />
            </div>
          </div>
        ) : status === 'otp_pending' ? (
          /* OTP MFA Step-up authentication card */
          <form onSubmit={handleOtpVerify} className="login-form">
            <div className="login-alert">
              ⚠️ Anomaly detected. Multi-Factor OTP (MFA) is required. Use prototype code: <strong>123456</strong>.
            </div>
            <div className="form-group">
              <label>Enter 6-Digit OTP</label>
              <input
                type="text"
                className="form-input"
                placeholder="123456"
                maxLength={6}
                value={otp}
                onChange={e => setOtp(e.target.value)}
                style={{ textAlign: 'center', fontSize: '1.25rem', letterSpacing: '0.5em', fontFamily: 'var(--font-mono)' }}
              />
            </div>
            <button className="btn" type="submit" style={{ width: '100%' }}>
              Verify OTP Code
            </button>
            <button className="btn btn-secondary" onClick={() => setStatus('idle')} style={{ width: '100%' }}>
              Cancel
            </button>
          </form>
        ) : (
          /* Standard Login Entry Form */
          <form onSubmit={handleLoginSubmit} className="login-form">
            <div className="form-group">
              <label>Privileged Account Username</label>
              <select
                className="form-select"
                value={username}
                onChange={e => setUsername(e.target.value)}
              >
                <option value="john">john (Administrator - normal Coimbatore)</option>
                <option value="alice">alice (Database Admin - normal Chennai)</option>
                <option value="david">david (IT Support - normal Bangalore)</option>
                <option value="sam">sam (Security Auditor - normal Coimbatore)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Authentication Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
            </div>

            {/* Collapsible Advanced Parameters for custom testing */}
            <div style={{ marginTop: '0.5rem' }}>
              <button 
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setShowAdvanced(!showAdvanced)}
                style={{ fontSize: '0.75rem', width: '100%', justifyContent: 'center' }}
              >
                {showAdvanced ? 'Hide Simulation Tuning' : 'Show Simulation Tuning (Test Anomalies)'}
              </button>
              
              {showAdvanced && (
                <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', border: '1px solid var(--panel-border)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Simulate Login Hour (0-23)</label>
                    <input 
                      type="number" 
                      className="form-input" 
                      min="0" max="23"
                      value={loginHour} 
                      onChange={e => setLoginHour(parseInt(e.target.value) || 0)} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Simulate Location</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      value={location} 
                      onChange={e => setLocation(e.target.value)} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Simulate Device</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      value={device} 
                      onChange={e => setDevice(e.target.value)} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Simulate Prior Failed Logins</label>
                    <input 
                      type="number" 
                      className="form-input" 
                      min="0" max="10"
                      value={failedLogins} 
                      onChange={e => setFailedLogins(parseInt(e.target.value) || 0)} 
                    />
                  </div>
                </div>
              )}
            </div>

            <button className="btn" type="submit" style={{ width: '100%', marginTop: '0.5rem' }}>
              <span>Establish Secure Login</span>
              <ArrowRight size={16} />
            </button>
          </form>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
