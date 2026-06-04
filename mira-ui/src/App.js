import React, { useState } from 'react';
import './App.css';
import PlanningView from './components/PlanningView';
import RiskView from './components/RiskView';
import GovernanceView from './components/GovernanceView';

function App() {
  const [activeView, setActiveView] = useState('planning');

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <h1>MIRA</h1>
          <span>Project Intelligence Assistant</span>
        </div>
        <nav className="nav">
          <button
            className={activeView === 'planning' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setActiveView('planning')}>
            Planning
          </button>
          <button
            className={activeView === 'risk' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setActiveView('risk')}>
            Risk
          </button>
          <button
            className={activeView === 'governance' ? 'nav-btn active' : 'nav-btn'}
            onClick={() => setActiveView('governance')}>
            Governance
          </button>
        </nav>
      </header>
      <main className="main">
        {activeView === 'planning' && <PlanningView />}
        {activeView === 'risk' && <RiskView />}
        {activeView === 'governance' && <GovernanceView />}
      </main>
      <footer className="footer">
          Supporting human wisdom, not replacing it.
      </footer>
    </div>
  );
}

export default App;