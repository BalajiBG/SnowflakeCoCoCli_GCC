import streamlit as st
import time
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Liquidity Risk", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="Liquidity risk view with outflow-to-balance ratios" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>V_LIQUIDITY_RISK</strong> <span style="color:#6b7280;">— Stress level indicators</span>
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
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">💧 Liquidity <span style="color:#29B5E8;">Risk</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Liquidity stress indicators — outflow ratios, balance deterioration, and stress levels.</p>
""", unsafe_allow_html=True)

# --- Fetch Data ---
liq_df = session.sql(f"""
    SELECT FULL_NAME, CUSTOMER_TYPE, ACCOUNT_ID, TXN_DAY, 
           DAILY_OUTFLOWS, OUTFLOW_TO_BALANCE_PCT AS OUTFLOW_PCT, 
           LIQUIDITY_STRESS_LEVEL AS STRESS_LEVEL, STRESS_NARRATIVE
    FROM {DB}.{SCHEMA}.V_LIQUIDITY_RISK
    WHERE LIQUIDITY_STRESS_LEVEL IN ('HIGH','CRITICAL')
    ORDER BY OUTFLOW_TO_BALANCE_PCT DESC
""").to_pandas()

# --- AI Liquidity Intelligence (TOP) ---
st.markdown('<div class="section-header">AI Liquidity Intelligence</div>', unsafe_allow_html=True)

if not liq_df.empty:
    with st.status("AI Liquidity Intelligence — Processing...", expanded=True) as status:
        st.markdown('<span class="pipeline-step step-active">1. Scanning stressed accounts</span>', unsafe_allow_html=True)
        time.sleep(0.5)
        total_stressed = len(liq_df)
        critical_stressed = len(liq_df[liq_df["STRESS_LEVEL"] == "CRITICAL"]) if "STRESS_LEVEL" in liq_df.columns else 0
        max_outflow = liq_df["OUTFLOW_PCT"].max() if "OUTFLOW_PCT" in liq_df.columns else 0
        st.markdown(f'<span class="pipeline-step step-done">✓ {total_stressed} stressed accounts — {critical_stressed} CRITICAL, max outflow {max_outflow:.1f}%</span>', unsafe_allow_html=True)

        st.markdown('<span class="pipeline-step step-active">2. Preparing liquidity profiles</span>', unsafe_allow_html=True)
        time.sleep(0.5)
        liq_rows = []
        for _, r in liq_df.head(5).iterrows():
            liq_rows.append(f"{r['FULL_NAME']}: Outflow={r['OUTFLOW_PCT']:.1f}%, Level={r['STRESS_LEVEL']}, Type={r['CUSTOMER_TYPE']}")
        data_lines = "\n".join(liq_rows) if liq_rows else "No data"
        st.markdown(f'<span class="pipeline-step step-done">✓ Top {len(liq_rows)} stress profiles prepared</span>', unsafe_allow_html=True)

        st.markdown('<span class="pipeline-step step-active">3. Cortex LLM — Generating liquidity assessment</span>', unsafe_allow_html=True)

        liq_prompt = f"""Analyze this liquidity stress data. Be extremely concise. Bullet points only.

Summary: {total_stressed} stressed accounts, {critical_stressed} CRITICAL, max outflow={max_outflow:.1f}%
Top accounts:
{data_lines}

Reply in EXACTLY this format (one short line per bullet, no extra text):

STATUS: [CRITICAL/HIGH/MEDIUM/STABLE] - [5 word reason]

AT_RISK:
- [Name]: [outflow %, 6 words why dangerous]
- [Name]: [outflow %, 6 words why dangerous]
- [Name]: [outflow %, 6 words why dangerous]

ACTIONS:
- TREASURY: [immediate funding action]
- CUSTOMER: [who to contact, what to offer]
- REGULATORY: [LCR/NSFR impact, reporting needed]"""

        ai_response = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{liq_prompt.replace("'", "''")}') AS INSIGHT
        """).collect()[0]["INSIGHT"]

        st.markdown('<span class="pipeline-step step-done">✓ AI assessment complete</span>', unsafe_allow_html=True)
        status.update(label="AI Liquidity Intelligence — Complete", state="complete", expanded=False)

    lines = ai_response.strip().split('\n')
    status_line = ""
    risk_lines = []
    actions_lines = []
    current_section = ""
    for line in lines:
        line = line.strip().lstrip('*').lstrip('-').strip()
        if not line:
            continue
        if "STATUS:" in line:
            status_line = line.split("STATUS:")[-1].strip()
            current_section = ""
        elif "AT_RISK:" in line:
            current_section = "risk"
        elif "ACTIONS:" in line:
            current_section = "actions"
        elif current_section == "risk" and line:
            risk_lines.append(line.lstrip('- ').lstrip('* '))
        elif current_section == "actions" and line:
            actions_lines.append(line.lstrip('- ').lstrip('* '))

    status_color = "#dc2626" if "CRITICAL" in status_line.upper() else "#f59e0b" if "HIGH" in status_line.upper() else "#10b981"
    risk_html = "".join(f"<li>{r}</li>" for r in risk_lines[:3]) if risk_lines else "<li>No critical stress</li>"
    actions_html = "".join(f"<li>{a}</li>" for a in actions_lines[:3]) if actions_lines else "<li>Continue monitoring</li>"

    st.markdown(f"""
    <div class="ai-grid">
        <div class="ai-card" style="background:{status_color}15; border:1px solid {status_color}40;">
            <div class="ai-card-label" style="color:{status_color};">Liquidity Status</div>
            <div class="ai-card-content" style="color:#1a1a2e; font-weight:600;">{status_line}</div>
        </div>
        <div class="ai-card" style="background:#f59e0b15; border:1px solid #f59e0b40;">
            <div class="ai-card-label" style="color:#d97706;">Highest Risk</div>
            <div class="ai-card-content"><ul>{risk_html}</ul></div>
        </div>
        <div class="ai-card" style="background:#10b98115; border:1px solid #10b98140; grid-column: 1 / -1;">
            <div class="ai-card-label" style="color:#059669;">Recommended Actions</div>
            <div class="ai-card-content"><ul>{actions_html}</ul></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:#ecfdf5; border:1px solid #6ee7b7; border-radius:10px; padding:14px 16px;">
        <span style="font-size:0.7rem; font-weight:700; color:#059669; letter-spacing:1px; text-transform:uppercase;">STATUS</span>
        <div style="font-size:0.85rem; color:#064e3b; margin-top:4px; font-weight:600;">STABLE — No critical liquidity stress detected</div>
    </div>
    """, unsafe_allow_html=True)

# --- Data Table (BELOW) ---
st.markdown('<div class="section-header">Liquidity Stress Indicators</div>', unsafe_allow_html=True)
if not liq_df.empty:
    st.dataframe(liq_df, use_container_width=True, hide_index=True,
                 column_config={"OUTFLOW_PCT": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%")})
else:
    st.success("No critical liquidity stress detected.")
