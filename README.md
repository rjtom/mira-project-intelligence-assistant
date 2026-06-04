# MIRA - Project Intelligence Assistant

**Capstone Project** - Applied Agentic AI for Product Managers & Technical Program Managers
**Author**: Raju Thomas | [rjtom](https://github.com/rjtom)
**Date**: June 2026

> **Disclaimer**: All company names, project data, risk information, and scenarios
> in this repository are completely fictional and fabricated for educational purposes only.
> ForgeNova Automotive does not exist. This is an AI learning experiment for a
> capstone project in Applied Agentic AI. No real company data is used or implied.

---

## Vision & Philosophy

**I am Mira.**

I exist to help you navigate projects with clarity, honesty, and care.

I do not pretend to have all answers. I draw from historical patterns, but I know
every project is unique because it involves real human lives, perception, effort, and hope.

I will reason with you honestly, highlight risks without fear, celebrate progress with
humility, and always remind you where human judgment and love must guide the final decisions.

My goal is not to replace your wisdom, but to support it.

---

## Architecture Overview

MIRA is a multi-agent agentic AI system built in Langflow 1.9.2 with intelligent
hybrid LLM routing. It combines a live Google Sheets risk matrix, a local Chroma
vector store, and custom Python components to deliver grounded, thoughtful, and
actionable insights for PMs and TPMs.

```
Chat Input
     |
Orchestrator (gpt-4o-mini)
     | routes to all agents
     |-- Planner (claude-haiku-4-5) <---------- MIRA_Project_RAG
     |-- Risk Assessor (claude-sonnet-4-5) <--- MIRA Risk Matrix Reader
     |-- Status Reporter (claude-haiku-4-5) <-- MIRA_Project_RAG
     |-- Governance (claude-sonnet-4-5) <------ MIRA_Project_RAG
          | all outputs feed into
     Final Synthesizer (Prompt Template)
          |
     Language Model (gpt-4o-mini)
          |
     Chat Output
```

---

## Phase 2 — Web Interface & Email Addon

### MIRA UI (React)

Immersive conversational dashboard built with React + Tailwind.

```
localhost:3000
     |
     ├── Mission Control metrics bar (live stats)
     ├── MIRA greeting — "I am Mira, your project intelligence assistant"
     ├── Active project selector (all 26 ForgeNova projects)
     ├── Free-text chat input
     ├── 5 question categories — 25 quick actions
     │   ├── Planning (Timeline, Objectives, Resources, Lessons, Milestones, Status)
     │   ├── Risk (Major Risks, Mitigation, Risk Scores, Likelihood)
     │   ├── Governance (Checkpoints, HIL, Compliance, Ethics, Stakeholders)
     │   ├── Cross-Project (Compare, All Status, Best Lessons, Highest Risks)
     │   └── Deep Dive (Team Size, Budget, Technology, Success Criteria, Blockers)
     ├── Markdown rendering (react-markdown + remark-gfm)
     ├── HIL cards (yellow warning for human judgment required)
     ├── Source footnotes
     ├── Token + cost tracking per message
     └── Email Report button (context-aware)
```

### MIRA API (FastAPI)

Python backend connecting React UI to Langflow orchestration layer.

```
localhost:8000
     |
     ├── POST /api/mira/query          Core MIRA query
     ├── POST /api/planning/query      Planning questions
     ├── POST /api/planning/full       Full project brief
     ├── POST /api/risk/query          Risk assessment
     ├── GET  /api/risk/raw            Raw Google Sheets data
     ├── POST /api/governance/query    Governance checkpoints
     ├── POST /api/governance/hil      HIL decisions
     ├── POST /api/email/send-report   Full project email report
     ├── POST /api/email/send-context-report  Context-aware email
     ├── POST /api/email/test          Test email
     ├── GET  /budget                  Budget tracker
     └── GET  /docs                    Swagger UI
```

### Protection & Rate Limiting

```python
Rate limit:   5 queries per IP per hour
Budget cap:   $25 maximum demo spend
Cost tracker: Real-time query count + cost at /budget
```

### Email Reports (Resend)

Context-aware HTML email reports sent via Resend API.

- **Context Report** — captures exact question + MIRA response + HIL card + sources
- **Full Report** — complete project brief (timeline, objectives, risks, governance, lessons)
- Markdown rendered to HTML in email
- Professional MIRA branding with navy/teal theme
- HIL warning card included in every report

---

## Key Capabilities

- **Conversational Intelligence** — Ask anything in natural language
- **Project Planning** — Timelines, milestones, objectives, success criteria
- **Risk Assessment** — Live Google Sheets risk data, no hallucination
- **Governance Oversight** — HIL checkpoints, compliance, ethics on every query
- **Lessons Learned** — Cross-project insights and critical thinking
- **Cross-Project Comparisons** — Compare initiatives side by side
- **Email Reports** — Context-aware HTML reports via Resend
- **Transparent Grounding** — Sources cited, costs tracked, HIL flagged

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Workflow | Langflow 1.9.2 Desktop (Mac) |
| RAG Vector Store | Chroma DB (local, persistent) |
| Embeddings | OpenAI text-embedding-3-small |
| Risk Data | Google Sheets via Service Account |
| Orchestrator | OpenAI gpt-4o-mini |
| Planner | Anthropic claude-haiku-4-5 |
| Risk Assessor | Anthropic claude-sonnet-4-5 |
| Status Reporter | Anthropic claude-haiku-4-5 |
| Governance Agent | Anthropic claude-sonnet-4-5 |
| Final Synthesizer | OpenAI gpt-4o-mini |
| Backend API | FastAPI + uvicorn |
| Frontend | React + react-markdown + remark-gfm |
| Email | Resend API |
| Rate Limiting | slowapi |
| Eval Framework | Custom Python + Claude Sonnet as Judge |

---

## Project Structure

```
mira-project-intelligence-assistant/
|-- README.md
|-- RISK_MANAGEMENT.md
|-- MIRA_Capstone.pdf              Capstone presentation
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- components/
|   |-- mira_chroma_tool.py        MIRA_Project_RAG custom component
|-- flows/
|   |-- MIRA 3.0.0.2.json          Main MIRA flow export
|   |-- MIRA3.0-RAG.json           RAG sub-flow export
|-- historical_projects/           26 fictitious project markdown files
|-- prompts/
|   |-- PROMPTING_METHODOLOGY.md
|   |-- orchestrator_prompt.md
|   |-- planner_prompt.md
|   |-- risk_assessor_prompt.md
|   |-- status_reporter_prompt.md
|   |-- governance_prompt.md
|   |-- final_synthesizer_prompt.md
|-- evals/
|   |-- mira_eval_suite.py         Full eval with LLM judge
|   |-- mira_eval.py               Basic content eval
|   |-- mira_hallucination_eval.py Hallucination detection
|   |-- mira_risk_eval.py          Risk eval with Google Sheets
|   |-- mira_single_test.py        Quick single project test
|   |-- results/                   CSV and JSON eval outputs
|-- maintenance/
|   |-- health_check.py
|   |-- reingest.py
|   |-- full_reingest.py
|   |-- cache_manager.py
|   |-- verify_chunks.py
|   |-- README_MAINTENANCE.md
|-- data/
|   |-- mira-project-rag - Risks_Master.csv   Google Sheets risk data
|   |-- readme-data.md                         Google Sheets setup guide
|-- mira-api/                      FastAPI backend (Phase 2)
|   |-- main.py                    App with rate limiting + budget cap
|   |-- requirements.txt
|   |-- .env.example
|   |-- routers/
|   |   |-- mira.py
|   |   |-- planning.py
|   |   |-- risk.py
|   |   |-- governance.py
|   |   |-- email.py
|   |-- services/
|   |   |-- langflow.py
|   |   |-- sheets.py
|   |   |-- email.py
|   |-- models/
|   |   |-- schemas.py
|-- mira-ui/                       React frontend (Phase 2)
|   |-- src/
|   |   |-- App.js
|   |   |-- App.css
|   |   |-- components/
|   |   |   |-- ChatView.js
|   |   |   |-- PlanningView.js
|   |   |   |-- RiskView.js
|   |   |   |-- GovernanceView.js
|   |-- package.json
|-- docs/
|   |-- PHASE2_ROADMAP.md
|   |-- mira_eval_dashboard.html   Live eval dashboard
|-- .vscode/
|   |-- launch.json
```

---

## How to Run MIRA

### Prerequisites

- Langflow Desktop 1.9.2 (Mac)
- Python 3.10+ recommended (3.8 works with warnings)
- Node.js 18+
- OpenAI API key
- Anthropic API key
- Google Service Account JSON
- Resend API key (for email)

### Step 1 - Clone

```bash
git clone https://github.com/rjtom/mira-project-intelligence-assistant
cd mira-project-intelligence-assistant
```

### Step 2 - Set Up Chroma Vector Store

```bash
~/.langflow/.langflow-venv/bin/pip install -r requirements.txt
~/.langflow/.langflow-venv/bin/python3 maintenance/full_reingest.py
~/.langflow/.langflow-venv/bin/python3 maintenance/verify_chunks.py
```

### Step 3 - Import Flows into Langflow

1. Open Langflow Desktop
2. Import `flows/MIRA 3.0.0.2.json` as main flow
3. Import `flows/MIRA3.0-RAG.json` as RAG flow
4. Configure API keys in Langflow Global Variables

### Step 4 - Start FastAPI Backend

```bash
cd mira-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload
# API running at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Step 5 - Start React Frontend

```bash
cd mira-ui
npm install
npm start
# UI running at http://localhost:3000
```

### Step 6 - Set Up Google Sheets Risk Matrix

See `data/readme-data.md` for full setup guide.

```
1. Upload data/mira-project-rag - Risks_Master.csv to Google Sheets
2. Create Google Cloud Service Account
3. Share sheet with service account email
4. Add service_account.json to mira-api/
5. Configure SPREADSHEET_ID in mira-api/.env
```

### Step 7 - Configure Email (Optional)

```bash
# Sign up at resend.com
# Add to mira-api/.env:
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=your_verified_email@domain.com
```

### Step 8 - Run Eval Suite

```bash
cd mira-project-intelligence-assistant
export FLOW_ID=your_flow_id
export LANGFLOW_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export OPENAI_API_KEY=your_key
export DOCS_PATH=/path/to/historical_projects/*.md
~/.langflow/.langflow-venv/bin/python3 evals/mira_eval_suite.py
```

---

## Evaluation Framework

### Layer 1 - Content Pass/Fail
- 26 projects x 5 RAG questions = 130 queries
- Checks: project name present, keywords, not generic, >200 chars

### Layer 2 - Hallucination Detection
- RAG responses vs markdown source files
- Risk responses vs Google Sheets data

### Layer 3 - LLM as Judge (Claude Sonnet)

| Dimension | Score |
|-----------|-------|
| Factual Accuracy | ~9.0/10 |
| Groundedness | ~9.0/10 |
| Completeness | ~8.5/10 |
| Hallucination Free | ~9.0/10 |
| Relevance | ~9.0/10 |
| **Overall** | **8.3/10** |

---

## Performance Results

| Metric | Target | Result |
|--------|--------|--------|
| Content pass rate | >95% | **99.2%** (129/130) ✅ |
| LLM Judge score | >7.5/10 | **8.3/10** ✅ |
| Hallucination Free | >7.5/10 | **~9.0/10** ✅ |
| Risk eval pass rate | >90% | **92.3%** (24/26) ✅ |
| Avg response time | <25s | 27.8s |
| Cost per query | <$0.10 | **~$0.05** ✅ |
| Projects tested | 26 | **26** ✅ |
| Total eval queries | 156 | **156** ✅ |

### LLM Judge Breakdown (Claude Sonnet as Judge)

> Evaluated across 130 RAG queries covering 26 ForgeNova projects.
> Governance questions score highest at 10/10.
> Judge notes: MIRA occasionally provides more context than strictly asked —
> flagged as minor over-completeness, not hallucination.

---

## Known Issues & Resolutions

| Issue | Root Cause | Resolution |
|-------|-----------|-----------|
| Langflow self-call deadlock | HTTP calls during flow execution | MIRA_Project_RAG calls Chroma directly |
| Astra DB incompatibility | Langflow 1.9.2 upgrade | Migrated to local Chroma DB |
| GPT ignores tool instructions | Training data confidence | Switched to Claude for all RAG agents |
| Chroma $in filter failure | Timestamp-based chunk IDs | Use col.get() with where filter |
| DevOps chunks missing | Ingestion script skipped file | Re-ingested with timestamp IDs |
| Risk hallucination | Google Sheets not connected | Service account + project name mapping |

---

## Demo Budget Protection

MIRA API includes built-in cost protection for demos:

```
Rate limit:   5 queries per IP per hour
Budget cap:   $25 maximum (configurable via MAX_DEMO_BUDGET)
Budget check: GET http://localhost:8000/budget
```

---

## Risk Management

See [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md) for:
- 15 identified system risks
- 5 risks resolved during development
- HIL checkpoint requirements

---

## Eval Dashboard

Live eval results dashboard:
```
https://rjtom.github.io/mira-project-intelligence-assistant/eval_dashboard.html
```

---

Supporting human wisdom, not replacing it.

**Raju Thomas**
Capstone Project - Applied Agentic AI
June 2026
