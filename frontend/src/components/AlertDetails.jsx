import React from 'react';
import { X, ShieldAlert, Bot, RefreshCw } from 'lucide-react';

export default function AlertDetails({ alert, onClose, onOverride, onAskAssistant }) {
  if (!alert) return null;

  return (
    <div className="modal-overlay">
      <div className="glass-card modal-content">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert color="var(--danger)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Threat Analysis Details</h2>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
              Anomaly Description
            </h4>
            <p style={{ fontSize: '1rem', fontWeight: 500 }}>{alert.description}</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Affected Administrator
              </h4>
              <p style={{ fontSize: '0.95rem', fontWeight: 600 }}>
                {alert.username ? alert.username.toUpperCase() : 'UNKNOWN'}
              </p>
            </div>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Incident Severity
              </h4>
              <span className={alert.severity === 'CRITICAL' ? 'alert-pill' : 'warning-pill'}>
                {alert.severity}
              </span>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              AI Isolation Forest Decision Reasons
            </h4>
            <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--panel-border)' }}>
              {alert.reasons && alert.reasons.length > 0 ? (
                <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {alert.reasons.map((reason, idx) => (
                    <li key={idx} style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>
                      {reason}
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                  Generic baseline deviation detected. No detailed feature reasons provided.
                </p>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button 
              className="btn btn-secondary" 
              style={{ flex: 1 }}
              onClick={() => onAskAssistant(`Why is ${alert.username} flagged? Show mitigation steps.`)}
            >
              <Bot size={16} />
              Ask AI Assistant
            </button>
            <button 
              className="btn btn-danger" 
              style={{ flex: 1 }}
              onClick={() => {
                onOverride(alert.username);
                onClose();
              }}
            >
              <RefreshCw size={16} />
              Manual Account Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
