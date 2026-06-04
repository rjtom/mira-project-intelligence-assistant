import React, { useState } from 'react';
import './App.css';
import ChatView from './components/ChatView';

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <h1>MIRA</h1>
          <span>PROJECT INTELLIGENCE ASSISTANT</span>
        </div>
        <div className="header-tagline">
          Supporting human wisdom, not replacing it.
        </div>
      </header>

      <div className="metrics-bar">
        <div className="metric-card">
          <div className="metric-value">26</div>
          <div className="metric-label">Projects</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">99.2%</div>
          <div className="metric-label">Eval Pass Rate</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">8.3/10</div>
          <div className="metric-label">Judge Score</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">208</div>
          <div className="metric-label">RAG Chunks</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">Live</div>
          <div className="metric-label">Risk Matrix</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">5</div>
          <div className="metric-label">Agents</div>
        </div>
      </div>

      <main className="main">
        <ChatView />
      </main>
    </div>
  );
}

export default App;
