import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, ShieldAlert, Sparkles, HelpCircle } from 'lucide-react';
import API_URL from '../config';

// A simple, safe, and lightweight Markdown-to-HTML parser for React
function renderMarkdown(text) {
  if (!text) return '';

  let html = text;

  // 1. Alert boxes (e.g. > [!NOTE] or > [!CAUTION])
  html = html.replace(/>\s*\[!NOTE\]\s*\n*(.*?)(?=\n\n|\n*$)/gs, '<div class="warning-pill" style="display:block; margin: 0.5rem 0; padding: 0.75rem; border-radius: 8px; font-weight: normal; font-size: 0.85rem;"><strong>NOTE:</strong> $1</div>');
  html = html.replace(/>\s*\[!CAUTION\]\s*\n*(.*?)(?=\n\n|\n*$)/gs, '<div class="alert-pill" style="display:block; margin: 0.5rem 0; padding: 0.75rem; border-radius: 8px; font-weight: normal; font-size: 0.85rem;"><strong>CAUTION:</strong> $1</div>');

  // 2. Headings
  html = html.replace(/^### (.*?)$/gm, '<h4 style="font-size: 1rem; font-weight:600; margin: 1rem 0 0.5rem 0; color:var(--primary);">$1</h4>');
  html = html.replace(/^## (.*?)$/gm, '<h3 style="font-size: 1.15rem; font-weight:600; margin: 1.25rem 0 0.5rem 0; border-bottom: 1px solid var(--panel-border); padding-bottom: 0.25rem;">$1</h3>');
  html = html.replace(/^# (.*?)$/gm, '<h2 style="font-size: 1.3rem; font-weight:700; margin: 1.5rem 0 0.75rem 0;">$1</h2>');

  // 3. Tables
  // Simple table parser
  const lines = html.split('\n');
  let inTable = false;
  let tableLines = [];
  let parsedLines = [];

  for (let line of lines) {
    if (line.trim().startsWith('|')) {
      if (!inTable) {
        inTable = true;
        tableLines = [line];
      } else {
        tableLines.push(line);
      }
    } else {
      if (inTable) {
        inTable = false;
        // Parse the table
        const tableHtml = parseTableLines(tableLines);
        parsedLines.push(tableHtml);
      }
      parsedLines.push(line);
    }
  }
  if (inTable) {
    parsedLines.push(parseTableLines(tableLines));
  }
  html = parsedLines.join('\n');

  // 4. Bold / Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/`(.*?)`/g, '<code style="font-family:var(--font-mono); background:rgba(255,255,255,0.06); padding:0.1rem 0.3rem; border-radius:4px; font-size:0.85rem;">$1</code>');

  // 5. Lists
  html = html.replace(/^\s*[-*]\s*(.*?)$/gm, '<li style="margin-left: 1.25rem; font-size:0.9rem; margin-bottom:0.25rem;">$1</li>');
  
  // 6. Linebreaks (excluding list items/headings and tables)
  // Wrap paragraphs
  return html;
}

function parseTableLines(lines) {
  // Remove separation line (e.g. | :--- | :--- |)
  const rows = lines.filter(l => !l.includes(':---') && !l.includes('---:'));
  
  let html = '<table style="width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem;">';
  
  rows.forEach((row, idx) => {
    const cols = row.split('|').map(c => c.trim()).filter((c, i, a) => i > 0 && i < a.length - 1);
    html += '<tr>';
    cols.forEach(col => {
      if (idx === 0) {
        html += `<th style="border: 1px solid var(--panel-border); padding: 0.5rem 0.75rem; text-align: left; background: rgba(255,255,255,0.03); font-weight:600;">${col}</th>`;
      } else {
        html += `<td style="border: 1px solid var(--panel-border); padding: 0.5rem 0.75rem; text-align: left;">${col}</td>`;
      }
    });
    html += '</tr>';
  });
  
  html += '</table>';
  return html;
}

export default function Assistant({ initialQuery }) {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "Hello! I'm the **SentinelAI Security Assistant**. I continuously evaluate active administrator behaviors. Ask me about current threats, specific user histories, or recommended security protocols. Try clicking a shortcut query below!"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Focus and scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Pre-fill query if triggered from dashboard
  useEffect(() => {
    if (initialQuery) {
      handleSend(initialQuery);
    }
  }, [initialQuery]);

  const handleSend = async (queryToSend) => {
    const queryText = queryToSend || input;
    if (!queryText.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: queryText }]);
    if (!queryToSend) setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/assistant/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: queryText })
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { sender: 'assistant', text: data.reply }]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages(prev => [
        ...prev, 
        { 
          sender: 'assistant', 
          text: "⚠️ **System Communication Error**: Failed to reach SentinelAI assistant server. Please ensure the backend Flask server is running and the API URL is configured correctly." 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const shortcuts = [
    "Show high-risk users today",
    "Why was David blocked?",
    "Suggest mitigation steps for Alice",
    "What was John's recent activity?"
  ];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>AI Security Assistant</h1>
          <p>Investigate policy alerts and review security mitigation playbooks</p>
        </div>
      </div>

      <div className="glass-card chat-container">
        
        {/* Messages Pane */}
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.sender}`}>
              <div className="chat-avatar">
                {msg.sender === 'user' ? 'U' : <Bot size={16} />}
              </div>
              <div 
                className="chat-text"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }}
              />
            </div>
          ))}
          {loading && (
            <div className="chat-bubble assistant">
              <div className="chat-avatar"><Bot size={16} /></div>
              <div className="chat-text" style={{ color: 'var(--text-muted)' }}>
                Analyzing security state...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Shortcut Commands */}
        <div style={{ padding: '0.75rem 1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', borderBottom: '1px solid var(--panel-border)', background: 'rgba(0,0,0,0.1)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Sparkles size={12} color="var(--primary)" />
            Suggestions:
          </span>
          {shortcuts.map((sh, idx) => (
            <button 
              key={idx}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem', borderRadius: '4px' }}
              onClick={() => handleSend(sh)}
              disabled={loading}
            >
              {sh}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form 
          className="chat-input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            type="text"
            className="chat-input"
            placeholder="Type your security inquiry (e.g. 'Explain risk for Alice')"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button className="btn-send" type="submit" disabled={loading}>
            <Send size={18} />
          </button>
        </form>

      </div>
    </div>
  );
}
