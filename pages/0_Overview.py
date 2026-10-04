import streamlit as st
import time
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Overview", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="Aggregated KPIs from CUSTOMERS, ACCOUNTS, TRANSACTIONS, ALERTS" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🗄️ <strong>Base Tables</strong> <span style="color:#6b7280;">— CUSTOMERS, ACCOUNTS, TRANSACTIONS, ALERTS</span>
        </div>
        <div title="Pre-computed analytical views for AML, credit, liquidity scoring" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>Analytical Views</strong> <span style="color:#6b7280;">— V_AML_SCORING, V_CREDIT_RISK, V_LIQUIDITY_RISK</span>
        </div>
        <div title="Dynamic Tables with 1-min target lag" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            ⚡ <strong>Dynamic Tables</strong> <span style="color:#6b7280;">— DT_TXN_VELOCITY_MONITOR</span>
        </div>
        <div title="Cortex LLM for AI executive summary" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🤖 <strong>Cortex Complete</strong> <span style="color:#6b7280;">— AI executive summary</span>
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
    .kpi-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px; background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 16px 20px; text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-card.critical { border-left: 4px solid #dc2626; }
    .kpi-card.warning { border-left: 4px solid #f59e0b; }
    .kpi-card.info { border-left: 4px solid #29B5E8; }
    .kpi-card.success { border-left: 4px solid #10b981; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; margin: 0; }
    .kpi-label { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
    .kpi-sub { font-size: 0.7rem; color: #9ca3af; margin-top: 2px; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a1a2e;
        padding: 12px 0 8px; border-bottom: 2px solid #29B5E8; margin-bottom: 16px;
    }
    .grounding-box {
        background: #f8fbff; border: 1px solid #e8f4fd; border-radius: 10px;
        padding: 16px 20px; margin-top: 24px;
    }
    .grounding-title { font-size: 0.75rem; font-weight: 700; color: #29B5E8; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
    .grounding-item { font-size: 0.78rem; color: #374151; padding: 3px 0; border-bottom: 1px dotted #e5e7eb; }
    .grounding-item:last-child { border-bottom: none; }
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
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">📊 Risk & Compliance <span style="color:#29B5E8;">Overview</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Executive dashboard — portfolio health, risk posture, and compliance status at a glance.</p>
""", unsafe_allow_html=True)

# --- KPIs ---
kpis = session.sql(f"""
    SELECT 
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.CUSTOMERS) AS total_customers,
        (SELECT SUM(CURRENT_BALANCE) FROM {DB}.{SCHEMA}.ACCOUNTS) AS total_aum,
        (SELECT SUM(AMOUNT) FROM {DB}.{SCHEMA}.TRANSACTIONS) AS total_txn_volume,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.TRANSACTIONS) AS total_txns,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ALERTS WHERE STATUS IN ('OPEN','UNDER_REVIEW','ESCALATED')) AS open_alerts,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ALERTS WHERE SEVERITY = 'CRITICAL' AND STATUS != 'CLOSED') AS critical_alerts,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.CUSTOMERS WHERE KYC_RISK_TIER IN ('HIGH','VERY_HIGH')) AS high_risk_customers,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.CUSTOMERS WHERE IS_PEP = TRUE) AS pep_count,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ACCOUNTS WHERE NPA_STATUS != 'STANDARD') AS npa_accounts,
        (SELECT SUM(CURRENT_BALANCE) FROM {DB}.{SCHEMA}.ACCOUNTS WHERE NPA_STATUS != 'STANDARD') AS npa_exposure
