# MIRA - Project Intelligence Assistant

**Capstone Project** - Applied Agentic AI for Product Managers & Technical Program Managers
**Author**: Raju Thomas | [rjtom](https://github.com/rjtom)
**Date**: June 2, 2026

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

## Key Capabilities

- **Project Planning** - Timelines, milestones, objectives, and success criteria from 26 fictitious project documents
- **Risk Assessment** - Fabricated risk data from Google Sheets including scores, mitigation strategies, HIL checkpoints
- **Status Reporting** - Current project phase, progress, blockers, and next steps
- **Governance Oversight** - Human-in-the-Loop recommendations and ethical review on every query
- **Lessons Learned** - Cross-project insights and critical thinking analysis
- **Cross-Project Queries** - Compare and summarize across all 26 projects simultaneously
- **Transparent Grounding** - Clearly states when information is insufficient or uncertain

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Workflow | Langflow 1.9.2 Desktop (Mac) |
| RAG Vector Store | Chroma DB (local, persistent) |
| Embeddings | OpenAI text-embedding-3-small |
| Risk Data | Google Sheets via custom Python component |
| Orchestrator | OpenAI gpt-4o-mini |
| Planner | Anthropic claude-haiku-4-5 |
| Risk Assessor | Anthropic claude-sonnet-4-5 |
| Status Reporter | Anthropic claude-haiku-4-5 |
| Governance Agent | Anthropic claude-sonnet-4-5 |
| Final Synthesizer | OpenAI gpt-4o-mini |
| Eval Framework | Custom Python + Claude as Judge |

---

## Prompt Engineering Methodology

MIRA uses a hybrid prompting methodology combining 10 techniques:

| Technique | Purpose | Applied To |
|-----------|---------|-----------|
| System Prompting | Agent identity and constraints | All agents |
| Role Prompting | Expert persona assignment | All agents |
| Instruction Prompting | Explicit behavioral directives | All agents |
| Chain-of-Thought (CoT) | Structured reasoning chains | Risk Assessor |
| ReAct | Reason before acting (tool use) | All agents |
| Grounding Prompting | Prevents hallucination | All agents |
| Few-Shot Prompting | Implicit output format examples | Final Synthesizer |
| Constraint Prompting | Hard limits on behavior | All agents |
| Persona Prompting | Consistent MIRA voice | All agents |
| Output Structure Prompting | Defines expected format | All agents |

See [prompts/PROMPTING_METHODOLOGY.md](prompts/PROMPTING_METHODOLOGY.md) for full details.

---

## Custom Components

### 1. MIRA_Project_RAG
Direct Chroma DB retrieval with smart project filtering and embedding cache.
- Detects cross-project vs single-project queries
- Keyword + phrase map scoring to identify correct source document
- col.get() with metadata filter for reliable retrieval (fixes timestamp ID issue)
- Disk-based embedding cache for speed (43% improvement on repeat queries)
- No HTTP calls - avoids Langflow self-call deadlock

### 2. MIRA Risk Matrix Reader
Reads live risk data directly from Google Sheets via Google Service Account.
- Filters by project name dynamically
- Returns structured risk records with all columns
- Tool-mode compatible for agent use

---

## Project Structure

```
mira-project-intelligence-assistant/
|-- README.md
|-- RISK_MANAGEMENT.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- components/
|   |-- mira_chroma_tool.py         MIRA_Project_RAG custom component
|-- flows/
|   |-- MIRA_3_0_Final.json         Main MIRA flow export
|   |-- MIRA_RAG_Final.json         RAG sub-flow export
|-- historical_projects/            26 fictitious project markdown files
|   |-- 01_forgenova_ev_battery_expansion.md
|   |-- ... (26 files total)
|-- prompts/                        Agent system prompts
|   |-- PROMPTING_METHODOLOGY.md
|   |-- orchestrator_prompt.md
|   |-- planner_prompt.md
|   |-- risk_assessor_prompt.md
|   |-- status_reporter_prompt.md
|   |-- governance_prompt.md
|   |-- final_synthesizer_prompt.md
|-- evals/                          Evaluation suite
|   |-- mira_eval_suite.py          Full eval with LLM judge
|   |-- mira_eval.py                Basic content eval
|   |-- mira_hallucination_eval.py  Hallucination detection
|   |-- mira_single_test.py         Quick single project test
|   |-- results/                    CSV and JSON eval outputs
|-- maintenance/                    Vector store maintenance
|   |-- health_check.py             Daily collection health check
|   |-- reingest.py                 Smart re-ingest changed files
|   |-- full_reingest.py            Full collection rebuild
|   |-- cache_manager.py            Embedding cache management
|   |-- verify_chunks.py            Verify all projects present
|   |-- README_MAINTENANCE.md       Maintenance guide
|-- docs/
|   |-- PHASE2_ROADMAP.md           Phase 2 product roadmap
|-- .vscode/
|   |-- launch.json                 VSCode run configurations
```

---

## About the Fictitious Data

All project data in `historical_projects/` is completely fabricated:

- **ForgeNova Automotive** - fictional company, does not exist
- **26 project documents** - AI-generated scenarios for learning purposes
- **Risk Matrix** - fabricated risk data in Google Sheets for demo purposes
- **All timelines, budgets, team sizes** - fictional numbers for educational use

This data was specifically designed to test RAG retrieval, grounding, and
hallucination detection in a multi-agent AI system.

---

## Prerequisites

- Langflow Desktop 1.9.2 (Mac)
- Python 3.12+
- OpenAI API key
- Anthropic API key
- Google Service Account JSON (for Sheets access)

---

## How to Run MIRA

### Step 1 - Clone the Repository

```bash
git clone https://github.com/rjtom/mira-project-intelligence-assistant
cd mira-project-intelligence-assistant
```

### Step 2 - Install Dependencies

```bash
~/.langflow/.langflow-venv/bin/pip install -r requirements.txt
```

### Step 3 - Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### Step 4 - Set Up Chroma Vector Store

```bash
~/.langflow/.langflow-venv/bin/python3 maintenance/full_reingest.py
~/.langflow/.langflow-venv/bin/python3 maintenance/verify_chunks.py
```

Expected output:
```
Total chunks: ~208
Projects: 26/26
Status: PASS
```

### Step 5 - Import Flows into Langflow Desktop

1. Open Langflow Desktop
2. Import `flows/MIRA_3_0_Final.json` as the main flow
3. Import `flows/MIRA_RAG_Final.json` as the RAG flow
4. Configure API keys in Langflow Global Variables

### Step 6 - Configure Custom Components

MIRA_Project_RAG component:
- Chroma Path: `/Users/YOUR_USERNAME/.langflow/chroma_db`
- Collection Name: `MIRARAG`
- OpenAI API Key: your key

MIRA Risk Matrix Reader:
- Service Account JSON: path to your Google Service Account file
- Spreadsheet ID: your Google Sheets ID
- Range: `Risks_Master!A1:Z1000`

### Step 7 - Test MIRA

```bash
~/.langflow/.langflow-venv/bin/python3 evals/mira_single_test.py
```

Or in Langflow Playground:
```
What is the timeline for ForgeNova EV Battery Gigafactory Expansion?
What are the major risks for ForgeNova Autonomous Driving Platform?
What lessons were learned from ForgeNova DevOps Pipeline Transformation?
```

### Step 8 - Run Full Eval Suite

```bash
~/.langflow/.langflow-venv/bin/python3 evals/mira_eval_suite.py
```

156 queries across 26 projects. ~45 minutes. Results saved to `evals/results/`

---

## Vector Store Maintenance

```bash
# Daily health check
~/.langflow/.langflow-venv/bin/python3 maintenance/health_check.py

# After updating project files
~/.langflow/.langflow-venv/bin/python3 maintenance/reingest.py
~/.langflow/.langflow-venv/bin/python3 maintenance/cache_manager.py --clear-all
~/.langflow/.langflow-venv/bin/python3 maintenance/verify_chunks.py

# Monthly full rebuild
~/.langflow/.langflow-venv/bin/python3 maintenance/full_reingest.py
```

See [maintenance/README_MAINTENANCE.md](maintenance/README_MAINTENANCE.md) for cron schedule and runbooks.

---

## Evaluation Framework

### Layer 1 - Content Pass/Fail
- 26 projects x 6 questions = 156 queries
- Checks: project name present, question keywords, not generic, >200 chars

### Layer 2 - Hallucination Detection
- RAG responses vs markdown source files
- Risk responses vs Google Sheets data

### Layer 3 - LLM as Judge (Claude Sonnet)

| Dimension | What It Measures |
|-----------|-----------------|
| Factual Accuracy | Facts correct vs ground truth |
| Groundedness | Based on source data |
| Completeness | Covers key information |
| Hallucination Free | No fabricated details |
| Relevance | Answers the question |

Target: Overall score >= 7.5/10

---

## Performance Results

| Metric | Target | Result |
|--------|--------|--------|
| Content pass rate | >95% | **100%** (156/156) |
| LLM Judge score | >7.5/10 | Pending Anthropic key |
| Avg response time | <25s | 27.7s |
| Cost per query | <$0.10 | ~$0.05 |
| Total eval queries | 156 | 156 |
| Projects tested | 26 | 26 |

---

## Known Issues & Resolutions

| Issue | Root Cause | Resolution |
|-------|-----------|-----------|
| Langflow self-call deadlock | HTTP calls during flow execution | MIRA_Project_RAG calls Chroma directly |
| Astra DB incompatibility | Langflow 1.9.2 upgrade | Migrated to local Chroma DB |
| GPT ignores tool instructions | Training data confidence | Switched to Claude for all RAG agents |
| Chroma $in filter failure | Timestamp-based chunk IDs | Use col.get() with where filter |
| DevOps chunks missing | Ingestion script skipped file | Re-ingested with timestamp IDs |
| Embedding cache stale | Cache hit before new chunks | Clear cache after ingestion |

---

## Phase 2 Roadmap

See [docs/PHASE2_ROADMAP.md](docs/PHASE2_ROADMAP.md) for:
- Email Status Report Addon (automated weekly reports)
- Planning View (web interface)
- Risk Assessor View (web interface)
- Governance View (web interface)
- Target: 2-week delivery

---

## Risk Management

See [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md) for:
- 15 identified system risks
- 5 risks resolved during development
- HIL checkpoint requirements
- Monitoring approach

---

Supporting human wisdom, not replacing it.

**Raju Thomas**
Capstone Project - Applied Agentic AI
June 2026
