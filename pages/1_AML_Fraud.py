import streamlit as st
import time
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | AML & Fraud", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="Dynamic Tables with 1-min target lag for real-time risk computation" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            ⚡ <strong>Dynamic Tables</strong> <span style="color:#6b7280;">— Real-time risk signals (1-min lag)</span>
        </div>
        <div title="Pre-computed analytical views for fraud, credit, liquidity scoring" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>Analytical Views</strong> <span style="color:#6b7280;">— V_FRAUD_SIGNALS, V_AML_SCORING</span>
        </div>
        <div title="CoCo-generated synthetic data with realistic fraud patterns" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🧪 <strong>Synthetic Data</strong> <span style="color:#6b7280;">— CoCo-generated, privacy-safe</span>
        </div>
        <div title="Streamlit-in-Snowflake for secure, governed app hosting" style="cursor:help; padding:3px 0;">
            📱 <strong>Streamlit in Snowflake</strong> <span style="color:#6b7280;">— Secure app hosting</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp { background-color: #ffffff; font-size: 1.15rem; }
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"], p, li, td, th, label, .stSelectbox, .stTextInput { font-size: 1.1rem !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0rem; }
    [data-testid="stSidebarNav"] { padding-top: 0rem; }
    h1, h2, h3 { color: #1a1a2e; }
    .kpi-row { display: flex; gap: 16px; margin-bottom: 24px; }
    .kpi-card {
        flex: 1; background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 20px 24px; text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-card.critical { border-left: 4px solid #dc2626; }
    .kpi-card.warning { border-left: 4px solid #f59e0b; }
    .kpi-card.info { border-left: 4px solid #29B5E8; }
    .kpi-value { font-size: 2.2rem; font-weight: 700; color: #1a1a2e; margin: 0; }
    .kpi-label { font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a1a2e;
        padding: 12px 0 8px; border-bottom: 2px solid #29B5E8; margin-bottom: 16px;
    }
    .ai-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
    .ai-card { border-radius: 10px; padding: 14px 16px; }
    .ai-card-label { font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
    .ai-card-content { font-size: 0.82rem; line-height: 1.5; }
    .ai-card-content ul { margin: 0; padding-left: 16px; }
    .ai-card-content li { margin-bottom: 3px; }
    .pipeline-step {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 500; margin-right: 8px;
    }
    .step-active { background: #e8f4fd; color: #0c7cd5; border: 1px solid #29B5E8; }
    .step-done { background: #ecfdf5; color: #059669; border: 1px solid #6ee7b7; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">🚨 AML & <span style="color:#29B5E8;">Fraud</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Anti-money laundering risk scores, fraud signals, and active alerts.</p>
""", unsafe_allow_html=True)

# --- KPIs ---
kpis = session.sql(f"""
    SELECT 
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ALERTS WHERE STATUS IN ('OPEN','UNDER_REVIEW','ESCALATED')) AS open_alerts,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ALERTS WHERE SEVERITY = 'CRITICAL' AND STATUS != 'CLOSED') AS critical_alerts,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.V_AML_SCORING WHERE COMPOSITE_AML_SCORE > 70) AS high_risk_customers,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.V_CREDIT_RISK WHERE CREDIT_RISK_LEVEL IN ('HIGH','CRITICAL')) AS credit_risk_accounts,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.V_LIQUIDITY_RISK WHERE LIQUIDITY_STRESS_LEVEL IN ('HIGH','CRITICAL')) AS liquidity_stressed
""").collect()[0]

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card info"><div class="kpi-value">{kpis["OPEN_ALERTS"]}</div><div class="kpi-label">Open Alerts</div></div>
    <div class="kpi-card critical"><div class="kpi-value">{kpis["CRITICAL_ALERTS"]}</div><div class="kpi-label">Critical Alerts</div></div>
    <div class="kpi-card warning"><div class="kpi-value">{kpis["HIGH_RISK_CUSTOMERS"]}</div><div class="kpi-label">High-Risk Customers</div></div>
    <div class="kpi-card warning"><div class="kpi-value">{kpis["CREDIT_RISK_ACCOUNTS"]}</div><div class="kpi-label">Credit at Risk</div></div>
    <div class="kpi-card critical"><div class="kpi-value">{kpis["LIQUIDITY_STRESSED"]}</div><div class="kpi-label">Liquidity Stress</div></div>
</div>
""", unsafe_allow_html=True)

# --- Fetch data ---
aml_df = session.sql(f"""
    SELECT FULL_NAME, CUSTOMER_TYPE, KYC_RISK_TIER AS RISK_TIER, 
           COMPOSITE_AML_SCORE AS AML_SCORE, CRITICAL_ALERTS, RECOMMENDED_ACTION
    FROM {DB}.{SCHEMA}.V_AML_SCORING
    ORDER BY COMPOSITE_AML_SCORE DESC
    LIMIT 10
""").to_pandas()

fraud_df = session.sql(f"""
    SELECT FULL_NAME, SIGNAL_TYPE, TOTAL_AMOUNT, NUM_DEPOSITS AS COUNT, DESCRIPTION
    FROM {DB}.{SCHEMA}.V_FRAUD_SIGNALS
    ORDER BY TOTAL_AMOUNT DESC
""").to_pandas()

alerts_df = session.sql(f"""
    SELECT ALERT_CATEGORY AS CATEGORY, SEVERITY, ALERT_TYPE, CUSTOMER_ID, DESCRIPTION, STATUS
    FROM {DB}.{SCHEMA}.ALERTS
    WHERE STATUS IN ('OPEN','UNDER_REVIEW','ESCALATED')
    ORDER BY CASE SEVERITY WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END
""").to_pandas()

# --- AI Risk Intelligence (TOP) ---
st.markdown('<div class="section-header">AI Risk Intelligence</div>', unsafe_allow_html=True)

with st.status("AI Risk Intelligence — Processing...", expanded=True) as status:
    st.markdown('<span class="pipeline-step step-active">1. Fetching AML risk scores</span>', unsafe_allow_html=True)
    time.sleep(0.5)
    aml_rows = []
    for _, r in aml_df.head(5).iterrows():
        aml_rows.append(f"{r['FULL_NAME']}: AML_Score={r['AML_SCORE']}, Type={r['CUSTOMER_TYPE']}, Tier={r['RISK_TIER']}")
    st.markdown(f'<span class="pipeline-step step-done">✓ {len(aml_df)} AML risk profiles loaded</span>', unsafe_allow_html=True)

    st.markdown('<span class="pipeline-step step-active">2. Scanning fraud signals</span>', unsafe_allow_html=True)
    time.sleep(0.5)
    fraud_rows = []
    for _, r in fraud_df.head(5).iterrows():
        fraud_rows.append(f"{r['FULL_NAME']}: {r['SIGNAL_TYPE']}, Amount={r['TOTAL_AMOUNT']}")
    st.markdown(f'<span class="pipeline-step step-done">✓ {len(fraud_df)} fraud signals detected</span>', unsafe_allow_html=True)

    aml_lines = "\n".join(aml_rows) if aml_rows else "No data"
    fraud_lines = "\n".join(fraud_rows) if fraud_rows else "No data"

    st.markdown('<span class="pipeline-step step-active">3. Cortex LLM — Generating risk assessment</span>', unsafe_allow_html=True)

    insight_prompt = f"""Analyze this AML/Fraud data. Be extremely concise. Bullet points only.

KPIs: Open Alerts={kpis["OPEN_ALERTS"]}, Critical={kpis["CRITICAL_ALERTS"]}, High-Risk Customers={kpis["HIGH_RISK_CUSTOMERS"]}
Top AML risks:
{aml_lines}
Fraud signals:
{fraud_lines}

Reply in EXACTLY this format (one short line per bullet, no extra text):

RISK_LEVEL: [CRITICAL/HIGH/MEDIUM/LOW] - [5 word reason]

THREATS:
- [Name]: [8 words max why dangerous]
- [Name]: [8 words max why dangerous]
- [Name]: [8 words max why dangerous]

ACTIONS:
- FREEZE: [account/customer to block now]
- INVESTIGATE: [what to check]
- REPORT: [SAR/STR filing needed for whom]"""

    ai_response = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{insight_prompt.replace("'", "''")}') AS INSIGHT
    """).collect()[0]["INSIGHT"]

    st.markdown('<span class="pipeline-step step-done">✓ AI assessment complete</span>', unsafe_allow_html=True)
    status.update(label="AI Risk Intelligence — Complete", state="complete", expanded=False)

lines = ai_response.strip().split('\n')
risk_level_line = ""
threats_lines = []
actions_lines = []
current_section = ""
for line in lines:
    line = line.strip().lstrip('*').lstrip('-').strip()
    if not line:
        continue
    if "RISK_LEVEL:" in line:
        risk_level_line = line.split("RISK_LEVEL:")[-1].strip()
        current_section = ""
    elif "THREATS:" in line:
        current_section = "threats"
    elif "ACTIONS:" in line:
        current_section = "actions"
    elif current_section == "threats" and line:
        threats_lines.append(line.lstrip('- ').lstrip('* '))
    elif current_section == "actions" and line:
        actions_lines.append(line.lstrip('- ').lstrip('* '))

risk_color = "#dc2626" if "CRITICAL" in risk_level_line.upper() else "#f59e0b" if "HIGH" in risk_level_line.upper() else "#29B5E8"
threats_html = "".join(f"<li>{t}</li>" for t in threats_lines[:3]) if threats_lines else "<li>No immediate threats</li>"
actions_html = "".join(f"<li>{a}</li>" for a in actions_lines[:3]) if actions_lines else "<li>Continue monitoring</li>"

st.markdown(f"""
<div class="ai-grid">
    <div class="ai-card" style="background:{risk_color}15; border:1px solid {risk_color}40;">
        <div class="ai-card-label" style="color:{risk_color};">Risk Posture</div>
        <div class="ai-card-content" style="color:#1a1a2e; font-weight:600;">{risk_level_line}</div>
    </div>
    <div class="ai-card" style="background:#dc262615; border:1px solid #dc262640;">
        <div class="ai-card-label" style="color:#dc2626;">Top Threats</div>
        <div class="ai-card-content"><ul>{threats_html}</ul></div>
    </div>
    <div class="ai-card" style="background:#29B5E815; border:1px solid #29B5E840; grid-column: 1 / -1;">
        <div class="ai-card-label" style="color:#0c7cd5;">Recommended Actions</div>
        <div class="ai-card-content"><ul>{actions_html}</ul></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Data Tables (BELOW) ---
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="section-header">Top AML Risk Scores</div>', unsafe_allow_html=True)
    st.dataframe(aml_df, use_container_width=True, hide_index=True,
                 column_config={"AML_SCORE": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d")})

with col2:
    st.markdown('<div class="section-header">Active Fraud Signals</div>', unsafe_allow_html=True)
    st.dataframe(fraud_df, use_container_width=True, hide_index=True,
                 column_config={"TOTAL_AMOUNT": st.column_config.NumberColumn(format="₹%d")})

st.markdown('<div class="section-header">Alerts by Category & Severity</div>', unsafe_allow_html=True)
st.dataframe(alerts_df, use_container_width=True, hide_index=True)
