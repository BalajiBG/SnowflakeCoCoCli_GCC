---
name: risk-compliance-copilot
description: >
  Banking risk and compliance copilot skill. Surfaces fraud signals, credit/liquidity risk,
  and produces audit-ready regulatory outputs (STR, CTR, Basel reports) from natural language.
  Uses Cortex Search for policy RAG and Cortex Complete for governed answers with evidence chains.
triggers:
  - fraud detection
  - AML alert
  - suspicious transaction
  - structuring
  - money laundering
  - credit risk
  - NPA classification
  - liquidity risk
  - LCR
  - regulatory report
  - STR filing
  - CTR filing
  - Basel III
  - compliance
  - risk copilot
  - banking risk
  - NBFC risk
---

# Risk & Compliance Copilot Skill

## Overview
This skill provides an AI-powered risk and compliance copilot for banking and NBFC teams.
It combines structured transaction/account data with regulatory policy documents to deliver
governed, explainable, evidence-backed answers to compliance questions.

## Capabilities
1. **Fraud Signal Detection** - Identify structuring, round-tripping, rapid movement, trade mispricing
2. **Credit Risk Monitoring** - NPA early warning, consecutive bounces, concentration risk
3. **Liquidity Risk Assessment** - LCR/NSFR approximation, large outflow detection
4. **Policy Q&A** - RAG-based answers from RBI, Basel, PMLA, FEMA regulations
5. **Regulatory Report Generation** - Audit-ready STR, CTR, LCR, CDD reports with AI narratives, pipeline steps, and downloadable PDFs with SHA-256 integrity hashes
6. **AI Dashboard Intelligence** - Every dashboard page has live AI-generated risk posture, named threats/suspects, and actionable recommendations with pipeline step visualization

## Prerequisites
- Database: `RISK_COPILOT_DB` with schema `RISK_COPILOT`
- Tables: CUSTOMERS, ACCOUNTS, TRANSACTIONS, ALERTS, REGULATORY_POLICIES, FILINGS
- Views: V_FRAUD_SIGNALS, V_CREDIT_RISK, V_LIQUIDITY_RISK, V_AML_SCORING
- Dynamic Tables: DT_REALTIME_RISK_SUMMARY, DT_TXN_VELOCITY_MONITOR
- Cortex Search Service: POLICY_SEARCH_SERVICE
- Semantic View: SV_RISK_COPILOT
- LLM: llama3.1-8b for dashboard AI Intelligence, llama3.1-70b for Ask CoCo governed answers (via SNOWFLAKE.CORTEX.COMPLETE)

## Usage

### Quick Risk Summary
```
Ask: "Show me all critical risk signals across the portfolio"
```

### Fraud Investigation
```
Ask: "Which customers show cash structuring patterns below 10 lakh?"
Ask: "Show round-tripping activity for Shell Holdings"
```

### Policy Questions
```
Ask: "What are the RBI requirements for STR filing timelines?"
Ask: "What is the minimum LCR under Basel III?"
```

### Report Generation
```
Ask: "Generate an STR for customer CUST013 based on structuring alerts"
Ask: "Produce a CTR report for all cash transactions above threshold"
```

## Architecture

```
User Question
    │
    ▼
Intent Classifier (CORTEX.COMPLETE)
    │
    ├── FRAUD → V_FRAUD_SIGNALS + V_AML_SCORING
    ├── CREDIT_RISK → V_CREDIT_RISK
    ├── LIQUIDITY → V_LIQUIDITY_RISK
    ├── POLICY → Cortex Search (POLICY_SEARCH_SERVICE)
    ├── REPORT → Evidence Assembly + LLM Generation
    └── GENERAL → SQL Generation against base tables
    │
    ▼
Evidence Chain Assembly
    │
    ▼
Governed Answer (with confidence level + citations)
```

## Guardrails
- **Confidence scoring**: HIGH (data + policy), MEDIUM (partial), LOW (insufficient)
- **Evidence requirement**: Every answer must cite specific data points
- **Regulatory grounding**: Policy search runs for all categories
- **No speculation**: LLM is instructed to stay within evidence bounds
- **Audit trail**: Generated SQL, data evidence, and policy citations preserved

## Key SQL Patterns

### Structuring Detection
```sql
SELECT c.FULL_NAME, COUNT(*) AS num_deposits, SUM(t.AMOUNT) AS total
FROM RISK_COPILOT_DB.RISK_COPILOT.TRANSACTIONS t
JOIN RISK_COPILOT_DB.RISK_COPILOT.ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
JOIN RISK_COPILOT_DB.RISK_COPILOT.CUSTOMERS c ON a.CUSTOMER_ID = c.CUSTOMER_ID
WHERE t.IS_CASH = TRUE AND t.AMOUNT BETWEEN 900000 AND 999999
GROUP BY c.FULL_NAME HAVING COUNT(*) >= 3;
```

### Composite AML Score
```sql
SELECT CUSTOMER_ID, FULL_NAME, COMPOSITE_AML_SCORE, RECOMMENDED_ACTION
FROM RISK_COPILOT_DB.RISK_COPILOT.V_AML_SCORING
WHERE COMPOSITE_AML_SCORE > 70
ORDER BY COMPOSITE_AML_SCORE DESC;
```

### Policy RAG Query
```sql
SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'RISK_COPILOT_DB.RISK_COPILOT.POLICY_SEARCH_SERVICE',
        '{"query": "<user question>", "columns": ["CONTENT","REGULATION_NAME","SECTION_TITLE"], "limit": 3}'
    )
)['results'] AS results;
```
