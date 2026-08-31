# CoCoIceberg — Risk & Compliance Copilot

**AI-powered AML/CFT compliance intelligence built entirely on Snowflake**

> Built for the Snowflake Hackathon 2026 | Team CoCoIceberg

---

## What It Does

CoCoIceberg is an end-to-end compliance intelligence system that helps financial institutions detect fraud, assess risk, investigate alerts, and generate regulatory filings — all through natural language. It combines Snowflake's Cortex AI functions, Dynamic Tables, Semantic Views, and Cortex Search into a single Streamlit application with a multi-agent AI copilot at its core.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CoCoIceberg — Architecture                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    STREAMLIT IN SNOWFLAKE (Frontend)                      │   │
│  │                                                                           │   │
│  │  ┌──────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │ Ask CoCo │ │ AML Fraud │ │Credit Risk│ │Liquidity │ │ Velocity   │  │   │
│  │  │ (Chat)   │ │ Dashboard │ │ Dashboard │ │ Dashboard│ │ Anomalies  │  │   │
│  │  └────┬─────┘ └─────┬─────┘ └─────┬─────┘ └────┬─────┘ └─────┬──────┘  │   │
│  │       │              │              │             │              │         │   │
│  │  ┌────┴──────┐  ┌───┴──────────────┴─────────────┴──────────────┴──┐     │   │
│  │  │            │  │         AI INTELLIGENCE LAYER                     │     │   │
│  │  │Investigation│  │  Live pipeline steps → Cortex LLM → Colored     │     │   │
│  │  │ Workspace  │  │  insight cards (Risk Posture, Threats, Actions)  │     │   │
│  │  │            │  │  Runs on every dashboard page automatically      │     │   │
│  │  └────┬───────┘  └─────────────────┬───────────────────────────────┘     │   │
│  │       │                            │                                      │   │
│  │  ┌────┴────────────────────────────┴──────────────────────────────┐      │   │
│  │  │              Report Generator                                   │      │   │
│  │  │    (STR / CTR / LCR / CDD Reports)                             │      │   │
│  │  └────────────────────────────────────────────────────────────────┘      │   │
│  └───────┼────────────────────────────┼──────────────────────────────────────┘   │
│          │                            │                                          │
├──────────┼────────────────────────────┼──────────────────────────────────────────┤
│          │     CORTEX AI LAYER        │                                          │
│  ┌───────┴────────────────────────────┴──────────────────────────────────────┐   │
│  │                                                                            │   │
│  │  ┌────────────┐  ┌───────────────┐  ┌─────────────┐  ┌────────────────┐  │   │
│  │  │ AI_CLASSIFY│  │Cortex Analyst │  │Cortex Search│  │Cortex Complete │  │   │
│  │  │  (Intent)  │  │  (NL → SQL)   │  │ (Policy RAG)│  │ (Governed LLM)│  │   │
│  │  └────────────┘  └───────────────┘  └─────────────┘  └────────────────┘  │   │
│  │                                                                            │   │
│  │  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐ │   │
│  │  │ AI_PARSE_DOCUMENT│  │  AI_EXTRACT        │  │  Document Intelligence │ │   │
│  │  │ (OCR / Parse)    │  │ (Structured Fields)│  │  (Unstructured → Data) │ │   │
│  │  └──────────────────┘  └───────────────────┘  └────────────────────────┘ │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│          DATA LAYER (Dynamic Tables + Views)                                     │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                            │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │V_AML_SCORING│  │V_CREDIT_RISK │  │V_LIQUIDITY   │  │V_VELOCITY    │  │   │
│  │  │(Dynamic Tbl)│  │(Dynamic Tbl) │  │_RISK (DT)    │  │_ANOMALY (DT) │  │   │
│  │  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│  │         │                 │                  │                  │          │   │
│  │  ┌──────┴─────────────────┴──────────────────┴──────────────────┴──────┐  │   │
│  │  │              BASE TABLES (Relational Schema)                          │  │   │
│  │  │  CUSTOMERS | ACCOUNTS | TRANSACTIONS | ALERTS | POLICIES             │  │   │
│  │  └─────────────────────────────────────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│          SEMANTIC & SEARCH LAYER                                                 │
│  ┌────────────────────────┐  ┌────────────────────────────────────────────────┐  │
│  │   SV_RISK_COPILOT      │  │  POLICY_SEARCH_SERVICE                         │  │
│  │   (Semantic View)      │  │  (Cortex Search over RBI/PMLA/Basel docs)      │  │
│  │   Measures, Dimensions │  │  Regulatory citation retrieval                  │  │
│  │   Relationships, Joins │  │  for STR/CTR narrative generation               │  │
│  └────────────────────────┘  └────────────────────────────────────────────────┘  │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│          EXTERNAL INTEGRATIONS                                                   │
│  ┌────────────────────┐  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │  MCP (Jira)        │  │  CoCo CLI (Desktop) │  │  Cron Automation         │  │
│  │  Compliance ticket │  │  Reusable Skill      │  │  Daily risk monitoring   │  │
│  │  creation          │  │  (risk-compliance-   │  │  GET_RISK_SUMMARY()      │  │
│  │                    │  │   copilot)           │  │  scheduled @ 9:37am      │  │
│  └────────────────────┘  └─────────────────────┘  └──────────────────────────┘  │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Ask CoCo — 5-Step AI Pipeline                              │
└──────────────────────────────────────────────────────────────────────────────┘

  User Question
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  1. INTENT   │────▶│  AI_CLASSIFY → Routes to:                              │
│  CLASSIFIER  │     │  FRAUD_AND_AML | CREDIT_RISK | LIQUIDITY_RISK |        │
│              │     │  REGULATORY_POLICY | REPORT_GENERATION | GENERAL        │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  2. CORTEX   │────▶│  NL → SQL via Semantic View (SV_RISK_COPILOT)          │
│  ANALYST     │     │  Returns: SQL query + structured data results           │
│              │     │  Grounded in verified measures & dimensions              │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  3. CORTEX   │────▶│  RAG over regulatory policy corpus                      │
│  SEARCH      │     │  RBI Master Directions, PMLA 2002, Basel III, FATF      │
│  (Policy RAG)│     │  Returns: Relevant regulation sections with citations   │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  4. CONFIDENCE│───▶│  Assess evidence quality:                               │
│  ASSESSOR    │     │  HIGH (≥2 data sources) → Proceed with full answer      │
│              │     │  MEDIUM (1 source) → Answer with caveats                │
│              │     │  LOW (0 sources) → Warn user, suggest investigation     │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  5. GOVERNED │────▶│  CORTEX.COMPLETE synthesizes final answer:               │
│  LLM         │     │  • Cites data from Analyst results                      │
│              │     │  • References policy from Search                         │
│              │     │  • Applies compliance guardrails                         │
│              │     │  • Shows confidence badge (HIGH/MEDIUM/LOW)              │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
  AI Response with Evidence + Citations + Confidence Score
