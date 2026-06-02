# MIRA Risk Management Document

**Capstone Project** - Applied Agentic AI for Product Managers & Technical Program Managers
**Author**: Raju Thomas
**Date**: June 2, 2026

---

## 1. Risk Management Philosophy

MIRA's risk management is grounded in the same philosophy as the entire system:

I am Mira. I exist to help you navigate projects with clarity, honesty, and care.
Risk is a human reality - involving real people, perception, uncertainty,
effort, and long-term consequences. My goal is not to replace your wisdom,
but to support it.

---

## 2. Risk Management Approach

- Risk Assessor Agent (claude-sonnet-4-5) generates risks on-demand
- MIRA Risk Matrix Reader reads live data from Google Sheets
- All risk outputs reviewed by the Governance Agent
- Emphasis on Human-in-the-Loop (HIL), critical thinking, transparency

---

## 3. MIRA System Risk Register

| Risk ID | Category | Description | Impact | Likelihood | Score | Status |
|---------|----------|-------------|--------|------------|-------|--------|
| R001 | RAG Grounding | Retrieved context may not fully cover query | High | Medium | 15 | Active |
| R002 | Hallucination | Agent fabricates details not in context | High | Medium | 15 | High Priority |
| R003 | Philosophical Drift | Responses become mechanical | Medium | High | 12 | Monitored |
| R004 | Performance & Latency | Multi-agent flow too slow | Medium | High | 12 | Active |
| R005 | Scope Creep | Adding features beyond capstone scope | Medium | High | 12 | Controlled |
| R006 | Evaluation Bias | Overly positive self-assessment | Medium | Medium | 9 | Active |
| R007 | Data Quality | Historical files lack depth | High | Low | 5 | Completed |
| R008 | LLM Cost & Rate Limits | High token usage | Medium | Medium | 9 | Monitored |
| R009 | User Understanding | Evaluators miss philosophical depth | Medium | Medium | 9 | Preparing |
| R010 | Over-Reliance on AI | Users trust MIRA too much | Medium | Medium | 9 | High Priority |
| R011 | Langflow Deadlock | Agents cannot HTTP-call sub-flows | High | High | 20 | Resolved |
| R012 | Vector Store Migration | Astra DB incompatibility | High | Medium | 15 | Resolved |
| R013 | Embedding Contamination | Duplicate ingestion corrupts store | Medium | Medium | 9 | Resolved |
| R014 | GPT Tool Ignoring | GPT models skip tool calls | High | High | 20 | Resolved |
| R015 | Chroma Filter Failure | $in filter fails with timestamp IDs | High | High | 20 | Resolved |

---

## 4. Key Resolutions During Development

### R011 - Langflow Deadlock (Resolved)
Root Cause: Langflow cannot HTTP-call itself during flow execution.
Solution: MIRA_Project_RAG calls Chroma directly - no HTTP calls.

### R014 - GPT Tool Ignoring (Resolved)
Root Cause: GPT answers from training data instead of calling tools.
Solution: Switched Planner and Status Reporter to Claude Haiku.

### R015 - Chroma Filter Failure (Resolved)
Root Cause: Timestamp-based chunk IDs break col.query() $in filter.
Solution: Use col.get() with where filter instead of col.query().

---

## 5. Overall Risk Summary

- Total Risks: 15
- Resolved: R011, R012, R013, R014, R015 (5 risks)
- Active: R001, R002, R003, R004, R005, R006, R008, R009, R010
- Residual Risk Level: Low to Medium

---

## 6. HIL Checkpoints

| Decision Type | HIL Requirement | Who Decides |
|--------------|----------------|------------|
| Risk Score > 15 | Executive review required | Project Sponsor |
| Regulatory compliance | Mandatory human sign-off | Legal + Compliance |
| Safety-critical decisions | Phase gate approval | Safety Board |
| Talent decisions | HR leadership approval | CHRO |
| Technology changes | Technical review board | CTO |
| Budget > threshold | Finance approval | CFO |

---

## 7. Monitoring

- Eval Suite - 156 automated queries across 26 projects
- LLM Judge - Claude Sonnet scores every response 0-10
- Hallucination Detection - vs source documents
- Governance Agent - flags HIL checkpoints on every query

---

Supporting human wisdom, not replacing it.

Raju Thomas
Capstone Project - Applied Agentic AI
June 2026