""").collect()[0]

aum_cr = (kpis["TOTAL_AUM"] or 0) / 10000000
vol_cr = (kpis["TOTAL_TXN_VOLUME"] or 0) / 10000000
npa_cr = (kpis["NPA_EXPOSURE"] or 0) / 10000000

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card info"><div class="kpi-value">{kpis["TOTAL_CUSTOMERS"]}</div><div class="kpi-label">Customers</div><div class="kpi-sub">CUSTOMERS table</div></div>
    <div class="kpi-card success"><div class="kpi-value">₹{aum_cr:.0f}Cr</div><div class="kpi-label">Total AUM</div><div class="kpi-sub">ACCOUNTS.CURRENT_BALANCE</div></div>
    <div class="kpi-card info"><div class="kpi-value">₹{vol_cr:.0f}Cr</div><div class="kpi-label">Txn Volume</div><div class="kpi-sub">{kpis["TOTAL_TXNS"]} transactions</div></div>
    <div class="kpi-card warning"><div class="kpi-value">{kpis["OPEN_ALERTS"]}</div><div class="kpi-label">Open Alerts</div><div class="kpi-sub">ALERTS (non-closed)</div></div>
    <div class="kpi-card critical"><div class="kpi-value">{kpis["CRITICAL_ALERTS"]}</div><div class="kpi-label">Critical Alerts</div><div class="kpi-sub">Severity = CRITICAL</div></div>
    <div class="kpi-card warning"><div class="kpi-value">{kpis["HIGH_RISK_CUSTOMERS"]}</div><div class="kpi-label">High Risk</div><div class="kpi-sub">{kpis["PEP_COUNT"]} PEPs identified</div></div>
</div>
""", unsafe_allow_html=True)

# --- Row 2: Daily Transaction Trend ---
st.markdown('<div class="section-header">Daily Transaction Trend</div>', unsafe_allow_html=True)

trend_df = session.sql(f"""
    SELECT DATE_TRUNC('DAY', TXN_DATE)::DATE AS DAY,
           ROUND(SUM(AMOUNT) / 10000000, 1) AS VOLUME_CR,
           COUNT(*) AS TXN_COUNT,
           SUM(CASE WHEN RISK_SCORE > 70 THEN 1 ELSE 0 END) AS HIGH_RISK_TXNS
    FROM {DB}.{SCHEMA}.TRANSACTIONS
    GROUP BY DAY ORDER BY DAY
""").to_pandas()

if not trend_df.empty:
    trend_df = trend_df.rename(columns={"DAY": "Date", "VOLUME_CR": "Volume (Cr)", "HIGH_RISK_TXNS": "High Risk Txns"})
    trend_df = trend_df.set_index("Date")
    col_vol, col_risk = st.columns([3, 2])
    with col_vol:
        st.caption("Transaction Volume (INR Crores) — Source: TRANSACTIONS table")
        st.area_chart(trend_df[["Volume (Cr)"]], color="#29B5E8", height=220)
    with col_risk:
        st.caption("High-Risk Transactions per Day (Risk Score > 70)")
        st.bar_chart(trend_df[["High Risk Txns"]], color="#dc2626", height=220)

# --- Row 3: Alerts + Customer Risk ---
col_alerts, col_cust = st.columns(2)

with col_alerts:
    st.markdown('<div class="section-header">Alert Distribution</div>', unsafe_allow_html=True)
    alert_dist = session.sql(f"""
        SELECT ALERT_CATEGORY AS CATEGORY, SEVERITY,
               COUNT(*) AS COUNT
        FROM {DB}.{SCHEMA}.ALERTS
        GROUP BY ALERT_CATEGORY, SEVERITY
        ORDER BY ALERT_CATEGORY
    """).to_pandas()
    if not alert_dist.empty:
        pivot = alert_dist.pivot_table(index="CATEGORY", columns="SEVERITY", values="COUNT", fill_value=0).reset_index()
        pivot = pivot.set_index("CATEGORY")
        sev_colors = []
        for col in pivot.columns:
            if col == "CRITICAL":
                sev_colors.append("#dc2626")
            elif col == "HIGH":
                sev_colors.append("#f59e0b")
            elif col == "MEDIUM":
                sev_colors.append("#29B5E8")
            else:
                sev_colors.append("#10b981")
        st.bar_chart(pivot, color=sev_colors, height=250)
        st.caption("Source: ALERTS table — grouped by ALERT_CATEGORY x SEVERITY")

