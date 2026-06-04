import React, { useState } from 'react';
import axios from 'axios';

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

const QUESTION_TYPES = [
  { value: 'governance', label: 'Governance Checkpoints', endpoint: 'query', query: (p) => `What governance checkpoints were used in ${p}?` },
  { value: 'hil', label: 'HIL Decisions Required', endpoint: 'hil', query: (p) => `What HIL decisions are required for ${p}?` },
  { value: 'compliance', label: 'Compliance Review', endpoint: 'query', query: (p) => `What compliance requirements apply to ${p}?` },
  { value: 'ethics', label: 'Ethics & Accountability', endpoint: 'query', query: (p) => `What ethical considerations exist for ${p}?` },
  { value: 'stakeholders', label: 'Stakeholder Engagement', endpoint: 'query', query: (p) => `How were stakeholders engaged in ${p}?` },
];

function GovernanceView() {
  const [project, setProject] = useState(PROJECTS[0]);
  const [questionType, setQuestionType] = useState(QUESTION_TYPES[0]);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState(null);
  const [question, setQuestion] = useState('');

  const askMIRA = async () => {
    const q = questionType.query(project);
    setQuestion(q);
    setLoading(true);
    setResponse('');
    try {
      const url = questionType.endpoint === 'hil'
        ? `http://localhost:8000/api/governance/hil?project=${encodeURIComponent(project)}`
        : `http://localhost:8000/api/governance/query?project=${encodeURIComponent(project)}`;
      const res = await axios.post(url);
      setResponse(res.data.response);
      setTime(res.data.response_time);
    } catch (err) {
      setResponse('Error connecting to MIRA API. Is the backend running?');
    }
    setLoading(false);
  };

  return (
    <div className="view">
      <h2>Governance View</h2>
      <p className="view-subtitle">HIL checkpoints, compliance and ethical oversight</p>
      <div className="controls">
        <div className="control-group">
          <label>Project</label>
          <select value={project} onChange={e => setProject(e.target.value)}>
            {PROJECTS.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div className="control-group">
          <label>Governance Query</label>
          <select value={questionType.value} onChange={e => setQuestionType(QUESTION_TYPES.find(q => q.value === e.target.value))}>
            {QUESTION_TYPES.map(q => <option key={q.value} value={q.value}>{q.label}</option>)}
          </select>
        </div>
        <button className="ask-btn governance" onClick={askMIRA} disabled={loading}>
          {loading ? 'Reviewing...' : 'Review Governance'}
        </button>
      </div>
      {question && !loading && (
        <div className="question-preview"><span>Query:</span> {question}</div>
      )}
      {loading && <div className="loading">MIRA Governance Agent is reviewing...</div>}
      {response && (
        <div className="response-card governance">
          <div className="response-meta">
            <span>{project}</span>
            <span className="teal">{questionType.label}</span>
            {time && <span className="time">{time}s</span>}
          </div>
          <div className="response-text">
            {response.split('\n').map((line, i) => <p key={i}>{line}</p>)}
          </div>
        </div>
      )}
    </div>
  );
}

export default GovernanceView;
