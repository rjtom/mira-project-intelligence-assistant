# MIRA Phase 2 — Product Roadmap

**Project**: MIRA Project Intelligence Assistant
**Author**: Raju Thomas
**Date**: June 2, 2026
**Status**: Planning Phase

---

## Overview

Phase 2 transforms MIRA from a chat interface into a full **Project Intelligence Platform** with automated reporting, real-time dashboards, and role-based views for PMs, TPMs, and executives.

---

## Feature 1 — Email Status Report Addon

### Description
Automated weekly email reports delivered to PM/TPM distribution lists. MIRA runs a full project scan every Monday morning and delivers a concise intelligence brief to all stakeholders.

### Architecture
```
Scheduler (cron/n8n)
     ↓ triggers every Monday 8AM
MIRA API (all 26 projects)
     ↓ runs Status Reporter + Risk Assessor
Report Generator (Python)
     ↓ formats HTML email
Email Service (SendGrid/AWS SES)
     ↓ delivers to distribution list
Stakeholders (PMs, TPMs, Executives)
```

### Email Report Structure
```
Subject: MIRA Weekly Intelligence Brief — Week of {date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MIRA Project Intelligence Brief
Week of {date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 ON TRACK (12 projects)
🟡 AT RISK (8 projects)  
🔴 NEEDS ATTENTION (6 projects)

─────────────────────────────────
🔴 PROJECTS NEEDING ATTENTION
─────────────────────────────────
1. ForgeNova Autonomous Driving Platform
   Status: Phase 3 delays
   Risk Score: 18 (HIGH)
   HIL Required: Yes — Safety Board review needed
   Action: Schedule executive review by Friday

2. ForgeNova Global ERP Migration
   Status: Budget overrun risk
   Risk Score: 15 (HIGH)
   HIL Required: Yes — CFO approval needed
   Action: Financial review required

─────────────────────────────────
📊 RISK SUMMARY
─────────────────────────────────
High Risk Projects: 6
Average Risk Score: 11.2
New Risks This Week: 3
Resolved Risks: 1

─────────────────────────────────
🎯 THIS WEEK'S HIL CHECKPOINTS
─────────────────────────────────
• ForgeNova Autonomous Driving — Safety Board (Thu)
• ForgeNova ERP Migration — CFO Review (Wed)
• ForgeNova Cybersecurity — CISO Sign-off (Fri)

─────────────────────────────────
"Supporting human wisdom, not replacing it."
MIRA Project Intelligence Assistant
─────────────────────────────────
```

### Technical Implementation
- **Scheduler**: n8n or cron job
- **Email**: SendGrid API or AWS SES
- **Template**: Jinja2 HTML email template
- **Delivery**: Per project or consolidated report
- **Personalization**: Role-based content (Executive vs PM view)

### Configuration
```python
EMAIL_CONFIG = {
    "schedule": "every Monday 8AM EST",
    "recipients": {
        "executives": ["cto@forgenova.com"],
        "pms": ["pm-team@forgenova.com"],
        "tpms": ["tpm-team@forgenova.com"]
    },
    "report_type": "consolidated",  # or "per_project"
    "include_risks": True,
    "include_hil": True,
    "risk_threshold_alert": 15
}
```

---

## Feature 2 — Web Interface — Three Role-Based Views

### Architecture
```
React Frontend (Next.js)
     ↓ API calls
FastAPI Backend
     ↓ calls
MIRA Langflow API
     ↓ retrieves
Chroma DB + Google Sheets
```

---

### View 1 — Planning View

**Target User**: Project Managers, TPMs
**Purpose**: Project timeline, milestones, resources at a glance

**Layout**:
```
┌─────────────────────────────────────────────┐
│  MIRA Planning View                    🔍    │
├─────────────────────────────────────────────┤
│  Project Selector: [ForgeNova EV Battery ▼] │
├──────────────┬──────────────────────────────┤
│              │  Q1 2024  Q2 2024  Q3 2024   │
│  Timeline    │  ████████ ████████ ████████  │
│              │  Infra    Tech Int  Training  │
├──────────────┼──────────────────────────────┤
│  Objectives  │  • Double production capacity │
│              │  • Maintain quality standards │
│              │  • Achieve sustainability     │
├──────────────┼──────────────────────────────┤
│  Resources   │  👥 450 team members          │
│              │  💰 Significant investment    │
│              │  🤝 Multiple tech partners    │
├──────────────┼──────────────────────────────┤
│  Status      │  🟢 Completed Successfully   │
├──────────────┼──────────────────────────────┤
│  Ask MIRA    │  [What lessons were learned?] │
└──────────────┴──────────────────────────────┘
```

**Components**:
- Project selector dropdown (all 26 projects)
- Interactive Gantt chart (timeline)
- Objectives checklist
- Resource summary cards
- Status indicator (🟢🟡🔴)
- Embedded MIRA chat for follow-up questions
- Export to PDF button

