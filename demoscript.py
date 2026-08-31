# CoCoIceberg — 3-Minute Demo Script
# Total Time: ~3 minutes
# Pace: Conversational, confident. Read one section per page as you navigate.

# ============================================================================
# OPENING (15 seconds)
# ============================================================================
# [Show: Streamlit app landing page — Ask CoCo]

"""
Hi, this is CoCoIceberg — an AI-powered Risk and Compliance Copilot 
built entirely on Snowflake. It brings together Cortex AI, Dynamic Tables, 
Semantic Views, and MCP integrations to help compliance teams detect fraud, 
investigate alerts, and generate regulatory filings — all through natural language. 
Let me walk you through it.
"""

# ============================================================================
# PAGE 1: ASK COCO (30 seconds)
# ============================================================================
# [Show: Type a question like "Which customers have the highest AML risk?"]

"""
This is Ask CoCo — the AI copilot at the heart of the system.

WHAT: A natural language interface where compliance officers can ask any question 
about fraud, risk, or regulations — and get grounded, evidence-backed answers.

WHY: Compliance teams spend hours writing SQL and digging through policies. 
This gives them instant answers with citations they can trust.

HOW: Under the hood, it runs a five-step AI pipeline. First, AI_CLASSIFY routes 
the intent. Then Cortex Analyst converts the question to SQL using our Semantic View. 
Cortex Search retrieves relevant regulatory policies. A confidence assessor scores 
the evidence. And finally, Cortex Complete synthesizes the answer with guardrails. 
You can see the confidence badge here — HIGH means multiple data sources confirmed it.
"""

# ============================================================================
# PAGE 2: AML FRAUD (25 seconds)
# ============================================================================
# [Show: AML Fraud dashboard — watch pipeline steps animate, then colored cards]

"""
Next, AML Fraud.

WHAT: The moment this page loads, you see the AI Risk Intelligence pipeline in action — 
step by step. First it loads AML risk profiles, then scans fraud signals, 
and then Cortex LLM generates a live threat assessment.

WHY: A traditional dashboard just shows data. This one tells you what the data means. 
It names the specific customers who are dangerous, tells you why, 
and gives you three concrete actions — freeze this account, investigate that, 
file a SAR for this customer. That's the difference between a BI tool and an AI copilot.

HOW: Powered by Dynamic Tables that continuously recompute risk scores, 
and Cortex Complete that analyzes the live data and generates actionable intelligence 
in colored insight cards — Risk Posture, Top Threats, and Recommended Actions.
"""

# ============================================================================
# PAGE 3: CREDIT RISK (20 seconds)
# ============================================================================
# [Show: Credit Risk dashboard — pipeline steps, then insight cards]

"""
Credit Risk.

WHAT: Same AI Intelligence pattern. The pipeline loads the portfolio, 
prepares risk profiles, and Cortex LLM assesses portfolio health.

WHY: A compliance officer doesn't just want to see a table of accounts. 
They want to know — which account do I call first? Should I cut limits? 
Do I need to report to the credit committee? The AI answers all three.

HOW: V_CREDIT_RISK Dynamic Table feeds into Cortex Complete. 
The colored cards show Portfolio Health status, Critical Accounts by name, 
and specific collection and mitigation actions.
"""

# ============================================================================
# PAGE 4: LIQUIDITY RISK (20 seconds)
# ============================================================================
# [Show: Liquidity Risk dashboard — pipeline steps, then insight cards]

"""
Liquidity Risk.

WHAT: AI Liquidity Intelligence — same live pipeline pattern. 
Scans stressed accounts, prepares profiles, generates assessment.

WHY: Treasury teams need to know immediately if outflows are concentrating, 
which accounts are draining fastest, and whether LCR thresholds are at risk. 
The AI surfaces this without them having to analyze spreadsheets.

HOW: V_LIQUIDITY_RISK Dynamic Table computes outflow-to-balance ratios. 
Cortex Complete identifies the highest-risk accounts and recommends 
treasury actions, customer interventions, and regulatory reporting needs.
"""

# ============================================================================
# PAGE 5: VELOCITY ANOMALIES (20 seconds)
# ============================================================================
# [Show: Velocity Anomalies page — pipeline steps, then insight cards]

"""
Velocity Anomalies.

WHAT: AI Velocity Intelligence — detects unusual transaction velocity patterns 
and immediately classifies the threat type.

WHY: Fraudsters move fast. The AI doesn't just show you the anomalies — 
it tells you whether this looks like structuring, layering, or mule behavior. 
It names the suspects, says which accounts to freeze, 
and whether to file a Suspicious Transaction Report.

HOW: The DT_TXN_VELOCITY_MONITOR Dynamic Table tracks rolling velocity windows. 
Cortex Complete matches patterns against known fraud typologies 
and generates the threat assessment with specific recommended actions.
"""

# ============================================================================
# PAGE 6: INVESTIGATION (30 seconds)
# ============================================================================
# [Show: Select an alert, generate investigation report, click Create Jira Ticket]

"""
Now the Investigation Workspace — this is where it gets powerful.

WHAT: A deep-dive workspace where you select an alert, review the customer profile, 
see their AML score, and generate a full AI investigation report.

WHY: Writing investigation reports takes compliance officers hours. 
This produces a structured, citation-heavy report in seconds — 
with subject background, timeline, key findings, typology match, and recommendation.

HOW: Cortex Complete generates the report using evidence from cross-table SQL joins — 
customers, accounts, transactions, and alerts all stitched together. 
The AML composite score comes from our Dynamic Table. 
And here's the MCP integration — when I click Create Jira Ticket, 
it writes to our compliance table and syncs directly to Jira via the MCP connector. 
That's a real ticket in our Jira board right now.
"""

# ============================================================================
# PAGE 7: REPORT GENERATOR (30 seconds)
# ============================================================================
# [Show: Select CTR from dropdown, click Generate, watch pipeline, download PDF]

"""
Finally, the Report Generator.

WHAT: Produces formal regulatory filings — Suspicious Transaction Reports, 
Cash Transaction Reports, Basel III LCR reports, and Customer Due Diligence reviews. 
Every report type now has a Generate button — not just STR.

WHY: These filings have strict formatting requirements and must cite specific 
transactions, dates, and amounts. Manual preparation is error-prone and slow.

HOW: Watch what happens when I click Generate CTR Report. 
You see the same pipeline pattern — compiling data, generating the AI narrative 
through Cortex Complete, and building the PDF. The narrative is written in 
regulatory language with specific account names, amounts, and pattern observations.
And here's the download — a professional PDF with CONFIDENTIAL header, 
data tables, AI-generated analysis, and a SHA-256 integrity hash 
for audit trail verification. Every report type works the same way.
"""

# ============================================================================
# CLOSING — CoCo INGENUITY (15 seconds)
# ============================================================================
# [Show: Sidebar with "Powered By" section visible]

"""
And beyond the app itself — every dashboard page has AI Intelligence built in, 
not just showing data but telling you what it means and what to do about it. 
We've published this as a reusable CoCo skill that other teams can install. 
We have a daily cron automation that monitors risk thresholds. 
Three custom stored procedures the agent can call for real actions. 
And guardrails throughout — input validation, confidence scoring, 
and graceful fallbacks when evidence is thin.

That's CoCoIceberg — compliance intelligence, powered entirely by Snowflake. 
Thank you.
"""

# ============================================================================
# TOTAL: ~3 minutes
# ============================================================================