```

---

## Dashboard AI Intelligence Pipeline

Each dashboard page (AML Fraud, Credit Risk, Liquidity Risk, Velocity Anomalies) runs its own AI pipeline with live step-by-step visualization:

```
  Page Load
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  1. DATA     │────▶│  Fetch from Dynamic Tables / Views                     │
│  LOADING     │     │  ✓ "10 AML risk profiles loaded"                       │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  2. PROFILE  │────▶│  Extract key fields into clean format                  │
│  PREPARATION │     │  ✓ "Top 5 risk profiles prepared"                      │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  3. CORTEX   │────▶│  SNOWFLAKE.CORTEX.COMPLETE (llama3.1-8b)               │
│  LLM         │     │  Generates: Risk posture, threats, actions             │
│              │     │  ✓ "AI assessment complete"                            │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────┐
  │  COLORED INSIGHT CARDS                                   │
  │  ┌─────────────┐  ┌─────────────────────────────────┐  │
  │  │ Risk Posture │  │ Top Threats / Critical Accounts │  │
  │  │ (color-coded)│  │ (specific customer names)       │  │
  │  └─────────────┘  └─────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────────────┐  │
  │  │ Recommended Actions (FREEZE/COLLECT/REPORT)       │  │
  │  └───────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────┘
```

---

## Report Generation Pipeline

All 4 report types (STR, CTR, LCR, CDD) follow the same AI-powered generation flow:

```
  User selects report type + clicks "Generate"
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  1. DATA     │────▶│  Compile relevant data (transactions, accounts, KYC)   │
│  COMPILATION │     │  ✓ "5 accounts compiled" / "8 high-risk profiles"      │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  2. CORTEX   │────▶│  SNOWFLAKE.CORTEX.COMPLETE generates formal narrative  │
│  LLM         │     │  Regulatory language, citations, pattern analysis      │
└──────────────┘     └────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  3. PDF      │────▶│  FPDF2 builds professional PDF with:                   │
│  BUILDER     │     │  • Data tables, narrative, SHA-256 hash                │
│              │     │  • CONFIDENTIAL header, signature blocks               │
│              │     │  ✓ "PDF ready" → Download button                       │
└──────────────┘     └────────────────────────────────────────────────────────┘
```

---

## Investigation & Compliance Workflow

```
  Alert Triggered (OPEN)
       │
       ▼