---

### View 2 — Governance View

**Target User**: Governance Officers, Compliance Teams, Executives
**Purpose**: HIL checkpoints, compliance status, human oversight requirements

**Layout**:
```
┌─────────────────────────────────────────────┐
│  MIRA Governance View                  🔍    │
├─────────────────────────────────────────────┤
│  Project: [All Projects ▼]  Week: [Current] │
├──────────────────────────────────────────────┤
│  HIL CHECKPOINTS THIS WEEK                  │
│  ┌──────────────────────────────────────┐   │
│  │ 🔴 Safety Board Review — Thu 2PM     │   │
│  │    ForgeNova Autonomous Driving       │   │
│  │    [Mark Complete] [Escalate]        │   │
│  ├──────────────────────────────────────┤   │
│  │ 🟡 CFO Approval — Wed EOD           │   │
│  │    ForgeNova ERP Migration           │   │
│  │    [Mark Complete] [Reschedule]      │   │
│  └──────────────────────────────────────┘   │
├──────────────────────────────────────────────┤
│  COMPLIANCE DASHBOARD                       │
│  Regulatory: 🟢 18/26  Safety: 🟡 22/26    │
│  Ethics: 🟢 26/26     Budget: 🟡 20/26     │
├──────────────────────────────────────────────┤
│  CRITICAL THINKING ANALYSIS                 │
│  Assumptions Challenged: 12 this week       │
│  Human Impact Reviews: 8 completed          │
└──────────────────────────────────────────────┘
```

**Components**:
- HIL checkpoint calendar and task list
- Compliance status dashboard
- Decision log (who approved what, when)
- Critical thinking analysis tracker
- Escalation workflow
- Audit trail export

---

### View 3 — Risk Assessor View

**Target User**: Risk Officers, PMO, Executives
**Purpose**: Live risk matrix, scores, mitigations across all projects

**Layout**:
```
┌─────────────────────────────────────────────┐
│  MIRA Risk Intelligence View           🔍    │
├─────────────────────────────────────────────┤
│  Filter: [All Projects ▼] [All Categories ▼]│
├──────────────────────────────────────────────┤
│  RISK HEATMAP                               │
│        Low    Medium   High                 │
│  High  🟡      🔴       🔴                  │
│  Med   🟢      🟡       🔴                  │
│  Low   🟢      🟢       🟡                  │
├──────────────────────────────────────────────┤
│  TOP RISKS                                  │
│  ┌──────────────────────────────────────┐   │
│  │ Score 18 │ Autonomous Driving        │   │
│  │ Safety   │ Sensor fusion reliability │   │
│  │ HIL: YES │ [View Details] [Mitigate] │   │
│  ├──────────────────────────────────────┤   │
│  │ Score 15 │ ERP Migration            │   │
│  │ Financial│ Budget overrun risk       │   │
│  │ HIL: YES │ [View Details] [Mitigate] │   │
│  └──────────────────────────────────────┘   │
├──────────────────────────────────────────────┤
│  RISK TRENDS                                │
│  [Line chart — risk scores over time]       │
├──────────────────────────────────────────────┤
│  Ask MIRA about risks...                    │
│  [What are the top risks this quarter?    ] │
└──────────────────────────────────────────────┘
```

**Components**:
- Interactive risk heatmap (Impact vs Likelihood)
- Sortable risk register table
- Risk score trend charts
- Mitigation action tracker
- HIL requirement flags
- Export to Excel/PDF
- Embedded MIRA chat for risk questions

---

## Technical Stack for Phase 2

### Frontend
```
Next.js 14 (React)
Tailwind CSS
Recharts (data visualization)
shadcn/ui (components)
```

### Backend
```
FastAPI (Python)
Langflow API integration
Google Sheets API
SendGrid (email)
```

### Infrastructure
```
Vercel (frontend hosting)
Railway or Render (backend)
Existing Chroma DB
Existing Langflow flows
```

---

## Implementation Timeline

| Phase | Feature | Timeline | Effort |
|-------|---------|----------|--------|
| 2.1 | Email Status Report | Week 1-2 | Medium |
| 2.2 | Planning View | Week 2-4 | Medium |
| 2.3 | Risk Assessor View | Week 3-5 | Medium |
| 2.4 | Governance View | Week 4-6 | High |
| 2.5 | Integration & Testing | Week 6-7 | Medium |
| 2.6 | Launch | Week 8 | Low |

---

## Connection to inaibridge.ai

Phase 2 becomes the foundation for the **inaibridge.ai enterprise platform**:

```
MIRA Phase 2 (ForgeNova)
        ↓
inaibridge.ai Platform
        ↓
White-label for any enterprise PMO
        ↓
Multi-tenant SaaS product
```

---

*"Supporting human wisdom, not replacing it."*

**Raju Thomas**
Capstone Project — Applied Agentic AI
June 2026
