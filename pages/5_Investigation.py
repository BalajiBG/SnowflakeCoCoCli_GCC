import streamlit as st
import json
import re
from fpdf import FPDF
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Investigation", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"
LLM_MODEL = "llama3.1-70b"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="CORTEX.COMPLETE generates formal investigation summaries with evidence citations" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🤖 <strong>Cortex Complete</strong> <span style="color:#6b7280;">— AI investigation reports</span>
        </div>
        <div title="Composite AML scoring view combines KYC, transactions, alerts" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>V_AML_SCORING</strong> <span style="color:#6b7280;">— Composite risk scoring</span>
        </div>
        <div title="MCP integration with Jira for compliance ticket creation" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🔗 <strong>MCP (Jira)</strong> <span style="color:#6b7280;">— Create compliance tickets</span>
        </div>
        <div title="Snowflake relational joins across CUSTOMERS, ACCOUNTS, TRANSACTIONS, ALERTS" style="cursor:help; padding:3px 0;">
            🗄️ <strong>Snowflake SQL</strong> <span style="color:#6b7280;">— Cross-table evidence joins</span>
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
    .profile-card {
        background: #f8fbff; border: 1px solid #e8f4fd; border-radius: 12px;
        padding: 20px; margin-bottom: 16px;
    }
    .profile-field { display: inline-block; margin-right: 24px; margin-bottom: 8px; }
    .profile-label { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
    .profile-value { font-size: 0.95rem; font-weight: 600; color: #1a1a2e; }
    .alert-banner {
        background: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid #dc2626;
        border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;
    }
    .alert-banner.high {
        background: #fffbeb; border-color: #fde68a; border-left-color: #f59e0b;
    }
    .score-ring {
        display: inline-flex; align-items: center; justify-content: center;
        width: 80px; height: 80px; border-radius: 50%;
        font-size: 1.5rem; font-weight: 700; color: white;
    }
    .score-critical { background: linear-gradient(135deg, #dc2626, #991b1b); }
    .score-high { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .score-medium { background: linear-gradient(135deg, #29B5E8, #0c7cd5); }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a1a2e;
        padding: 12px 0 8px; border-bottom: 2px solid #29B5E8; margin-bottom: 16px;
    }
    footer { display: none; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">🔍 Investigation <span style="color:#29B5E8;">Workspace</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Drill into alerts, review evidence chains, and generate investigation findings.</p>
""", unsafe_allow_html=True)

# --- Alert Selection ---
alerts = session.sql(f"""
    SELECT ALERT_ID, CUSTOMER_ID, ALERT_TYPE, SEVERITY, STATUS, ALERT_DATE, DESCRIPTION
    FROM {DB}.{SCHEMA}.ALERTS
    WHERE STATUS IN ('OPEN','UNDER_REVIEW','ESCALATED')
    ORDER BY CASE SEVERITY WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END, ALERT_DATE DESC
""").to_pandas()

selected_alert = st.selectbox(
    "Select alert to investigate:",
    alerts["ALERT_ID"].tolist(),
    format_func=lambda x: f"{'🔴' if alerts[alerts['ALERT_ID']==x]['SEVERITY'].values[0]=='CRITICAL' else '🟡'} {x} — {alerts[alerts['ALERT_ID']==x]['ALERT_TYPE'].values[0]} — {alerts[alerts['ALERT_ID']==x]['DESCRIPTION'].values[0][:70]}..."
)

if selected_alert:
    alert_row = alerts[alerts["ALERT_ID"] == selected_alert].iloc[0]
    customer_id = alert_row["CUSTOMER_ID"]

    # Alert Banner
    banner_class = "alert-banner" if alert_row["SEVERITY"] == "CRITICAL" else "alert-banner high"
    st.markdown(f"""
    <div class="{banner_class}">
        <strong>{alert_row['ALERT_TYPE']}</strong> — Severity: <strong>{alert_row['SEVERITY']}</strong> — Status: {alert_row['STATUS']}<br>
        <span style="color:#4b5563;">{alert_row['DESCRIPTION']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Customer Profile Card
    customer = session.sql(f"SELECT * FROM {DB}.{SCHEMA}.CUSTOMERS WHERE CUSTOMER_ID = '{customer_id}'").to_pandas()
    if not customer.empty:
        c = customer.iloc[0]
        st.markdown(f"""
        <div class="profile-card">
            <div style="font-size:0.85rem; color:#29B5E8; font-weight:600; margin-bottom:12px;">SUBJECT PROFILE</div>
            <div class="profile-field"><div class="profile-label">Name</div><div class="profile-value">{c['FULL_NAME']}</div></div>
            <div class="profile-field"><div class="profile-label">Type</div><div class="profile-value">{c['CUSTOMER_TYPE']}</div></div>
            <div class="profile-field"><div class="profile-label">KYC Risk</div><div class="profile-value">{c['KYC_RISK_TIER']}</div></div>
            <div class="profile-field"><div class="profile-label">PEP</div><div class="profile-value">{'⚠️ Yes' if c['IS_PEP'] else 'No'}</div></div>
            <div class="profile-field"><div class="profile-label">Jurisdiction</div><div class="profile-value">{c['JURISDICTION']}</div></div>
            <div class="profile-field"><div class="profile-label">Occupation</div><div class="profile-value">{c['OCCUPATION']}</div></div>
            <div class="profile-field"><div class="profile-label">Sanctions</div><div class="profile-value">{'🔴 MATCH' if c['SANCTIONS_MATCH'] else '🟢 Clear'}</div></div>
            <div class="profile-field"><div class="profile-label">Adverse Media</div><div class="profile-value">{'🔴 Flagged' if c['ADVERSE_MEDIA_FLAG'] else '🟢 Clear'}</div></div>
        </div>
        """, unsafe_allow_html=True)

    # AML Score + Transactions in columns
    col_score, col_txn = st.columns([1, 3])
    
    with col_score:
        aml = session.sql(f"SELECT * FROM {DB}.{SCHEMA}.V_AML_SCORING WHERE CUSTOMER_ID = '{customer_id}'").to_pandas()
        if not aml.empty:
            a = aml.iloc[0]
            score = a['COMPOSITE_AML_SCORE']
            score_class = "score-critical" if score > 75 else ("score-high" if score > 50 else "score-medium")
            st.markdown(f"""
            <div style="text-align:center; padding:20px;">
                <div class="score-ring {score_class}">{score:.0f}</div>
                <div style="margin-top:8px; font-size:0.8rem; color:#6b7280;">AML SCORE</div>
                <div style="margin-top:12px; font-size:0.85rem; font-weight:500; color:#1a1a2e;">{a['RECOMMENDED_ACTION']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_txn:
        st.markdown('<div class="section-header">Related Transactions (by risk score)</div>', unsafe_allow_html=True)
        txns = session.sql(f"""
            SELECT t.TXN_ID, t.TXN_DATE, t.TXN_TYPE, t.AMOUNT, t.CURRENCY,
                   t.COUNTERPARTY_NAME, t.COUNTERPARTY_COUNTRY, t.RISK_SCORE
            FROM {DB}.{SCHEMA}.TRANSACTIONS t
            JOIN {DB}.{SCHEMA}.ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
            WHERE a.CUSTOMER_ID = '{customer_id}'
            ORDER BY t.RISK_SCORE DESC, t.TXN_DATE DESC LIMIT 15
        """).to_pandas()
        st.dataframe(txns, use_container_width=True, hide_index=True,
                     column_config={
                         "RISK_SCORE": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
                         "AMOUNT": st.column_config.NumberColumn(format="₹%d")
                     })

    # AI Investigation
    st.markdown('<div class="section-header">AI Investigation Summary</div>', unsafe_allow_html=True)
    if st.button("Generate Investigation Report", type="primary", use_container_width=True):
        with st.spinner("Assembling evidence and generating investigation report..."):
            alert_detail = session.sql(f"SELECT * FROM {DB}.{SCHEMA}.ALERTS WHERE ALERT_ID = '{selected_alert}'").collect()[0]
            txn_summary = session.sql(f"""
                SELECT TXN_TYPE, COUNT(*) AS cnt, SUM(AMOUNT) AS total, MAX(RISK_SCORE) AS max_risk,
                       LISTAGG(DISTINCT COUNTERPARTY_COUNTRY, ', ') AS countries
                FROM {DB}.{SCHEMA}.TRANSACTIONS t
                JOIN {DB}.{SCHEMA}.ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
                WHERE a.CUSTOMER_ID = '{customer_id}' GROUP BY TXN_TYPE
            """).collect()
            
            context = f"""Alert: {alert_detail['DESCRIPTION']}
Evidence: {alert_detail['EVIDENCE_SUMMARY']}
Customer: {customer.iloc[0].to_dict() if not customer.empty else 'Unknown'}
Transaction Profile: {json.dumps([r.as_dict() for r in txn_summary], default=str)}"""

            prompt = f"""You are a senior AML investigator producing a formal investigation report.

{context}

Produce a structured report:
## Investigation Summary
### Subject & Background
### Alert Trigger & Timeline
### Key Findings
### Risk Indicators Identified
### Typology Match
### Recommendation
### Evidence Strength Assessment"""

            escaped = prompt.replace("'", "''")
            summary = session.sql(f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{LLM_MODEL}', '{escaped}') AS response").collect()[0]["RESPONSE"]
            st.session_state["investigation_summary"] = summary
            st.session_state["investigation_alert"] = selected_alert

    # Show report and actions if summary exists for this alert
    if st.session_state.get("investigation_alert") == selected_alert and st.session_state.get("investigation_summary"):
        summary = st.session_state["investigation_summary"]
        st.markdown(summary)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pw = pdf.w - 20

        # Header
        pdf.set_fill_color(220, 38, 38)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(pw, 7, "CONFIDENTIAL - INTERNAL USE ONLY", ln=True, align="C", fill=True)
        pdf.ln(4)
        pdf.set_text_color(26, 26, 46)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(pw, 10, "INVESTIGATION REPORT", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(pw, 6, "AML/CFT Compliance Investigation", ln=True, align="C")
        pdf.ln(6)

        # Doc metadata
        pdf.set_fill_color(248, 249, 250)
        import hashlib as _hl
        _doc_hash = _hl.sha256(f"{selected_alert}{customer_id}".encode()).hexdigest()[:16].upper()
        meta_items = [
            ("Alert ID", selected_alert),
            ("Subject", customer.iloc[0]['FULL_NAME'] if not customer.empty else "Unknown"),
            ("Customer ID", customer_id),
            ("Severity", alert_row['SEVERITY']),
            ("Alert Type", alert_row['ALERT_TYPE']),
            ("Document Hash", _doc_hash),
        ]
        for label, value in meta_items:
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(40, 5, label + ":", fill=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(pw - 40, 5, str(value), ln=True, fill=True)
        pdf.ln(6)

        # Separator
        pdf.set_draw_color(41, 181, 232)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(4)

        # Body content
        pdf.set_font("Helvetica", "", 10)
        for line in summary.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
            pdf.set_x(10)
            if line.startswith("## "):
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 13)
                pdf.set_text_color(26, 26, 46)
                pdf.cell(0, 8, line.replace("## ", ""), ln=True)
                pdf.set_draw_color(41, 181, 232)
                pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
                pdf.ln(2)
                pdf.set_font("Helvetica", "", 10)
            elif line.startswith("### "):
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(26, 26, 46)
                pdf.cell(0, 7, line.replace("### ", ""), ln=True)
                pdf.set_font("Helvetica", "", 10)
            elif line.startswith("- ") or line.startswith("* "):
                pdf.set_x(15)
                pdf.set_text_color(26, 26, 46)
                pdf.multi_cell(180, 5, line)
            else:
                pdf.set_text_color(26, 26, 46)
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                pdf.multi_cell(190, 5, clean_line)

        # Footer
        pdf.ln(10)
        pdf.set_draw_color(26, 26, 46)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(26, 26, 46)
        pdf.cell(pw/2, 5, "Prepared By:")
        pdf.cell(pw/2, 5, "Reviewing Officer:", ln=True)
        pdf.cell(pw/2, 5, "CoCoIceberg AI Compliance Engine")
        pdf.cell(pw/2, 5, "", ln=True)
        pdf.ln(8)
        pdf.cell(pw/2, 5, "___________________________")
        pdf.cell(pw/2, 5, "___________________________", ln=True)
        pdf.cell(pw/2, 5, "System Generated")
        pdf.cell(pw/2, 5, "Name & Designation", ln=True)
        pdf.ln(8)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(pw, 4, "This document is system-generated and classified CONFIDENTIAL.", ln=True, align="C")
        pdf.cell(pw, 4, f"Alert: {selected_alert} | Hash: {_doc_hash} | System: CoCoIceberg v1.0", ln=True, align="C")

        pdf_bytes = bytes(pdf.output())
        st.download_button(
            "Download Report (PDF)",
            pdf_bytes,
            file_name=f"investigation_{selected_alert}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # --- Actions: Escalate & Create Jira Ticket ---
        st.markdown('<div class="section-header">Actions</div>', unsafe_allow_html=True)
        col_esc, col_tkt = st.columns(2)
        with col_esc:
            if st.button("⚠️ Escalate Alert", use_container_width=True):
                session.sql(f"CALL {DB}.{SCHEMA}.ESCALATE_ALERT('{selected_alert}', 'Escalated via Investigation Workspace')").collect()
                st.success(f"Alert {selected_alert} escalated.")
        with col_tkt:
            if st.button("🎫 Create Jira Ticket", use_container_width=True):
                ticket_summary = f"[{alert_row['SEVERITY']}] {alert_row['ALERT_TYPE']} - {customer_id}"
                ticket_desc = summary[:2000]
                session.sql(f"""
                    INSERT INTO {DB}.{SCHEMA}.COMPLIANCE_TICKETS 
                    (ALERT_ID, CUSTOMER_ID, CUSTOMER_NAME, SEVERITY, SUMMARY, DESCRIPTION)
                    VALUES ('{selected_alert}', '{customer_id}', 
                            '{customer.iloc[0]["FULL_NAME"] if not customer.empty else "Unknown"}',
                            '{alert_row["SEVERITY"]}', 
                            '{ticket_summary.replace(chr(39), chr(39)+chr(39))}',
                            '{ticket_desc.replace(chr(39), chr(39)+chr(39))}')
                """).collect()
                st.success(f"Compliance ticket created for {selected_alert}. Pending Jira sync via MCP.")