with col_cust:
    st.markdown('<div class="section-header">Customer Risk Profile</div>', unsafe_allow_html=True)
    risk_profile = session.sql(f"""
        SELECT c.FULL_NAME, c.CUSTOMER_TYPE, c.KYC_RISK_TIER,
               ROUND(a.COMPOSITE_AML_SCORE, 1) AS AML_SCORE,
               CASE WHEN c.IS_PEP THEN 'Yes' ELSE 'No' END AS PEP,
               CASE WHEN c.SANCTIONS_MATCH THEN 'MATCH' ELSE 'Clear' END AS SANCTIONS
        FROM {DB}.{SCHEMA}.CUSTOMERS c
        JOIN {DB}.{SCHEMA}.V_AML_SCORING a ON c.CUSTOMER_ID = a.CUSTOMER_ID
        ORDER BY a.COMPOSITE_AML_SCORE DESC
    """).to_pandas()
    if not risk_profile.empty:
        st.dataframe(risk_profile, use_container_width=True, hide_index=True,
                     column_config={
                         "AML_SCORE": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
                     }, height=290)
        st.caption("Source: CUSTOMERS + V_AML_SCORING (composite risk score)")

# --- Row 4: NPA Exposure + Cross-Border ---
col_npa, col_xborder = st.columns(2)

with col_npa:
    st.markdown('<div class="section-header">NPA Exposure by Account Type</div>', unsafe_allow_html=True)
    npa_df = session.sql(f"""
        SELECT ACCOUNT_TYPE, NPA_STATUS,
               ROUND(SUM(CURRENT_BALANCE) / 10000000, 1) AS BALANCE_CR
        FROM {DB}.{SCHEMA}.ACCOUNTS
        WHERE NPA_STATUS != 'STANDARD'
        GROUP BY ACCOUNT_TYPE, NPA_STATUS
        ORDER BY BALANCE_CR DESC
    """).to_pandas()
    if not npa_df.empty:
        npa_pivot = npa_df.pivot_table(index="ACCOUNT_TYPE", columns="NPA_STATUS", values="BALANCE_CR", fill_value=0).reset_index()
        npa_pivot = npa_pivot.set_index("ACCOUNT_TYPE")
        npa_colors = []
        for col in npa_pivot.columns:
            if col == "LOSS":
                npa_colors.append("#dc2626")
            elif col == "DOUBTFUL":
                npa_colors.append("#f59e0b")
            else:
                npa_colors.append("#fb923c")
        st.bar_chart(npa_pivot, color=npa_colors, height=250)
        st.caption("Source: ACCOUNTS table — NPA_STATUS x ACCOUNT_TYPE (INR Cr)")
    else:
        st.success("No NPA exposure detected.")

    st.markdown(f"""
    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:10px 14px; margin-top:8px;">
        <span style="font-size:0.8rem; font-weight:600; color:#dc2626;">{kpis["NPA_ACCOUNTS"]} NPA Accounts</span>
        <span style="font-size:0.8rem; color:#374151;"> — Total exposure: ₹{npa_cr:.1f} Cr</span>
    </div>
    """, unsafe_allow_html=True)

with col_xborder:
    st.markdown('<div class="section-header">Cross-Border Transaction Risk</div>', unsafe_allow_html=True)
    xborder_df = session.sql(f"""
        SELECT COUNTERPARTY_COUNTRY AS COUNTRY,
               COUNT(*) AS TXN_COUNT,
               ROUND(SUM(AMOUNT) / 10000000, 1) AS VOLUME_CR,
               ROUND(AVG(RISK_SCORE), 1) AS AVG_RISK_SCORE,
               MAX(RISK_SCORE) AS MAX_RISK_SCORE
        FROM {DB}.{SCHEMA}.TRANSACTIONS
        WHERE COUNTERPARTY_COUNTRY IS NOT NULL AND COUNTERPARTY_COUNTRY != 'India'
        GROUP BY COUNTERPARTY_COUNTRY
        ORDER BY AVG_RISK_SCORE DESC
    """).to_pandas()
    if not xborder_df.empty:
        st.dataframe(xborder_df, use_container_width=True, hide_index=True,
                     column_config={
                         "AVG_RISK_SCORE": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
                         "VOLUME_CR": st.column_config.NumberColumn(format="₹%.1f Cr"),
                     }, height=250)
        st.caption("Source: TRANSACTIONS — non-India counterparty countries")

    high_risk_countries = len(xborder_df[xborder_df["AVG_RISK_SCORE"] > 50]) if not xborder_df.empty else 0
    st.markdown(f"""
    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px 14px; margin-top:8px;">
        <span style="font-size:0.8rem; font-weight:600; color:#d97706;">{high_risk_countries} High-Risk Jurisdictions</span>
        <span style="font-size:0.8rem; color:#374151;"> — Avg risk score > 50</span>
    </div>
    """, unsafe_allow_html=True)

