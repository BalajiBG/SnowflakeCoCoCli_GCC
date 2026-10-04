import streamlit as st
import time
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Credit Risk", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="Pre-computed credit risk view with NPA detection" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>V_CREDIT_RISK</strong> <span style="color:#6b7280;">— Credit scoring & NPA detection</span>
        </div>
        <div title="Dynamic Tables with 1-min target lag" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            ⚡ <strong>Dynamic Tables</strong> <span style="color:#6b7280;">— Real-time risk signals</span>
        </div>
        <div title="Streamlit-in-Snowflake for secure, governed app hosting" style="cursor:help; padding:3px 0;">
            📱 <strong>Streamlit in Snowflake</strong> <span style="color:#6b7280;">— Secure app hosting</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0rem; }
    [data-testid="stSidebarNav"] { padding-top: 0rem; }
    h1, h2, h3 { color: #1a1a2e; }
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
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">💳 Credit <span style="color:#29B5E8;">Risk</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Credit risk monitoring — consecutive bounces, NPA status, and risk narratives.</p>
""", unsafe_allow_html=True)

# --- Fetch Data ---
credit_df = session.sql(f"""
    SELECT FULL_NAME, ACCOUNT_ID, CREDIT_RISK_LEVEL AS RISK_LEVEL, 
           CONSECUTIVE_BOUNCES AS BOUNCES, NPA_STATUS, RISK_NARRATIVE
    FROM {DB}.{SCHEMA}.V_CREDIT_RISK
    ORDER BY CASE CREDIT_RISK_LEVEL WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END
""").to_pandas()

# --- AI Credit Risk Intelligence (TOP) ---
st.markdown('<div class="section-header">AI Credit Risk Intelligence</div>', unsafe_allow_html=True)

with st.status("AI Credit Risk Intelligence — Processing...", expanded=True) as status:
    st.markdown('<span class="pipeline-step step-active">1. Loading credit portfolio</span>', unsafe_allow_html=True)
    time.sleep(0.5)
    total_accounts = len(credit_df)
    critical_count = len(credit_df[credit_df["RISK_LEVEL"] == "CRITICAL"]) if not credit_df.empty else 0
    high_count = len(credit_df[credit_df["RISK_LEVEL"] == "HIGH"]) if not credit_df.empty else 0
    npa_count = len(credit_df[credit_df["NPA_STATUS"] == "NPA"]) if not credit_df.empty and "NPA_STATUS" in credit_df.columns else 0
    st.markdown(f'<span class="pipeline-step step-done">✓ {total_accounts} accounts — {critical_count} CRITICAL, {high_count} HIGH, {npa_count} NPA</span>', unsafe_allow_html=True)

    st.markdown('<span class="pipeline-step step-active">2. Preparing risk profiles</span>', unsafe_allow_html=True)
    time.sleep(0.5)
    top_rows = []
    for _, r in credit_df.head(5).iterrows():
        top_rows.append(f"{r['FULL_NAME']}: Risk={r['RISK_LEVEL']}, Bounces={r['BOUNCES']}, NPA={r['NPA_STATUS']}")
    data_lines = "\n".join(top_rows) if top_rows else "No data"
    st.markdown(f'<span class="pipeline-step step-done">✓ Top {len(top_rows)} risk profiles prepared</span>', unsafe_allow_html=True)

    st.markdown('<span class="pipeline-step step-active">3. Cortex LLM — Generating credit assessment</span>', unsafe_allow_html=True)

    credit_prompt = f"""Analyze this credit risk portfolio. Be extremely concise. Bullet points only.

Portfolio: {total_accounts} accounts, {critical_count} CRITICAL, {high_count} HIGH, {npa_count} NPA
Top accounts:
{data_lines}

Reply in EXACTLY this format (one short line per bullet, no extra text):

HEALTH: [CRITICAL/HIGH/MEDIUM/LOW] - [5 word reason]

AT_RISK:
- [Name]: [bounces, NPA status, 6 words why urgent]
- [Name]: [bounces, NPA status, 6 words why urgent]
- [Name]: [bounces, NPA status, 6 words why urgent]

ACTIONS:
- COLLECT: [which account to call first]
- MITIGATE: [limit cut or restructure needed]
- REPORT: [RBI/provisioning action needed]"""

    ai_response = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{credit_prompt.replace("'", "''")}') AS INSIGHT
    """).collect()[0]["INSIGHT"]

    st.markdown('<span class="pipeline-step step-done">✓ AI assessment complete</span>', unsafe_allow_html=True)
    status.update(label="AI Credit Risk Intelligence — Complete", state="complete", expanded=False)

lines = ai_response.strip().split('\n')
health_line = ""
risk_lines = []
actions_lines = []
current_section = ""
for line in lines:
    line = line.strip().lstrip('*').lstrip('-').strip()
    if not line:
        continue
    if "HEALTH:" in line:
        health_line = line.split("HEALTH:")[-1].strip()
        current_section = ""
    elif "AT_RISK:" in line:
        current_section = "risk"
    elif "ACTIONS:" in line:
        current_section = "actions"
    elif current_section == "risk" and line:
        risk_lines.append(line.lstrip('- ').lstrip('* '))
    elif current_section == "actions" and line:
        actions_lines.append(line.lstrip('- ').lstrip('* '))

health_color = "#dc2626" if "CRITICAL" in health_line.upper() else "#f59e0b" if "HIGH" in health_line.upper() else "#10b981"
risk_html = "".join(f"<li>{r}</li>" for r in risk_lines[:3]) if risk_lines else "<li>No critical accounts</li>"
actions_html = "".join(f"<li>{a}</li>" for a in actions_lines[:3]) if actions_lines else "<li>Continue monitoring</li>"

st.markdown(f"""
<div class="ai-grid">
    <div class="ai-card" style="background:{health_color}15; border:1px solid {health_color}40;">
        <div class="ai-card-label" style="color:{health_color};">Portfolio Health</div>
        <div class="ai-card-content" style="color:#1a1a2e; font-weight:600;">{health_line}</div>
    </div>
    <div class="ai-card" style="background:#f59e0b15; border:1px solid #f59e0b40;">
        <div class="ai-card-label" style="color:#d97706;">Critical Accounts</div>
        <div class="ai-card-content"><ul>{risk_html}</ul></div>
    </div>
    <div class="ai-card" style="background:#29B5E815; border:1px solid #29B5E840; grid-column: 1 / -1;">
        <div class="ai-card-label" style="color:#0c7cd5;">Recommended Actions</div>
        <div class="ai-card-content"><ul>{actions_html}</ul></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Data Table (BELOW) ---
st.markdown('<div class="section-header">Credit Risk Monitor</div>', unsafe_allow_html=True)
st.dataframe(credit_df, use_container_width=True, hide_index=True)
