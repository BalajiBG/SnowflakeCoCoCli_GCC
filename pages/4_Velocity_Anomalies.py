import streamlit as st
import time
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Velocity Anomalies", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="Dynamic Table monitoring transaction velocity per hour" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            ⚡ <strong>DT_TXN_VELOCITY_MONITOR</strong> <span style="color:#6b7280;">— Real-time velocity</span>
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
    .stApp { background-color: #ffffff; font-size: 1.15rem; }
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"], p, li, td, th, label, .stSelectbox, .stTextInput { font-size: 1.1rem !important; }
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
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">⚡ Velocity <span style="color:#29B5E8;">Anomalies</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Transaction velocity monitoring — unusual hourly patterns, multi-country involvement, and burst detection.</p>
""", unsafe_allow_html=True)

# --- Fetch Data ---
velocity_df = session.sql(f"""
    SELECT FULL_NAME, ACCOUNT_ID, HOUR_BUCKET, TXN_COUNT_PER_HOUR AS TXN_COUNT, 
           VOLUME_PER_HOUR AS VOLUME, COUNTRIES_INVOLVED, VELOCITY_FLAG AS FLAG
    FROM {DB}.{SCHEMA}.DT_TXN_VELOCITY_MONITOR
    WHERE VELOCITY_FLAG != 'NORMAL'
    ORDER BY VOLUME_PER_HOUR DESC
    LIMIT 15
""").to_pandas()

# --- AI Velocity Intelligence (TOP) ---
st.markdown('<div class="section-header">AI Velocity Intelligence</div>', unsafe_allow_html=True)

if not velocity_df.empty:
    with st.status("AI Velocity Intelligence — Processing...", expanded=True) as status:
        st.markdown('<span class="pipeline-step step-active">1. Scanning velocity anomalies</span>', unsafe_allow_html=True)
        time.sleep(0.5)
        total_anomalies = len(velocity_df)
        unique_customers = velocity_df["FULL_NAME"].nunique() if "FULL_NAME" in velocity_df.columns else 0
        max_volume = velocity_df["VOLUME"].max() if "VOLUME" in velocity_df.columns else 0
        st.markdown(f'<span class="pipeline-step step-done">✓ {total_anomalies} anomalies — {unique_customers} customers, max volume {max_volume:,.0f}</span>', unsafe_allow_html=True)

        st.markdown('<span class="pipeline-step step-active">2. Preparing suspect profiles</span>', unsafe_allow_html=True)
        time.sleep(0.5)
        vel_rows = []
        for _, r in velocity_df.head(5).iterrows():
            vel_rows.append(f"{r['FULL_NAME']}: Volume={r['VOLUME']:,.0f}, Txns={r['TXN_COUNT']}, Countries={r['COUNTRIES_INVOLVED']}, Flag={r['FLAG']}")
        data_lines = "\n".join(vel_rows) if vel_rows else "No data"
        st.markdown(f'<span class="pipeline-step step-done">✓ Top {len(vel_rows)} suspect profiles prepared</span>', unsafe_allow_html=True)

        st.markdown('<span class="pipeline-step step-active">3. Cortex LLM — Generating threat assessment</span>', unsafe_allow_html=True)

        velocity_prompt = f"""Analyze these transaction velocity anomalies. Be extremely concise. Bullet points only.

Summary: {total_anomalies} anomalies, {unique_customers} customers, max hourly volume={max_volume:,.0f}
Top accounts:
{data_lines}

Reply in EXACTLY this format (one short line per bullet, no extra text):

THREAT: [CRITICAL/HIGH/MEDIUM/LOW] - [pattern type: structuring/layering/mule/burst]

SUSPECTS:
- [Name]: [volume, txn count, 6 words why suspicious]
- [Name]: [volume, txn count, 6 words why suspicious]
- [Name]: [volume, txn count, 6 words why suspicious]

ACTIONS:
- BLOCK: [which accounts to freeze now]
- INVESTIGATE: [what to check - IP/device/beneficiary]
- FILE: [STR/SAR needed? For whom?]"""

        ai_response = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{velocity_prompt.replace("'", "''")}') AS INSIGHT
        """).collect()[0]["INSIGHT"]

        st.markdown('<span class="pipeline-step step-done">✓ AI assessment complete</span>', unsafe_allow_html=True)
        status.update(label="AI Velocity Intelligence — Complete", state="complete", expanded=False)

    lines = ai_response.strip().split('\n')
    threat_line = ""
    suspects_lines = []
    actions_lines = []
    current_section = ""
    for line in lines:
        line = line.strip().lstrip('*').lstrip('-').strip()
        if not line:
            continue
        if "THREAT:" in line:
            threat_line = line.split("THREAT:")[-1].strip()
            current_section = ""
        elif "SUSPECTS:" in line:
            current_section = "suspects"
        elif "ACTIONS:" in line:
            current_section = "actions"
        elif current_section == "suspects" and line:
            suspects_lines.append(line.lstrip('- ').lstrip('* '))
        elif current_section == "actions" and line:
            actions_lines.append(line.lstrip('- ').lstrip('* '))

    threat_color = "#dc2626" if "CRITICAL" in threat_line.upper() else "#f59e0b" if "HIGH" in threat_line.upper() else "#29B5E8"
    suspects_html = "".join(f"<li>{s}</li>" for s in suspects_lines[:3]) if suspects_lines else "<li>No high-threat accounts</li>"
    actions_html = "".join(f"<li>{a}</li>" for a in actions_lines[:3]) if actions_lines else "<li>Continue monitoring</li>"

    st.markdown(f"""
    <div class="ai-grid">
        <div class="ai-card" style="background:{threat_color}15; border:1px solid {threat_color}40;">
            <div class="ai-card-label" style="color:{threat_color};">Threat Level</div>
            <div class="ai-card-content" style="color:#1a1a2e; font-weight:600;">{threat_line}</div>
        </div>
        <div class="ai-card" style="background:#dc262615; border:1px solid #dc262640;">
            <div class="ai-card-label" style="color:#dc2626;">Top Suspects</div>
            <div class="ai-card-content"><ul>{suspects_html}</ul></div>
        </div>
        <div class="ai-card" style="background:#1a1a2e10; border:1px solid #1a1a2e30; grid-column: 1 / -1;">
            <div class="ai-card-label" style="color:#1a1a2e;">Recommended Actions</div>
            <div class="ai-card-content"><ul>{actions_html}</ul></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:#ecfdf5; border:1px solid #6ee7b7; border-radius:10px; padding:14px 16px;">
        <span style="font-size:0.7rem; font-weight:700; color:#059669; letter-spacing:1px; text-transform:uppercase;">STATUS</span>
        <div style="font-size:0.85rem; color:#064e3b; margin-top:4px; font-weight:600;">NORMAL — No velocity anomalies detected</div>
    </div>
    """, unsafe_allow_html=True)

# --- Data Table (BELOW) ---
st.markdown('<div class="section-header">Transaction Velocity Anomalies</div>', unsafe_allow_html=True)
if not velocity_df.empty:
    st.dataframe(velocity_df, use_container_width=True, hide_index=True)
else:
    st.success("No velocity anomalies detected.")
