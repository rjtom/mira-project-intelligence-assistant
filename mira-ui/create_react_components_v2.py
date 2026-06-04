import os

PROJECTS = [
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
]

projects_js = "const PROJECTS = [\n" + "\n".join(f'  "{p}",' for p in PROJECTS) + "\n];"

files = {}

files['src/components/PlanningView.js'] = f"""import React, {{ useState }} from 'react';
import axios from 'axios';

{projects_js}

const QUESTION_TYPES = [
  {{ value: 'timeline', label: 'Timeline & Milestones', query: (p) => `What is the timeline for ${{p}}?` }},
  {{ value: 'objectives', label: 'Objectives & Goals', query: (p) => `What are the objectives for ${{p}}?` }},
  {{ value: 'resources', label: 'Resource Requirements', query: (p) => `What are the resource requirements for ${{p}}?` }},
  {{ value: 'lessons', label: 'Lessons Learned', query: (p) => `What lessons were learned from ${{p}}?` }},
];

function PlanningView() {{
  const [project, setProject] = useState(PROJECTS[0]);
  const [questionType, setQuestionType] = useState(QUESTION_TYPES[0]);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState(null);
  const [question, setQuestion] = useState('');

  const askMIRA = async () => {{
    const q = questionType.query(project);
    setQuestion(q);
    setLoading(true);
    setResponse('');
    try {{
      const res = await axios.post(
        `http://localhost:8000/api/planning/query?project=${{encodeURIComponent(project)}}&question_type=${{questionType.value}}`
      );
      setResponse(res.data.response);
      setTime(res.data.response_time);
    }} catch (err) {{
      setResponse('Error connecting to MIRA API. Is the backend running?');
    }}
    setLoading(false);
  }};

  return (
    <div className="view">
      <h2>Planning View</h2>
      <p className="view-subtitle">Timelines, objectives, resources and lessons learned</p>
      <div className="controls">
        <div className="control-group">
          <label>Project</label>
          <select value={{project}} onChange={{e => setProject(e.target.value)}}>
            {{PROJECTS.map(p => <option key={{p}} value={{p}}>{{p}}</option>)}}
          </select>
        </div>
        <div className="control-group">
          <label>Question Type</label>
          <select value={{questionType.value}} onChange={{e => setQuestionType(QUESTION_TYPES.find(q => q.value === e.target.value))}}>
            {{QUESTION_TYPES.map(q => <option key={{q.value}} value={{q.value}}>{{q.label}}</option>)}}
          </select>
        </div>
        <button className="ask-btn" onClick={{askMIRA}} disabled={{loading}}>
          {{loading ? 'Asking MIRA...' : 'Ask MIRA'}}
        </button>
      </div>
      {{question && !loading && (
        <div className="question-preview"><span>Query:</span> {{question}}</div>
      )}}
      {{loading && <div className="loading">MIRA Planner is thinking...</div>}}
      {{response && (
        <div className="response-card">
          <div className="response-meta">
            <span>{{project}}</span>
            <span className="teal">{{questionType.label}}</span>
            {{time && <span className="time">{{time}}s</span>}}
          </div>
          <div className="response-text">
            {{response.split('\\n').map((line, i) => <p key={{i}}>{{line}}</p>)}}
          </div>
        </div>
      )}}
    </div>
  );
}}

export default PlanningView;
"""

files['src/components/RiskView.js'] = f"""import React, {{ useState }} from 'react';
import axios from 'axios';

{projects_js}

const QUESTION_TYPES = [
  {{ value: 'risks', label: 'Major Risks', query: (p) => `What are the major risks for ${{p}}?` }},
  {{ value: 'mitigation', label: 'Mitigation Strategies', query: (p) => `What are the mitigation strategies for ${{p}}?` }},
  {{ value: 'hil', label: 'HIL Checkpoints', query: (p) => `What HIL checkpoints are required for ${{p}}?` }},
  {{ value: 'score', label: 'Risk Scores & Impact', query: (p) => `What are the risk scores for ${{p}}?` }},
  {{ value: 'likelihood', label: 'Risk Likelihood', query: (p) => `What is the risk likelihood for ${{p}}?` }},
];

function RiskView() {{
  const [project, setProject] = useState(PROJECTS[0]);
  const [questionType, setQuestionType] = useState(QUESTION_TYPES[0]);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState(null);
  const [question, setQuestion] = useState('');
  const [dataSource, setDataSource] = useState('');

  const askMIRA = async () => {{
    const q = questionType.query(project);
    setQuestion(q);
    setLoading(true);
    setResponse('');
    setDataSource('');
    try {{
      const res = await axios.post(
        `http://localhost:8000/api/risk/query?project=${{encodeURIComponent(project)}}&question_type=${{questionType.value}}`
      );
      setResponse(res.data.response);
      setTime(res.data.response_time);
      setDataSource(res.data.data_source || '');
    }} catch (err) {{
      setResponse('Error connecting to MIRA API. Is the backend running?');
    }}
    setLoading(false);
  }};

  return (
    <div className="view">
      <h2>Risk Assessor View</h2>
      <p className="view-subtitle">Risk scores, mitigation strategies and HIL checkpoints</p>
      <div className="controls">
        <div className="control-group">
          <label>Project</label>
          <select value={{project}} onChange={{e => setProject(e.target.value)}}>
            {{PROJECTS.map(p => <option key={{p}} value={{p}}>{{p}}</option>)}}
          </select>
        </div>
        <div className="control-group">
          <label>Risk Question</label>
          <select value={{questionType.value}} onChange={{e => setQuestionType(QUESTION_TYPES.find(q => q.value === e.target.value))}}>
            {{QUESTION_TYPES.map(q => <option key={{q.value}} value={{q.value}}>{{q.label}}</option>)}}
          </select>
        </div>
        <button className="ask-btn risk" onClick={{askMIRA}} disabled={{loading}}>
          {{loading ? 'Assessing...' : 'Assess Risk'}}
        </button>
      </div>
      {{question && !loading && (
        <div className="question-preview"><span>Query:</span> {{question}}</div>
      )}}
      {{loading && <div className="loading">MIRA Risk Assessor is analyzing...</div>}}
      {{response && (
        <div className="response-card risk">
          <div className="response-meta">
            <span>{{project}}</span>
            <span className="teal">{{questionType.label}}</span>
            {{dataSource && <span className="teal">{{dataSource}}</span>}}
            {{time && <span className="time">{{time}}s</span>}}
          </div>
          <div className="response-text">
            {{response.split('\\n').map((line, i) => <p key={{i}}>{{line}}</p>)}}
          </div>
        </div>
      )}}
    </div>
  );
}}

export default RiskView;
"""