┌──────────────────┐     ┌─────────────────────────────────────┐
│  Investigation   │────▶│  AI generates formal report:         │
│  Workspace       │     │  • Subject profile + KYC review      │
│                  │     │  • Transaction evidence (risk > 50)  │
│  Select Alert    │     │  • AML composite score               │
│  Review Evidence │     │  • Typology match (FATF)             │
└──────────────────┘     └─────────────────────────────────────┘
       │                            │
       ├────────────────────────────┤
       ▼                            ▼
┌──────────────┐           ┌────────────────┐
│  Escalate    │           │  Create Jira   │
│  Alert       │           │  Ticket (MCP)  │
│  (Stored     │           │                │
│   Procedure) │           │  → FOR project │
└──────────────┘           └────────────────┘
                                    │
                                    ▼
                           ┌────────────────┐
                           │  Report        │
                           │  Generator     │
                           │  STR/CTR/LCR/  │
                           │  CDD Reports   │
                           │  AI Narrative + │
                           │  PDF Download  │
                           └────────────────┘
```

---

## Snowflake Features & CoCo Capabilities Used

| Category | Feature | How We Use It |
|----------|---------|---------------|
| **Cortex AI** | AI_CLASSIFY | Semantic intent routing for user queries |
| **Cortex AI** | Cortex Analyst | NL-to-SQL via Semantic View for all dashboards |
| **Cortex AI** | Cortex Search | RAG over RBI/PMLA/Basel regulatory policies |
| **Cortex AI** | Cortex Complete | Investigation reports, STR narratives, governed answers, **AI Intelligence on every dashboard** |
| **Cortex AI** | AI_PARSE_DOCUMENT | Unstructured compliance document processing |
| **Data Platform** | Dynamic Tables | Real-time risk scoring (AML, Credit, Liquidity, Velocity) |
| **Data Platform** | Semantic View | Data ontology with measures, dimensions, relationships |
| **Data Platform** | Stored Procedures | ESCALATE_ALERT, GET_RISK_SUMMARY, FLAG_FOR_STR |
| **App Platform** | Streamlit in Snowflake | Full application hosting |
| **CoCo** | Reusable Skill | Published `risk-compliance-copilot` skill for other teams |
| **CoCo** | MCP (Jira) | Compliance ticket creation in Jira via MCP connector |
| **CoCo** | Cron Automation | Daily risk summary monitoring (scheduled at 9:37am) |
| **CoCo** | Custom Tools | 3 stored procedures callable by the CoCo agent |
| **CoCo** | Multi-Agent Pipeline | 5-step chain: Classify → Analyst → Search → Assess → LLM |
| **CoCo** | Guardrails | Input validation, confidence scoring, graceful fallback |

---

## Hackathon Ingenuity Criteria

| Criteria | What We Built |
|----------|---------------|
| **Reusable & shareable skills** | Published `risk-compliance-copilot` skill to stage — other teams can install via `cortex skill add` |
| **MCP connectors to external tools** | Jira MCP integration — creates compliance tickets in Jira directly from the Investigation page |
| **Automations & scheduled runs** | CoCo cron job runs daily, calls `GET_RISK_SUMMARY()`, reports critical risk thresholds |
| **Custom tools & function calling** | 3 stored procedures (ESCALATE_ALERT, GET_RISK_SUMMARY, FLAG_FOR_STR) — real actions, not just text |
| **Multi-agent orchestration** | 5-step pipeline in Ask CoCo + AI Intelligence pipeline on every dashboard with live step-by-step progress visualization |
| **Working across surfaces** | Streamlit (Snowsight) + CoCo CLI (Desktop) + Published Skill + Cron automation |
| **Guardrails & graceful fallback** | Input length validation, confidence badges (HIGH/MEDIUM/LOW), try/except with user-friendly errors, evidence-based scoring |
| **Real World Relevance** | AI-powered dashboards don't just show data — they interpret it, name specific risky customers, and recommend concrete actions (FREEZE/COLLECT/ESCALATE) |

---

## Pages

| Page | Purpose |
|------|---------|
| **Ask CoCo** | Natural language copilot — ask anything about fraud, risk, compliance. 5-step AI pipeline with live progress visualization |
| **AML Fraud** | AI Risk Intelligence (live threat assessment, top threats, actions) + AML composite scoring + fraud signal detection + alert severity tracking |
| **Credit Risk** | AI Credit Risk Intelligence (portfolio health, critical accounts, actions) + NPA scoring + bounce tracking + risk narratives |
| **Liquidity Risk** | AI Liquidity Intelligence (stress assessment, highest risk, actions) + outflow ratios + balance deterioration monitoring |
| **Velocity Anomalies** | AI Velocity Intelligence (threat level, suspects, actions) + transaction velocity spikes + multi-country pattern detection |
| **Investigation** | Deep-dive into alerts, AI-generated investigation reports, Jira ticket creation |
| **Report Generator** | AI-generated regulatory filings with PDF export — STR, CTR, LCR, CDD. Each report has Generate button, live pipeline steps, AI narrative, and downloadable PDF with SHA-256 integrity hash |

---

## Quick Start

**Live App URL:** `https://app.snowflake.com/opxbaih/uu49750/#/streamlit-apps/RISK_COPILOT_DB.RISK_COPILOT.RISK_COMPLIANCE_COPILOT`