# --- AI Executive Summary ---
st.markdown('<div class="section-header">AI Executive Summary</div>', unsafe_allow_html=True)

with st.status("AI Executive Summary — Processing...", expanded=True) as status:
    st.markdown('<span class="pipeline-step step-active">1. Aggregating risk metrics</span>', unsafe_allow_html=True)
    time.sleep(0.3)

    velocity_anomalies = session.sql(f"""
        SELECT COUNT(*) AS CNT FROM {DB}.{SCHEMA}.DT_TXN_VELOCITY_MONITOR WHERE VELOCITY_FLAG != 'NORMAL'
    """).collect()[0]["CNT"]

    credit_critical = session.sql(f"""
        SELECT COUNT(*) AS CNT FROM {DB}.{SCHEMA}.V_CREDIT_RISK WHERE CREDIT_RISK_LEVEL IN ('HIGH','CRITICAL')
    """).collect()[0]["CNT"]

    liq_stressed = session.sql(f"""
        SELECT COUNT(*) AS CNT FROM {DB}.{SCHEMA}.V_LIQUIDITY_RISK WHERE LIQUIDITY_STRESS_LEVEL IN ('HIGH','CRITICAL')
    """).collect()[0]["CNT"]

    st.markdown(f'<span class="pipeline-step step-done">✓ {kpis["OPEN_ALERTS"]} alerts, {velocity_anomalies} velocity anomalies, {credit_critical} credit risks</span>', unsafe_allow_html=True)

    st.markdown('<span class="pipeline-step step-active">2. Cortex LLM — Generating executive brief</span>', unsafe_allow_html=True)

    summary_prompt = f"""You are a Chief Risk Officer producing a concise executive risk brief. Bullet points only. Be direct.

PORTFOLIO:
- Customers: {kpis["TOTAL_CUSTOMERS"]}, AUM: INR {aum_cr:.0f} Cr, Transactions: {kpis["TOTAL_TXNS"]} (INR {vol_cr:.0f} Cr)
- High-Risk Customers: {kpis["HIGH_RISK_CUSTOMERS"]}, PEPs: {kpis["PEP_COUNT"]}

ALERTS:
- Open: {kpis["OPEN_ALERTS"]}, Critical: {kpis["CRITICAL_ALERTS"]}

RISK SIGNALS:
- NPA Accounts: {kpis["NPA_ACCOUNTS"]} (INR {npa_cr:.1f} Cr exposure)
- Velocity Anomalies: {velocity_anomalies}
- Credit Risk (HIGH/CRITICAL accounts): {credit_critical}
- Liquidity Stressed (HIGH/CRITICAL): {liq_stressed}
- High-Risk Jurisdictions: {high_risk_countries}

Reply in EXACTLY this format:

OVERALL_RISK: [CRITICAL/HIGH/MEDIUM/LOW] - [5 word summary]

KEY_CONCERNS:
- [Concern 1: specific numbers and what they mean]
- [Concern 2: specific numbers and what they mean]
- [Concern 3: specific numbers and what they mean]

IMMEDIATE_ACTIONS:
- [Action 1: what to do now]
- [Action 2: what to escalate]
- [Action 3: regulatory filing needed]

POSITIVE_SIGNALS:
- [One positive observation about the portfolio]"""

    ai_response = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{summary_prompt.replace("'", "''")}') AS INSIGHT
    """).collect()[0]["INSIGHT"]

    st.markdown('<span class="pipeline-step step-done">✓ Executive brief generated</span>', unsafe_allow_html=True)
    status.update(label="AI Executive Summary — Complete", state="complete", expanded=False)

lines = ai_response.strip().split('\n')
risk_line = ""
concerns_lines = []
actions_lines = []
positive_lines = []
current_section = ""
for line in lines:
    line = line.strip().lstrip('*').lstrip('-').strip()
    if not line:
        continue
    if "OVERALL_RISK:" in line:
        risk_line = line.split("OVERALL_RISK:")[-1].strip()
    elif "KEY_CONCERNS:" in line:
        current_section = "concerns"
    elif "IMMEDIATE_ACTIONS:" in line:
        current_section = "actions"
    elif "POSITIVE_SIGNALS:" in line:
        current_section = "positive"
    elif current_section == "concerns" and line:
        concerns_lines.append(line.lstrip('- ').lstrip('* '))
    elif current_section == "actions" and line:
        actions_lines.append(line.lstrip('- ').lstrip('* '))
    elif current_section == "positive" and line:
        positive_lines.append(line.lstrip('- ').lstrip('* '))

risk_color = "#dc2626" if "CRITICAL" in risk_line.upper() else "#f59e0b" if "HIGH" in risk_line.upper() else "#29B5E8"
concerns_html = "".join(f"<li>{c}</li>" for c in concerns_lines[:4]) if concerns_lines else "<li>No major concerns</li>"
actions_html = "".join(f"<li>{a}</li>" for a in actions_lines[:3]) if actions_lines else "<li>Continue monitoring</li>"
positive_html = "".join(f"<li>{p}</li>" for p in positive_lines[:2]) if positive_lines else "<li>Portfolio within normal parameters</li>"

st.markdown(f"""
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
    <div class="ai-card" style="background:{risk_color}15; border:1px solid {risk_color}40;">
        <div class="ai-card-label" style="color:{risk_color};">Overall Risk Posture</div>
        <div class="ai-card-content" style="color:#1a1a2e; font-weight:600;">{risk_line}</div>
    </div>
    <div class="ai-card" style="background:#dc262615; border:1px solid #dc262640;">
        <div class="ai-card-label" style="color:#dc2626;">Key Concerns</div>
        <div class="ai-card-content"><ul>{concerns_html}</ul></div>
    </div>
    <div class="ai-card" style="background:#29B5E815; border:1px solid #29B5E840;">
        <div class="ai-card-label" style="color:#0c7cd5;">Immediate Actions</div>
        <div class="ai-card-content"><ul>{actions_html}</ul></div>
    </div>
    <div class="ai-card" style="background:#10b98115; border:1px solid #10b98140;">
        <div class="ai-card-label" style="color:#059669;">Positive Signals</div>
        <div class="ai-card-content"><ul>{positive_html}</ul></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Data Grounding Footer ---