files['src/components/GovernanceView.js'] = f"""import React, {{ useState }} from 'react';
import axios from 'axios';

{projects_js}

const QUESTION_TYPES = [
  {{ value: 'governance', label: 'Governance Checkpoints', endpoint: 'query', query: (p) => `What governance checkpoints were used in ${{p}}?` }},
  {{ value: 'hil', label: 'HIL Decisions Required', endpoint: 'hil', query: (p) => `What HIL decisions are required for ${{p}}?` }},
  {{ value: 'compliance', label: 'Compliance Review', endpoint: 'query', query: (p) => `What compliance requirements apply to ${{p}}?` }},
  {{ value: 'ethics', label: 'Ethics & Accountability', endpoint: 'query', query: (p) => `What ethical considerations exist for ${{p}}?` }},
  {{ value: 'stakeholders', label: 'Stakeholder Engagement', endpoint: 'query', query: (p) => `How were stakeholders engaged in ${{p}}?` }},
];

function GovernanceView() {{
  const [project, setProject] = useState(PROJECTS[0]);
  const [questionType, setQuestionType] = useState(QUESTION_TYPES[0]);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState(null);
  const [question, setQuestion] = useState('');

  const askMIRA = async () => {{
    const q = questionType.query(project);
    setQuestion(q);
    setLoading(true);
    setResponse('');
    try {{
      const url = questionType.endpoint === 'hil'
        ? `http://localhost:8000/api/governance/hil?project=${{encodeURIComponent(project)}}`
        : `http://localhost:8000/api/governance/query?project=${{encodeURIComponent(project)}}`;
      const res = await axios.post(url);
      setResponse(res.data.response);
      setTime(res.data.response_time);
    }} catch (err) {{
      setResponse('Error connecting to MIRA API. Is the backend running?');
    }}
    setLoading(false);
  }};

  return (
    <div className="view">
      <h2>Governance View</h2>
      <p className="view-subtitle">HIL checkpoints, compliance and ethical oversight</p>
      <div className="controls">
        <div className="control-group">
          <label>Project</label>
          <select value={{project}} onChange={{e => setProject(e.target.value)}}>
            {{PROJECTS.map(p => <option key={{p}} value={{p}}>{{p}}</option>)}}
          </select>
        </div>
        <div className="control-group">
          <label>Governance Query</label>
          <select value={{questionType.value}} onChange={{e => setQuestionType(QUESTION_TYPES.find(q => q.value === e.target.value))}}>
            {{QUESTION_TYPES.map(q => <option key={{q.value}} value={{q.value}}>{{q.label}}</option>)}}
          </select>
        </div>
        <button className="ask-btn governance" onClick={{askMIRA}} disabled={{loading}}>
          {{loading ? 'Reviewing...' : 'Review Governance'}}
        </button>
      </div>
      {{question && !loading && (
        <div className="question-preview"><span>Query:</span> {{question}}</div>
      )}}
      {{loading && <div className="loading">MIRA Governance Agent is reviewing...</div>}}
      {{response && (
        <div className="response-card governance">
          <div className="response-meta">
            <span>{{project}}</span>
            <span className="teal">{{questionType.label}}</span>
            {{time && <span className="time">{{time}}s</span>}}
          </div>
          <div className="response-text">
            {{response.split('\\n').map((line, i) => <p key={{i}}>{{line}}</p>)}}
          </div>
        </div>
      )}}
    </div>
  );
}}

export default GovernanceView;
"""

for filepath, content in files.items():
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created: {filepath}")

print("\nAll 3 components created with all 26 projects!")