> **Judge Access:** Login credentials are shared separately via the hackathon submission form. Use the direct app URL above — it opens the app immediately after login.

```sql
-- The app is deployed at:
-- Database: RISK_COPILOT_DB
-- Schema: RISK_COPILOT
-- Streamlit: RISK_COMPLIANCE_COPILOT

-- View in Snowsight:
SHOW STREAMLITS IN RISK_COPILOT_DB.RISK_COPILOT;

-- Or use CoCo CLI skill:
-- cortex skill add risk-compliance-copilot --from-stage @RISK_COPILOT_DB.RISK_COPILOT.STREAMLIT_STAGE/skills/
```

---

## Data Model

```
CUSTOMERS (10 customers)
    │
    ├── ACCOUNTS (1:N)
    │       │
    │       └── TRANSACTIONS (1:N, ~300 txns)
    │
    ├── ALERTS (1:N, risk alerts)
    │
    └── COMPLIANCE_TICKETS (1:N, Jira-synced)

POLICIES (regulatory corpus → Cortex Search)

Dynamic Table Views:
    V_AML_SCORING       — Composite AML risk per customer
    V_CREDIT_RISK       — NPA and credit exposure scores
    V_LIQUIDITY_RISK    — LCR and outflow stress
    V_VELOCITY_ANOMALY  — Transaction velocity spikes
```

---

## Team

**Team CoCoIceberg** — Snowflake Hackathon 2026

Built with Snowflake Cortex, Streamlit in Snowflake, and CoCo CLI.