st.markdown(f"""
<div class="grounding-box">
    <div class="grounding-title">Data Grounding — All metrics sourced from Snowflake objects</div>
    <div class="grounding-item">🗄️ <strong>{DB}.{SCHEMA}.CUSTOMERS</strong> — Customer profiles, KYC risk tiers, PEP status, sanctions screening</div>
    <div class="grounding-item">🗄️ <strong>{DB}.{SCHEMA}.ACCOUNTS</strong> — Account balances, credit limits, NPA classification</div>
    <div class="grounding-item">🗄️ <strong>{DB}.{SCHEMA}.TRANSACTIONS</strong> — Transaction history, risk scores, counterparty details</div>
    <div class="grounding-item">🗄️ <strong>{DB}.{SCHEMA}.ALERTS</strong> — Risk alerts by category, severity, and status</div>
    <div class="grounding-item">📊 <strong>{DB}.{SCHEMA}.V_AML_SCORING</strong> — Composite AML risk scores (KYC + txn risk + alerts)</div>
    <div class="grounding-item">📊 <strong>{DB}.{SCHEMA}.V_CREDIT_RISK</strong> — Credit risk levels, NPA status, bounce detection</div>
    <div class="grounding-item">📊 <strong>{DB}.{SCHEMA}.V_LIQUIDITY_RISK</strong> — Liquidity stress levels, outflow ratios</div>
    <div class="grounding-item">⚡ <strong>{DB}.{SCHEMA}.DT_TXN_VELOCITY_MONITOR</strong> — Real-time velocity anomaly detection (1-min lag)</div>
    <div class="grounding-item">🤖 <strong>SNOWFLAKE.CORTEX.COMPLETE</strong> — AI executive summary via llama3.1-8b</div>
</div>
""", unsafe_allow_html=True)
