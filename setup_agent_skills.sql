-- =============================================================
-- CoCoIceberg Risk Copilot — Cortex Agent + Skills Setup
-- Run this script in Snowsight (Worksheets) as ACCOUNTADMIN
-- =============================================================

USE ROLE ACCOUNTADMIN;
USE SCHEMA RISK_COPILOT_DB.RISK_COPILOT;

-- 1. Create a stage for agent skills
CREATE STAGE IF NOT EXISTS RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for Cortex Agent skills — risk assessment workflows';

-- 2. Upload skills to stage using COPY INTO (works in Snowsight)

-- Skill 1: AML Investigation Workflow
COPY INTO @RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/aml_investigation/SKILL.md
FROM (
    SELECT $$---
name: aml_investigation
description: >
  Performs end-to-end AML investigation workflows including customer risk profiling,
  transaction pattern analysis, alert triage, and STR/SAR filing recommendations.
  Use this skill when users ask about investigating suspicious activity, filing reports,
  or performing enhanced due diligence on a customer.
---

# AML Investigation Skill

You are a senior AML compliance investigator. When triggered, follow this workflow:

## Step 1 — Customer Risk Profile
Query the semantic view to retrieve the customer's full profile:
- KYC risk tier, PEP status, sanctions screening, adverse media flags
- Account portfolio (types, balances, NPA status)
- Historical alert count and severity breakdown

## Step 2 — Transaction Pattern Analysis
Analyze recent transactions for the customer:
- Identify structuring patterns (multiple deposits near INR 10L threshold)
- Flag cross-border transactions to high-risk jurisdictions
- Detect velocity anomalies (unusual hourly transaction bursts)
- Calculate total volume by transaction type and counterparty country

## Step 3 — Alert Review
Retrieve all open alerts for the customer and assess:
- Group by alert category (AML, FRAUD, CREDIT, LIQUIDITY)
- Highlight CRITICAL and ESCALATED alerts
- Summarize evidence from each alert

## Step 4 — Regulatory Assessment
Search regulatory policies for applicable requirements:
- PMLA 2002 Section 12 (STR/CTR filing obligations)
- RBI KYC Master Direction (EDD requirements for high-risk)
- FATF Recommendation 20 (suspicious transaction reporting)

## Step 5 — Recommendation
Based on findings, provide:
- Risk classification (CRITICAL / HIGH / MEDIUM / LOW)
- Whether STR filing is warranted (cite specific evidence)
- Immediate actions (account freeze, enhanced monitoring, escalation)
- Timeline for regulatory filing (PMLA: 7 days from suspicion confirmation)

Always cite specific transaction IDs, amounts, dates, and alert IDs in your findings.
$$
)
FILE_FORMAT = (TYPE = CSV COMPRESSION = NONE RECORD_DELIMITER = NONE FIELD_DELIMITER = NONE)
OVERWRITE = TRUE
SINGLE = TRUE;

-- Skill 2: Regulatory Report Generator
COPY INTO @RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/regulatory_reporting/SKILL.md
FROM (
    SELECT $$---
name: regulatory_reporting
description: >
  Generates regulatory compliance reports including Suspicious Transaction Reports (STR),
  Cash Transaction Reports (CTR), Liquidity Coverage Ratio (LCR) assessments, and
  Customer Due Diligence (CDD/EDD) reports. Use this skill when users need to prepare
  regulatory filings or compliance documentation.
---

# Regulatory Reporting Skill

You are a compliance reporting specialist. Generate formal regulatory reports following these templates:

## STR — Suspicious Transaction Report
Required under PMLA 2002 Section 12. Must be filed with FIU-IND within 7 days.
Structure:
1. **Subject Information**: Full name, customer type, KYC tier, PEP status, jurisdiction
2. **Suspicious Activity**: Transaction details, patterns identified, risk scores
3. **Alert History**: All related alerts with severity and evidence summaries
4. **Regulatory Basis**: Cite applicable PMLA sections and FATF recommendations
5. **Declaration**: Filing deadline, tipping-off prohibition (PMLA Section 66)

## CTR — Cash Transaction Report
Required for cash transactions exceeding INR 10,00,000.
Structure:
1. **Accounts Exceeding Threshold**: Customer, account, cash txn count, total amount
2. **Pattern Observations**: Frequency, amounts, time periods
3. **Regulatory Basis**: RBI cash reporting requirements

## LCR — Liquidity Coverage Ratio
Basel III compliance assessment.
Structure:
1. **Key Metrics**: Approximate LCR, HQLA, 30-day net outflows
2. **Stressed Accounts**: Accounts with HIGH/CRITICAL liquidity stress
3. **Compliance Status**: Above or below 100% minimum

## CDD/EDD — Customer Due Diligence
Enhanced review for high-risk and PEP customers.
Structure:
1. **High-Risk Population**: Count, PEP status, jurisdictions
2. **Sanctions & Adverse Media**: Flags requiring immediate review
3. **Overdue KYC**: Reviews past due > 1 year
4. **Recommendations**: Priority review order, escalation path

Always use data from the semantic view and format amounts in INR with proper notation.
$$
)
FILE_FORMAT = (TYPE = CSV COMPRESSION = NONE RECORD_DELIMITER = NONE FIELD_DELIMITER = NONE)
OVERWRITE = TRUE
SINGLE = TRUE;

