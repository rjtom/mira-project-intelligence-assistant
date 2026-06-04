import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const PROJECTS = [
  "ForgeNova EV Battery Gigafactory Expansion",
  "ForgeNova Autonomous Driving Platform Development",
  "ForgeNova Electric SUV Launch Program",
  "ForgeNova Quantum Secure Software Platform",
  "ForgeNova Hydrogen Fuel Cell Vehicle Program",
  "ForgeNova Connected Car Ecosystem Platform",
  "ForgeNova Battery Recycling & Second-Life Program",
  "ForgeNova AI Driver Assistance System",
  "ForgeNova Global ERP System Migration",
  "ForgeNova Multi-Cloud Infrastructure Modernization",
  "ForgeNova Enterprise Cybersecurity Enhancement Program",
  "ForgeNova Data Analytics & Business Intelligence Platform",
  "ForgeNova DevOps Pipeline Transformation",
  "ForgeNova Digital Twin Factory Initiative",
  "ForgeNova Employee Experience Platform",
  "ForgeNova Global Supply Chain Visibility Platform",
  "ForgeNova Software Defined Vehicle Platform",
  "ForgeNova Next-Generation Battery Technology Program",
  "ForgeNova Urban Air Mobility Initiative",
  "ForgeNova Blockchain-Enabled Supply Chain Transparency",
  "ForgeNova AI-Powered Quality Control System",
  "ForgeNova Enterprise Sustainability Dashboard",
  "ForgeNova Autonomous Logistics Network",
  "ForgeNova Circular Economy Platform",
  "ForgeNova AI Ethics and Governance Framework",
  "ForgeNova Advanced Sustainability Intelligence Platform",
];

const QUICK_ACTIONS = [
  { label: "Timeline", question: "What is the timeline for {project}?" },
  { label: "Objectives", question: "What are the objectives for {project}?" },
  { label: "Risks", question: "What are the major risks for {project}?" },
  { label: "Governance", question: "What governance checkpoints were used in {project}?" },
  { label: "Lessons", question: "What lessons were learned from {project}?" },
  { label: "Resources", question: "What are the resource requirements for {project}?" },
  { label: "Compare Supply Chain", question: "How does {project} compare to ForgeNova Blockchain-Enabled Supply Chain Transparency?" },
  { label: "HIL Decisions", question: "What Human-in-the-Loop decisions are required for {project}?" },
];

function estimateTokens(text) {
  return Math.round(text.length / 4);
}

function estimateCost(tokens) {
  return ((tokens * 0.000003) + (tokens * 0.000015)).toFixed(5);
}

const HIL_KEYWORDS = [
  'human judgment required',
  'hil checkpoint',
  'human-in-the-loop',
  'human oversight required',
  'requires human review',
  'human review required',
  'human decision required',
];

function parseResponse(text) {
  const lines = text.split('\n');
  const bodyLines = [];
  const hilLines = [];
  const sourceLines = [];
  let inSources = false;

  for (const line of lines) {
    const lower = line.toLowerCase();
    const isHIL = HIL_KEYWORDS.some(kw => lower.includes(kw));
    const isSource = lower.startsWith('source:') ||
                     lower.startsWith('data source:') ||
                     lower.startsWith('[1]') ||
                     lower.startsWith('[2]') ||
                     lower.startsWith('[3]');

    if (isSource) { inSources = true; }

    if (isHIL) {
      hilLines.push(line);
    } else if (inSources || isSource) {
      if (line.trim()) sourceLines.push(line);
    } else {
      bodyLines.push(line);
    }
  }

  // Deduplicate HIL lines
  const uniqueHIL = [...new Set(hilLines)];

  return {
    body: bodyLines.join('\n').trim(),
    hilLines: uniqueHIL,
    sources: sourceLines,
  };
}

function ChatView() {
  const [project, setProject] = useState(PROJECTS[0]);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'mira',
      body: 'I am Mira, your project intelligence assistant. What would you like to explore?',
      hilLines: [],
      sources: [],
      tokens: null,
      cost: null,
      time: null,
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [totalTokens, setTotalTokens] = useState(0);
  const [totalCost, setTotalCost] = useState(0);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (question) => {
    if (!question.trim()) return;
    const userTokens = estimateTokens(question);
    setMessages(prev => [...prev, {
      role: 'user',
      body: question,
      hilLines: [],
      sources: [],
      tokens: userTokens,
      cost: null,
      time: null,
    }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(
        'http://localhost:8000/api/mira/query',
        { question, session_id: `chat-${Date.now()}` }
      );
      const { body, hilLines, sources } = parseResponse(res.data.response);
      const responseTokens = estimateTokens(res.data.response);
      const responseCost = estimateCost(responseTokens);

      setTotalTokens(prev => prev + userTokens + responseTokens);
      setTotalCost(prev => (parseFloat(prev) + parseFloat(responseCost)).toFixed(5));

      setMessages(prev => [...prev, {
        role: 'mira',
        body,
        hilLines,
        sources,
        time: res.data.response_time,
        tokens: responseTokens,
        cost: responseCost,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'mira',
        body: 'I encountered an error connecting to the backend. Please ensure the API is running on port 8000.',
        hilLines: [],
        sources: [],
        tokens: null,
        cost: null,
        time: null,
      }]);
    }
    setLoading(false);
  };

  const handleQuickAction = (template) => {
    sendMessage(template.replace('{project}', project));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="chat-view">
      <div className="chat-project-bar">
        <label>Active Project</label>
        <select value={project} onChange={e => setProject(e.target.value)}>
          {PROJECTS.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
        <div className="session-stats">
          Session: ~{totalTokens.toLocaleString()} tokens &middot; ~${totalCost}
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message message-${msg.role}`}>
            {msg.role === 'mira' && <div className="message-avatar">M</div>}

            <div className="message-content">
              <div className="message-text">
                {msg.role === 'mira' ? (
                  <ReactMarkdown>{msg.body}</ReactMarkdown>
                ) : (
                  <p>{msg.body}</p>
                )}
              </div>

              {msg.hilLines && msg.hilLines.length > 0 && (
                <div className="hil-card">
                  <span className="hil-icon">⚠️</span>
                  <div>
                    <div className="hil-title">Human Judgment Required</div>
                    {msg.hilLines.map((line, j) => (
                      <p key={j} className="hil-text">{line.replace(/^#+\s*/, '').replace(/\*\*/g, '')}</p>
                    ))}
                  </div>
                </div>
              )}

              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <div className="sources-title">Sources</div>
                  {msg.sources.map((s, j) => (
                    <div key={j} className="source-item">[{j + 1}] {s.replace(/^\[\d+\]\s*/, '')}</div>
                  ))}
                </div>
              )}

              {(msg.time || msg.tokens) && (
                <div className="message-footer">
                  {msg.time && <span className="message-time">{msg.time}s</span>}
                  {msg.tokens && <span className="message-tokens">~{msg.tokens.toLocaleString()} tokens</span>}
                  {msg.cost && <span className="message-cost">~${msg.cost}</span>}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message message-mira">
            <div className="message-avatar">M</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="quick-actions">
        {QUICK_ACTIONS.map(qa => (
          <button key={qa.label} className="quick-btn" onClick={() => handleQuickAction(qa.question)}>
            {qa.label}
          </button>
        ))}
      </div>

      <div className="chat-input-area">
        <textarea
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything about your projects... (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button className="send-btn" onClick={() => sendMessage(input)} disabled={loading || !input.trim()}>
          {loading ? '...' : '→'}
        </button>
      </div>
    </div>
  );
}

export default ChatView;