-- Skill 3: Risk Dashboard Analytics
COPY INTO @RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/risk_analytics/SKILL.md
FROM (
    SELECT $$---
name: risk_analytics
description: >
  Provides executive-level risk analytics including portfolio health scoring,
  trend analysis, peer comparisons, and risk concentration analysis.
  Use this skill when users ask for dashboards, summaries, executive briefs,
  or portfolio-level risk assessments.
---

# Risk Analytics Skill

You are a Chief Risk Officer's analytical assistant. Provide data-driven risk intelligence:

## Portfolio Health Score
Calculate an overall portfolio health score (0-100) based on:
- AML risk concentration: % of customers rated HIGH/VERY_HIGH
- NPA exposure: NPA balance as % of total AUM
- Alert density: Open critical alerts per 100 customers
- Liquidity stress: % of accounts under HIGH/CRITICAL stress
- Cross-border risk: % of transaction volume to high-risk jurisdictions

## Trend Analysis
When asked about trends:
- Query daily transaction volumes and identify spikes
- Track alert creation rate over time
- Monitor risk score distribution changes
- Identify emerging patterns (new jurisdictions, new transaction types)

## Risk Concentration
Identify concentration risks:
- Top 3 customers by transaction volume (concentration risk)
- Geographic concentration in high-risk jurisdictions
- Sector concentration by customer type (CORPORATE vs INDIVIDUAL vs HNI)

## Executive Brief Format
Always structure executive outputs as:
1. **Risk Posture**: One-line assessment with severity level
2. **Key Metrics**: 4-6 bullet points with specific numbers
3. **Concerns**: Top 3 issues requiring attention
4. **Actions**: Concrete next steps with ownership
$$
)
FILE_FORMAT = (TYPE = CSV COMPRESSION = NONE RECORD_DELIMITER = NONE FIELD_DELIMITER = NONE)
OVERWRITE = TRUE
SINGLE = TRUE;

-- 3. Verify skills are uploaded
LS @RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/ PATTERN='.*SKILL\.md';

-- 4. Create the Cortex Agent
CREATE OR REPLACE AGENT RISK_COPILOT_DB.RISK_COPILOT.RISK_COPILOT_AGENT
FROM SPECIFICATION $$
{
    "models": {
        "orchestration": "auto"
    },
    "instructions": {
        "orchestration": "You are CoCoIceberg, a risk and compliance AI agent for banking. Route data questions to Cortex Analyst, regulatory policy questions to Cortex Search, and use skills for investigation workflows and report generation.",
        "response": "Provide concise, evidence-based risk assessments. Always cite specific data: customer IDs, transaction IDs, amounts, dates, and risk scores. Format currency in INR. Use bullet points for clarity."
    },
    "tools": [
        {
            "tool_spec": {
                "type": "cortex_analyst_text_to_sql",
                "name": "RiskAnalyst",
                "description": "Answers questions about customers, accounts, transactions, and alerts using the risk copilot semantic view. Use for any data query about AML scores, transaction volumes, customer profiles, NPA status, etc."
            }
        },
        {
            "tool_spec": {
                "type": "cortex_search",
                "name": "PolicySearch",
                "description": "Searches regulatory policy documents including PMLA, RBI guidelines, FATF recommendations, and Basel III frameworks. Use when the user asks about regulations, compliance requirements, or filing obligations."
            }
        },
        {
            "tool_spec": {
                "type": "data_to_chart",
                "name": "ChartGenerator",
                "description": "Generates charts and visualizations from data results."
            }
        }
    ],
    "tool_resources": {
        "RiskAnalyst": {
            "semantic_view": "RISK_COPILOT_DB.RISK_COPILOT.SV_RISK_COPILOT",
            "execution_environment": {
                "type": "warehouse",
                "warehouse": "COMPUTE_WH"
            }
        },
        "PolicySearch": {
            "search_service": "RISK_COPILOT_DB.RISK_COPILOT.POLICY_SEARCH_SERVICE"
        }
    },
    "skills": [
        {
            "name": "aml_investigation",
            "source": {
                "type": "STAGE",
                "path": "@RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/aml_investigation"
            }
        },
        {
            "name": "regulatory_reporting",
            "source": {
                "type": "STAGE",
                "path": "@RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/regulatory_reporting"
            }
        },
        {
            "name": "risk_analytics",
            "source": {
                "type": "STAGE",
                "path": "@RISK_COPILOT_DB.RISK_COPILOT.SKILL_STAGE/skills/risk_analytics"
            }
        }
    ]
}
$$;

-- 5. Verify the agent was created
DESCRIBE AGENT RISK_COPILOT_DB.RISK_COPILOT.RISK_COPILOT_AGENT;

-- 6. Grant usage so the Streamlit app can invoke it
GRANT USAGE ON AGENT RISK_COPILOT_DB.RISK_COPILOT.RISK_COPILOT_AGENT TO ROLE ACCOUNTADMIN;
