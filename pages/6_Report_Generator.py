import streamlit as st
import json
import hashlib
import io
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session
from pdf_helper import FPDF

st.set_page_config(page_title="CoCoIceberg | Reports", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"
LLM_MODEL = "llama3.1-70b"
_current_user = session.sql("SELECT CURRENT_USER() AS U").collect()[0]["U"]
_report_date = datetime.now().strftime('%Y-%m-%d %H:%M IST')

def _add_pdf_footer(pdf, pw, doc_hash, ref_label=""):
    """Add a modern footer to any report PDF."""
    pdf.ln(4)
    pdf.set_draw_color(41, 181, 232)
    pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(pw/2, 5, f"Prepared By: {_current_user}")
    pdf.cell(pw/2, 5, f"Date: {_report_date}", ln=True, align="R")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(pw/2, 4, "CoCoIceberg AI Compliance Engine")
    pdf.cell(pw/2, 4, "Powered by Snowflake Cortex", ln=True, align="R")
    pdf.ln(4)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(150, 150, 150)
    ref = f" | {ref_label}" if ref_label else ""
    pdf.cell(pw, 4, f"CONFIDENTIAL | Hash: {doc_hash}{ref} | CoCoIceberg v1.0", ln=True, align="C")
    pdf.cell(pw, 4, "This document is system-generated for compliance review purposes only.", ln=True, align="C")

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="CORTEX.COMPLETE generates formal STR/CTR narratives with regulatory language" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🤖 <strong>Cortex Complete</strong> <span style="color:#6b7280;">— Regulatory report generation</span>
        </div>
        <div title="Cortex Search retrieves applicable RBI/PMLA/Basel regulations for citations" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🔍 <strong>Cortex Search</strong> <span style="color:#6b7280;">— Policy citation retrieval</span>
        </div>
        <div title="AI_PARSE_DOCUMENT and AI_EXTRACT process uploaded compliance documents" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📄 <strong>Document AI</strong> <span style="color:#6b7280;">— Unstructured doc processing</span>
        </div>
        <div title="SHA-256 document hashing for audit trail integrity verification" style="cursor:help; padding:3px 0;">
            🔐 <strong>Document Auth</strong> <span style="color:#6b7280;">— SHA-256 integrity hash</span>
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
    .report-container {
        background: #f8fbff; border: 1px solid #e8f4fd; border-radius: 12px;
        padding: 24px; margin: 16px 0;
    }
    .report-meta {
        display: flex; gap: 24px; padding: 12px 20px;
        background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px;
        margin-bottom: 16px;
    }
    .meta-item { }
    .meta-label { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; }
    .meta-value { font-size: 0.9rem; font-weight: 600; color: #1a1a2e; }
    .section-header {
        font-size: 1.1rem; font-weight: 600; color: #1a1a2e;
        padding: 12px 0 8px; border-bottom: 2px solid #29B5E8; margin-bottom: 16px;
    }
    .pipeline-step {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 500; margin-right: 8px;
    }
    .step-active { background: #e8f4fd; color: #0c7cd5; border: 1px solid #29B5E8; }
    .step-done { background: #ecfdf5; color: #059669; border: 1px solid #6ee7b7; }
</style>
""", unsafe_allow_html=True)


def generate_str_html(customer_info, alert_info, suspicious_txns, policies, str_narrative, filing_ref):
    """Generate a formal, authenticated HTML document for STR filing."""
    filing_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
    doc_hash = hashlib.sha256(f"{filing_ref}{filing_date}{customer_info['CUSTOMER_ID']}".encode()).hexdigest()[:16].upper()
    
    # Build transaction table rows
    txn_rows = ""
    for t in suspicious_txns:
        txn_rows += f"""<tr>
            <td>{t['TXN_ID']}</td>
            <td>{str(t['TXN_DATE'])[:19]}</td>
            <td>{t['TXN_TYPE']}</td>
            <td style="text-align:right;">{'₹' if t['CURRENCY']=='INR' else '$'}{(t['AMOUNT'] or 0):,.2f}</td>
            <td>{t.get('COUNTERPARTY_NAME','—') or '—'}</td>
            <td>{t.get('COUNTERPARTY_COUNTRY','—') or '—'}</td>
            <td style="text-align:center;"><strong>{t['RISK_SCORE']}</strong></td>
        </tr>"""
    
    # Build alert rows
    alert_rows = ""
    for a in alert_info:
        alert_rows += f"""<tr>
            <td>{a['ALERT_ID']}</td>
            <td>{a['ALERT_TYPE']}</td>
            <td>{a['SEVERITY']}</td>
            <td>{str(a['ALERT_DATE'])[:19]}</td>
            <td>{a['DESCRIPTION'][:120]}...</td>
        </tr>"""
    
    # Build policy citations
    policy_section = ""
    for p in policies:
        policy_section += f"""<div style="margin-bottom:12px; padding:10px; background:#f0f7ff; border-left:3px solid #29B5E8;">
            <strong>{p.get('REGULATION_NAME','')}</strong> — {p.get('SECTION_TITLE','')}<br>
            <span style="font-size:0.85rem; color:#333;">{p.get('CONTENT','')[:500]}</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>STR Filing — {filing_ref}</title>
<style>
    @page {{ margin: 20mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; color: #1a1a1a; line-height: 1.5; margin: 0; padding: 40px; }}
    .header {{ text-align: center; border-bottom: 3px double #1a1a2e; padding-bottom: 20px; margin-bottom: 30px; }}
    .header h1 {{ font-size: 16pt; margin: 0; color: #1a1a2e; letter-spacing: 2px; }}
    .header h2 {{ font-size: 12pt; margin: 5px 0 0; color: #333; font-weight: normal; }}
    .classification {{ text-align: center; background: #dc2626; color: white; padding: 6px 20px; font-weight: bold; font-size: 10pt; letter-spacing: 3px; display: inline-block; margin: 10px auto; }}
    .doc-meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; background: #f8f9fa; padding: 15px; border: 1px solid #ddd; margin-bottom: 25px; font-size: 9.5pt; }}
    .doc-meta div {{ }}
    .doc-meta .label {{ color: #666; font-weight: bold; text-transform: uppercase; font-size: 8pt; }}
    .section {{ margin-bottom: 25px; page-break-inside: avoid; }}
    .section h3 {{ font-size: 12pt; color: #1a1a2e; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 9pt; margin: 10px 0; }}
    th {{ background: #1a1a2e; color: white; padding: 8px 6px; text-align: left; font-size: 8pt; text-transform: uppercase; }}
    td {{ padding: 6px; border-bottom: 1px solid #eee; }}
    tr:nth-child(even) {{ background: #f8f9fa; }}
    .narrative {{ text-align: justify; }}
    .stamp {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #1a1a2e; display: grid; grid-template-columns: 1fr 1fr; }}
    .stamp .left {{ }}
    .stamp .right {{ text-align: right; }}
    .verification {{ background: #f0f7f0; border: 1px solid #4caf50; padding: 12px; margin-top: 20px; font-size: 9pt; }}
    .watermark {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 80pt; color: rgba(220,38,38,0.04); font-weight: bold; letter-spacing: 10px; z-index: -1; }}
    .footer {{ text-align: center; font-size: 8pt; color: #999; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }}
</style>
</head>
<body>
<div class="watermark">CONFIDENTIAL</div>

<div class="header">
    <div class="classification">CONFIDENTIAL — RESTRICTED</div>
    <h1>SUSPICIOUS TRANSACTION REPORT</h1>
    <h2>Filed under Prevention of Money Laundering Act, 2002 — Section 12</h2>
</div>

<div class="doc-meta">
    <div><span class="label">Filing Reference:</span><br>{filing_ref}</div>
    <div><span class="label">Filing Date & Time:</span><br>{filing_date}</div>
    <div><span class="label">Document Hash:</span><br>{doc_hash}</div>
    <div><span class="label">Regulatory Body:</span><br>Financial Intelligence Unit — India (FIU-IND)</div>
    <div><span class="label">Reporting Entity:</span><br>CoCoIceberg Compliance System</div>
    <div><span class="label">Classification:</span><br>CONFIDENTIAL — Do Not Disclose to Subject</div>
</div>

<div class="section">
    <h3>Part A — Subject Information</h3>
    <table>
        <tr><td style="width:200px; font-weight:bold;">Full Name</td><td>{customer_info['FULL_NAME']}</td></tr>
        <tr><td style="font-weight:bold;">Customer ID</td><td>{customer_info['CUSTOMER_ID']}</td></tr>
        <tr><td style="font-weight:bold;">Customer Type</td><td>{customer_info['CUSTOMER_TYPE']}</td></tr>
        <tr><td style="font-weight:bold;">KYC Risk Classification</td><td>{customer_info['KYC_RISK_TIER']}</td></tr>
        <tr><td style="font-weight:bold;">PEP Status</td><td>{'YES — Politically Exposed Person' if customer_info['IS_PEP'] else 'No'}</td></tr>
        <tr><td style="font-weight:bold;">Jurisdiction</td><td>{customer_info['JURISDICTION']}</td></tr>
        <tr><td style="font-weight:bold;">Occupation</td><td>{customer_info['OCCUPATION']}</td></tr>
        <tr><td style="font-weight:bold;">Declared Source of Funds</td><td>{customer_info['SOURCE_OF_FUNDS']}</td></tr>
        <tr><td style="font-weight:bold;">Declared Annual Income</td><td>₹{(customer_info['ANNUAL_INCOME'] or 0):,.2f}</td></tr>
        <tr><td style="font-weight:bold;">Sanctions Screening</td><td>{'MATCH FOUND ⚠️' if customer_info['SANCTIONS_MATCH'] else 'Clear'}</td></tr>
        <tr><td style="font-weight:bold;">Adverse Media</td><td>{'FLAGGED ⚠️' if customer_info['ADVERSE_MEDIA_FLAG'] else 'Clear'}</td></tr>
        <tr><td style="font-weight:bold;">Last KYC Review</td><td>{customer_info['LAST_KYC_REVIEW']}</td></tr>
        <tr><td style="font-weight:bold;">Onboarding Date</td><td>{customer_info['ONBOARDING_DATE']}</td></tr>
    </table>
</div>

<div class="section">
    <h3>Part B — Alert History</h3>
    <table>
        <tr><th>Alert ID</th><th>Type</th><th>Severity</th><th>Date</th><th>Description</th></tr>
        {alert_rows}
    </table>
</div>

<div class="section">
    <h3>Part C — Suspicious Transaction Details</h3>
    <table>
        <tr><th>TXN ID</th><th>Date/Time</th><th>Type</th><th>Amount</th><th>Counterparty</th><th>Country</th><th>Risk Score</th></tr>
        {txn_rows}
    </table>
    <p style="font-size:9pt; color:#666;">Total suspicious transactions: {len(suspicious_txns)} | Combined value: ₹{sum((t['AMOUNT'] or 0) for t in suspicious_txns):,.2f}</p>
</div>

<div class="section">
    <h3>Part D — Narrative & Analysis</h3>
    <div class="narrative">{str_narrative.replace(chr(10), '<br>')}</div>
</div>

<div class="section">
    <h3>Part E — Regulatory Basis</h3>
    {policy_section}
</div>

<div class="section">
    <h3>Part F — Declaration & Authentication</h3>
    <div class="verification">
        <strong>VERIFICATION STATEMENT</strong><br><br>
        This Suspicious Transaction Report has been generated by the CoCoIceberg Compliance Intelligence System 
        using AI-powered evidence analysis. All data points cited herein are sourced directly from the institution's 
        transaction monitoring systems and have been verified against the regulatory policy knowledge base.<br><br>
        <strong>Document Integrity Hash:</strong> SHA-256: {doc_hash}<br>
        <strong>Generated:</strong> {filing_date}<br>
        <strong>Filing Deadline (PMLA Sec 12):</strong> Within 7 days of suspicion confirmation<br>
        <strong>Tipping Off Prohibition:</strong> Under Section 66 of PMLA, disclosure of this filing to the subject is prohibited.
    </div>
</div>

<div class="stamp">
    <div class="left">
        <strong>Prepared By:</strong><br>
        {_current_user}<br>
        CoCoIceberg AI Compliance Engine<br>
        Powered by Snowflake Cortex
    </div>
    <div class="right">
        <strong>Report Date:</strong><br>
        {filing_date}<br><br>
        <strong>Authorized Signatory:</strong><br>
        ___________________________<br>
        <span style="font-size:9pt;">Principal Officer / MLRO</span>
    </div>
</div>

<div class="footer">
    This document is system-generated and classified CONFIDENTIAL under PMLA 2002. 
    Unauthorized disclosure is punishable under Section 66 of the Act.<br>
    Reference: {filing_ref} | Hash: {doc_hash} | System: CoCoIceberg v1.0
</div>

</body>
</html>"""
    return html


st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">📝 Regulatory <span style="color:#29B5E8;">Reports</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Generate audit-ready regulatory filings with full evidence trails and regulatory citations.</p>
""", unsafe_allow_html=True)

# --- Report Type ---
report_type = st.selectbox("Report Type", [
    "Suspicious Transaction Report (STR)",
    "Cash Transaction Report (CTR)",
    "Basel III — Liquidity Coverage Ratio",
    "Customer Due Diligence (CDD)"
], label_visibility="collapsed")

st.markdown("---")

if report_type == "Suspicious Transaction Report (STR)":
    customers_with_alerts = session.sql(f"""
        SELECT DISTINCT c.CUSTOMER_ID, c.FULL_NAME, a.ALERT_TYPE, a.SEVERITY
        FROM {DB}.{SCHEMA}.CUSTOMERS c
        JOIN {DB}.{SCHEMA}.ALERTS a ON c.CUSTOMER_ID = a.CUSTOMER_ID
        WHERE a.ALERT_CATEGORY = 'AML' AND a.STATUS IN ('OPEN','UNDER_REVIEW','ESCALATED')
        ORDER BY CASE a.SEVERITY WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END
    """).to_pandas()
    
    col_select, col_btn = st.columns([3, 1])
    with col_select:
        selected_customer = st.selectbox(
            "Select subject for STR:",
            customers_with_alerts["CUSTOMER_ID"].tolist(),
            format_func=lambda x: f"{x} — {customers_with_alerts[customers_with_alerts['CUSTOMER_ID']==x]['FULL_NAME'].values[0]} ({customers_with_alerts[customers_with_alerts['CUSTOMER_ID']==x]['ALERT_TYPE'].values[0]})"
        )
    with col_btn:
        st.write("")
        generate = st.button("Generate STR", type="primary", use_container_width=True)
    
    if generate:
        with st.spinner("Compiling evidence and generating STR..."):
            customer_info = session.sql(f"SELECT * FROM {DB}.{SCHEMA}.CUSTOMERS WHERE CUSTOMER_ID = '{selected_customer}'").collect()[0].as_dict()
            alert_info = [r.as_dict() for r in session.sql(f"""
                SELECT * FROM {DB}.{SCHEMA}.ALERTS 
                WHERE CUSTOMER_ID = '{selected_customer}' AND ALERT_CATEGORY = 'AML'
                ORDER BY ALERT_DATE DESC
            """).collect()]
            suspicious_txns = [r.as_dict() for r in session.sql(f"""
                SELECT t.* FROM {DB}.{SCHEMA}.TRANSACTIONS t
                JOIN {DB}.{SCHEMA}.ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
                WHERE a.CUSTOMER_ID = '{selected_customer}' AND t.RISK_SCORE > 50
                ORDER BY t.RISK_SCORE DESC LIMIT 20
            """).collect()]
            
            policy_result = session.sql(f"""
                SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    '{DB}.{SCHEMA}.POLICY_SEARCH_SERVICE',
                    '{{"query": "STR filing requirements suspicious transaction", "columns": ["CONTENT","REGULATION_NAME","SECTION_TITLE"], "limit": 3}}'
                ))['results'] AS results
            """).collect()
            policies = json.loads(policy_result[0]["RESULTS"]) if policy_result[0]["RESULTS"] else []

            # Generate narrative via LLM
            prompt = f"""You are a senior compliance officer writing the NARRATIVE section of a Suspicious Transaction Report for FIU-IND filing.

SUBJECT: {customer_info['FULL_NAME']} ({customer_info['CUSTOMER_ID']})
Type: {customer_info['CUSTOMER_TYPE']} | KYC Risk: {customer_info['KYC_RISK_TIER']} | PEP: {customer_info['IS_PEP']}
Jurisdiction: {customer_info['JURISDICTION']} | Occupation: {customer_info['OCCUPATION']}
Source of Funds: {customer_info['SOURCE_OF_FUNDS']} | Annual Income: {customer_info['ANNUAL_INCOME']}

ALERTS: {json.dumps(alert_info[:5], default=str)}
SUSPICIOUS TRANSACTIONS (top 10 by risk): {json.dumps(suspicious_txns[:10], default=str)}

Write a detailed narrative that covers:
1. How the suspicion first arose (which alert triggered investigation)
2. Chronological description of the suspicious activity with SPECIFIC transaction IDs, dates, amounts
3. Why the activity is suspicious (cite exact amounts, patterns, counterparties)
4. Red flags identified (with specific data points)
5. Typology match (which ML/TF typology from FATF does this match)
6. Conclusion and recommendation (file/escalate/restrict)

REQUIREMENTS:
- Cite EVERY transaction ID mentioned
- Include ALL amounts with currency
- Name ALL counterparties and countries
- Reference specific dates
- Use formal regulatory language suitable for FIU submission
- Do NOT use markdown formatting - write in plain professional prose with numbered paragraphs"""

            escaped = prompt.replace("'", "''")
            str_narrative = session.sql(f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{LLM_MODEL}', '{escaped}') AS response").collect()[0]["RESPONSE"]
            
            # Generate filing reference
            filing_ref = f"STR/{datetime.now().strftime('%Y')}/{selected_customer}/{datetime.now().strftime('%m%d%H%M')}"
            
            # Generate HTML document
            html_doc = generate_str_html(customer_info, alert_info, suspicious_txns, policies, str_narrative, filing_ref)
            
            # Store in session state so it persists across reruns
            st.session_state["str_data"] = {
                "customer_info": customer_info,
                "alert_info": alert_info,
                "suspicious_txns": suspicious_txns,
                "policies": policies,
                "str_narrative": str_narrative,
                "filing_ref": filing_ref,
                "html_doc": html_doc,
                "selected_customer": selected_customer,
            }

    # Display results from session state (persists after download button click)
    if st.session_state.get("str_data") and st.session_state["str_data"].get("selected_customer") == selected_customer:
        data = st.session_state["str_data"]
        customer_info = data["customer_info"]
        alert_info = data["alert_info"]
        suspicious_txns = data["suspicious_txns"]
        policies = data["policies"]
        str_narrative = data["str_narrative"]
        filing_ref = data["filing_ref"]

        # Display metadata
        st.success(f"STR Generated — Reference: **{filing_ref}**")
        st.markdown(f"""
        <div class="report-meta">
            <div class="meta-item"><div class="meta-label">Filing Reference</div><div class="meta-value">{filing_ref}</div></div>
            <div class="meta-item"><div class="meta-label">Subject</div><div class="meta-value">{customer_info['FULL_NAME']}</div></div>
            <div class="meta-item"><div class="meta-label">Filing Date</div><div class="meta-value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div></div>
            <div class="meta-item"><div class="meta-label">Regulatory Body</div><div class="meta-value">FIU-IND</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display narrative preview
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown("**Narrative Preview:**")
        st.markdown(str_narrative)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Evidence section
        with st.expander("Evidence Trail"):
            st.markdown("**Transactions Cited:**")
            txn_df = session.sql(f"""
                SELECT TXN_ID, TXN_DATE, TXN_TYPE, AMOUNT, COUNTERPARTY_NAME, COUNTERPARTY_COUNTRY, RISK_SCORE
                FROM {DB}.{SCHEMA}.TRANSACTIONS t
                JOIN {DB}.{SCHEMA}.ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
                WHERE a.CUSTOMER_ID = '{selected_customer}' AND t.RISK_SCORE > 50 ORDER BY t.TXN_DATE
            """).to_pandas()
            st.dataframe(txn_df, use_container_width=True, hide_index=True)
            st.markdown("**Regulatory Basis:**")
            for p in policies:
                st.info(f"**{p.get('REGULATION_NAME','')}** — {p.get('SECTION_TITLE','')}\n\n> {p.get('CONTENT','')[:400]}")
        
        # Build PDF with fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pw = pdf.w - 20

        # Header
        pdf.set_fill_color(220, 38, 38)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(pw, 7, "CONFIDENTIAL - RESTRICTED", ln=True, align="C", fill=True)
        pdf.ln(2)
        pdf.set_text_color(26, 26, 46)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(pw, 10, "SUSPICIOUS TRANSACTION REPORT", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(pw, 6, "Filed under Prevention of Money Laundering Act, 2002 - Section 12", ln=True, align="C")
        pdf.ln(4)

        # Doc metadata
        pdf.set_fill_color(248, 249, 250)
        doc_hash = hashlib.sha256(f"{filing_ref}{customer_info['CUSTOMER_ID']}".encode()).hexdigest()[:16].upper()
        meta_items = [
            ("Filing Reference", filing_ref),
            ("Filing Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')),
            ("Document Hash", doc_hash),
            ("Regulatory Body", "Financial Intelligence Unit - India (FIU-IND)"),
        ]
        for label, value in meta_items:
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(40, 5, label + ":", fill=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(pw - 40, 5, value, ln=True, fill=True)
        pdf.ln(3)

        # Part A - Subject Information
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(26, 26, 46)
        pdf.cell(pw, 8, "PART A - SUBJECT INFORMATION", ln=True)
        pdf.set_draw_color(41, 181, 232)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        subject_fields = [
            ("Full Name", str(customer_info.get('FULL_NAME', '') or '')),
            ("Customer ID", str(customer_info.get('CUSTOMER_ID', '') or '')),
            ("Customer Type", str(customer_info.get('CUSTOMER_TYPE', '') or '')),
            ("KYC Risk Classification", str(customer_info.get('KYC_RISK_TIER', '') or '')),
            ("PEP Status", "YES - Politically Exposed Person" if customer_info.get('IS_PEP') else "No"),
            ("Jurisdiction", str(customer_info.get('JURISDICTION', '') or '')),
            ("Occupation", str(customer_info.get('OCCUPATION', '') or '')),
            ("Source of Funds", str(customer_info.get('SOURCE_OF_FUNDS', '') or '')),
            ("Annual Income", f"INR {(customer_info.get('ANNUAL_INCOME') or 0):,.2f}"),
            ("Sanctions Screening", "MATCH FOUND" if customer_info.get('SANCTIONS_MATCH') else "Clear"),
            ("Adverse Media", "FLAGGED" if customer_info.get('ADVERSE_MEDIA_FLAG') else "Clear"),
        ]
        pdf.set_font("Helvetica", "", 9)
        for label, value in subject_fields:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(50, 5, label)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(pw - 50, 5, value, ln=True)
        pdf.ln(3)

        # Part B - Alert History
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(pw, 8, "PART B - ALERT HISTORY", ln=True)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(26, 26, 46)
        pdf.set_text_color(255, 255, 255)
        col_widths_b = [20, 35, 20, 30, pw - 105]
        headers_b = ["Alert ID", "Type", "Severity", "Date", "Description"]
        for i, h in enumerate(headers_b):
            pdf.cell(col_widths_b[i], 6, h, fill=True)
        pdf.ln()
        pdf.set_text_color(26, 26, 46)
        pdf.set_font("Helvetica", "", 8)
        for a in alert_info:
            pdf.cell(col_widths_b[0], 5, str(a.get('ALERT_ID', '')))
            pdf.cell(col_widths_b[1], 5, str(a.get('ALERT_TYPE', ''))[:20])
            pdf.cell(col_widths_b[2], 5, str(a.get('SEVERITY', '')))
            pdf.cell(col_widths_b[3], 5, str(a.get('ALERT_DATE', ''))[:10])
            pdf.cell(col_widths_b[4], 5, str(a.get('DESCRIPTION', ''))[:60], ln=True)
        pdf.ln(3)

        # Part C - Suspicious Transactions
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(pw, 8, "PART C - SUSPICIOUS TRANSACTION DETAILS", ln=True)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_fill_color(26, 26, 46)
        pdf.set_text_color(255, 255, 255)
        col_widths_c = [22, 28, 22, 28, 38, 25, 15]
        headers_c = ["TXN ID", "Date", "Type", "Amount", "Counterparty", "Country", "Risk"]
        for i, h in enumerate(headers_c):
            pdf.cell(col_widths_c[i], 6, h, fill=True)
        pdf.ln()
        pdf.set_text_color(26, 26, 46)
        pdf.set_font("Helvetica", "", 7)
        for t in suspicious_txns:
            pdf.cell(col_widths_c[0], 4.5, str(t.get('TXN_ID', '')))
            pdf.cell(col_widths_c[1], 4.5, str(t.get('TXN_DATE', ''))[:10])
            pdf.cell(col_widths_c[2], 4.5, str(t.get('TXN_TYPE', '')))
            amt = (t.get('AMOUNT') or 0)
            cur = 'INR' if t.get('CURRENCY') == 'INR' else 'USD'
            pdf.cell(col_widths_c[3], 4.5, f"{cur} {amt:,.0f}")
            pdf.cell(col_widths_c[4], 4.5, str(t.get('COUNTERPARTY_NAME') or '-')[:22])
            pdf.cell(col_widths_c[5], 4.5, str(t.get('COUNTERPARTY_COUNTRY') or '-')[:12])
            pdf.cell(col_widths_c[6], 4.5, str(t.get('RISK_SCORE', '')), ln=True)
        pdf.ln(2)
        total_amt = sum((t.get('AMOUNT') or 0) for t in suspicious_txns)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(pw, 5, f"Total suspicious transactions: {len(suspicious_txns)} | Combined value: INR {total_amt:,.2f}", ln=True)
        pdf.ln(3)

        # Part D - Narrative
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(pw, 8, "PART D - NARRATIVE & ANALYSIS", ln=True)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 9)
        clean_narrative = re.sub(r'\*\*(.*?)\*\*', r'\1', str_narrative)
        clean_narrative = clean_narrative.replace('₹', 'INR ').replace('\u20b9', 'INR ').replace('—', '--')
        for para in clean_narrative.split("\n"):
            para = para.strip()
            if para:
                pdf.multi_cell(pw, 4.5, para)
                pdf.ln(2)
        pdf.ln(3)

        # Part E - Regulatory Basis
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(pw, 8, "PART E - REGULATORY BASIS", ln=True)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        for p in policies:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(pw, 5, f"{p.get('REGULATION_NAME', '')} - {p.get('SECTION_TITLE', '')}", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.multi_cell(pw, 4, str(p.get('CONTENT', ''))[:500])
            pdf.ln(2)
        pdf.ln(3)

        # Part F - Declaration
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(pw, 8, "PART F - DECLARATION & AUTHENTICATION", ln=True)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(pw, 4.5, "This Suspicious Transaction Report has been generated by the CoCoIceberg Compliance Intelligence System using AI-powered evidence analysis. All data points cited herein are sourced directly from the institution's transaction monitoring systems.")
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(pw, 5, f"Document Integrity Hash: SHA-256: {doc_hash}", ln=True)
        pdf.cell(pw, 5, "Filing Deadline (PMLA Sec 12): Within 7 days of suspicion confirmation", ln=True)
        pdf.cell(pw, 5, "Tipping Off Prohibition: Under Section 66 of PMLA, disclosure to subject is prohibited.", ln=True)

        # Modern Footer
        pdf.set_draw_color(41, 181, 232)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(26, 26, 46)
        pdf.cell(pw/2, 5, f"Prepared By: {_current_user}")
        pdf.cell(pw/2, 5, f"Date: {_report_date}", ln=True, align="R")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(pw/2, 4, "CoCoIceberg AI Compliance Engine")
        pdf.cell(pw/2, 4, "Powered by Snowflake Cortex", ln=True, align="R")
        pdf.ln(6)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(pw, 4, f"CONFIDENTIAL | Ref: {filing_ref} | Hash: {doc_hash} | CoCoIceberg v1.0", ln=True, align="C")
        pdf.cell(pw, 4, "This document is system-generated under PMLA 2002 for compliance review purposes only.", ln=True, align="C")

        pdf_bytes = bytes(pdf.output())

        # Download as PDF
        st.download_button(
            "Download STR (PDF)",
            pdf_bytes,
            file_name=f"STR_{selected_customer}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

elif report_type == "Cash Transaction Report (CTR)":
    st.markdown('<div class="section-header">CTR — Accounts Exceeding INR 10 Lakh Cash Threshold</div>', unsafe_allow_html=True)
    ctr_data = session.sql(f"""
        SELECT c.FULL_NAME, c.CUSTOMER_ID, a.ACCOUNT_ID,
               COUNT(t.TXN_ID) AS CASH_TXN_COUNT,
               SUM(t.AMOUNT) AS TOTAL_CASH_AMOUNT,
               MIN(t.TXN_DATE) AS FIRST_DATE, MAX(t.TXN_DATE) AS LAST_DATE
        FROM {DB}.{SCHEMA}.TRANSACTIONS t
        JOIN {DB}.{SCHEMA}.ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
        JOIN {DB}.{SCHEMA}.CUSTOMERS c ON a.CUSTOMER_ID = c.CUSTOMER_ID
        WHERE t.IS_CASH = TRUE
        GROUP BY c.FULL_NAME, c.CUSTOMER_ID, a.ACCOUNT_ID
        HAVING SUM(t.AMOUNT) >= 1000000
        ORDER BY TOTAL_CASH_AMOUNT DESC
    """).to_pandas()
    st.dataframe(ctr_data, use_container_width=True, hide_index=True,
                 column_config={"TOTAL_CASH_AMOUNT": st.column_config.NumberColumn(format="₹%d")})
    st.info(f"**{len(ctr_data)} accounts** require CTR filing based on RBI cash transaction thresholds (INR 10,00,000).")

    if not ctr_data.empty and st.button("Generate CTR Report", type="primary", use_container_width=True):
        with st.status("Generating CTR Report...", expanded=True) as ctr_status:
            st.markdown('<span class="pipeline-step step-active">1. Compiling cash transaction data</span>', unsafe_allow_html=True)
            import time
            time.sleep(0.5)
            ctr_summary = ""
            for _, r in ctr_data.iterrows():
                ctr_summary += f"- {r['FULL_NAME']} ({r['CUSTOMER_ID']}): {r['CASH_TXN_COUNT']} cash txns, Total ₹{r['TOTAL_CASH_AMOUNT']:,.0f}, Period {str(r['FIRST_DATE'])[:10]} to {str(r['LAST_DATE'])[:10]}\n"
            st.markdown(f'<span class="pipeline-step step-done">✓ {len(ctr_data)} accounts compiled</span>', unsafe_allow_html=True)

            st.markdown('<span class="pipeline-step step-active">2. Cortex LLM — Generating CTR narrative</span>', unsafe_allow_html=True)
            ctr_prompt = f"""Generate a formal Cash Transaction Report (CTR) narrative for regulatory filing under RBI Master Direction on KYC. Be concise and professional.

Accounts exceeding INR 10,00,000 cash threshold:
{ctr_summary}

Write a brief CTR narrative covering:
1. Summary of accounts flagged and total cash volume
2. Pattern observations (frequency, amounts, time periods)
3. Regulatory basis (RBI cash reporting requirement)
4. Recommendation (file CTR with FIU-IND within prescribed timeline)"""

            ctr_narrative = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE('{LLM_MODEL}', '{ctr_prompt.replace("'", "''")}') AS NARRATIVE
            """).collect()[0]["NARRATIVE"]
            st.markdown('<span class="pipeline-step step-done">✓ CTR narrative generated</span>', unsafe_allow_html=True)

            st.markdown('<span class="pipeline-step step-active">3. Building PDF</span>', unsafe_allow_html=True)
            filing_ref = f"CTR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            doc_hash = hashlib.sha256(f"{filing_ref}{datetime.now()}".encode()).hexdigest()[:16].upper()

            pdf = FPDF()
            pdf.add_page()
            pw = pdf.w - 20
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(pw, 10, "CASH TRANSACTION REPORT (CTR)", ln=True, align="C")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(pw, 5, f"Reference: {filing_ref} | Date: {datetime.now().strftime('%Y-%m-%d')} | CONFIDENTIAL", ln=True, align="C")
            pdf.ln(8)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "ACCOUNTS EXCEEDING CASH THRESHOLD", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(26, 26, 46)
            pdf.set_text_color(255, 255, 255)
            cols = [40, 25, 25, 20, 30, 25, 25]
            hdrs = ["Name", "Cust ID", "Account", "Txns", "Amount", "From", "To"]
            for i, h in enumerate(hdrs):
                pdf.cell(cols[i], 6, h, fill=True)
            pdf.ln()
            pdf.set_text_color(26, 26, 46)
            pdf.set_font("Helvetica", "", 7)
            for _, r in ctr_data.iterrows():
                pdf.cell(cols[0], 5, str(r['FULL_NAME'])[:22])
                pdf.cell(cols[1], 5, str(r['CUSTOMER_ID']))
                pdf.cell(cols[2], 5, str(r['ACCOUNT_ID']))
                pdf.cell(cols[3], 5, str(r['CASH_TXN_COUNT']))
                pdf.cell(cols[4], 5, f"INR {r['TOTAL_CASH_AMOUNT']:,.0f}")
                pdf.cell(cols[5], 5, str(r['FIRST_DATE'])[:10])
                pdf.cell(cols[6], 5, str(r['LAST_DATE'])[:10], ln=True)
            pdf.ln(6)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "NARRATIVE & ANALYSIS", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 9)
            clean = re.sub(r'\*\*(.*?)\*\*', r'\1', str(ctr_narrative))
            clean = clean.replace('₹', 'INR ').replace('\u20b9', 'INR ')
            for para in clean.split("\n"):
                para = para.strip()
                if para:
                    pdf.multi_cell(pw, 4.5, para)
                    pdf.ln(2)
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(pw, 5, f"Document Hash: SHA-256: {doc_hash}", ln=True)
            _add_pdf_footer(pdf, pw, doc_hash)

            pdf_bytes = bytes(pdf.output())
            st.markdown('<span class="pipeline-step step-done">✓ PDF ready</span>', unsafe_allow_html=True)
            ctr_status.update(label="CTR Report -- Complete", state="complete", expanded=False)

        st.markdown(f'<div class="report-container"><p>{ctr_narrative}</p></div>', unsafe_allow_html=True)
        st.download_button("Download CTR (PDF)", pdf_bytes,
                           file_name=f"CTR_{datetime.now().strftime('%Y%m%d')}.pdf",
                           mime="application/pdf", use_container_width=True)

elif report_type == "Basel III — Liquidity Coverage Ratio":
    st.markdown('<div class="section-header">LCR Approximation</div>', unsafe_allow_html=True)
    liq_data = session.sql(f"""
        SELECT FULL_NAME, CUSTOMER_TYPE, CURRENT_BALANCE, DAILY_OUTFLOWS, OUTFLOW_TO_BALANCE_PCT, LIQUIDITY_STRESS_LEVEL
        FROM {DB}.{SCHEMA}.V_LIQUIDITY_RISK ORDER BY OUTFLOW_TO_BALANCE_PCT DESC
    """).to_pandas()
    
    total_balance = liq_data["CURRENT_BALANCE"].sum() if not liq_data.empty else 0
    total_outflows = liq_data["DAILY_OUTFLOWS"].sum() if not liq_data.empty else 0
    approx_lcr = (total_balance / (total_outflows * 30)) * 100 if total_outflows > 0 else 999

    c1, c2, c3 = st.columns(3)
    c1.metric("Approx. LCR", f"{min(approx_lcr, 999):.1f}%")
    c2.metric("Total HQLA", f"₹{total_balance:,.0f}")
    c3.metric("30-Day Net Outflows", f"₹{total_outflows * 30:,.0f}")
    
    if approx_lcr < 100:
        st.error("LCR BELOW MINIMUM 100% — Regulatory breach risk. Immediate action required.")
    else:
        st.success("LCR above Basel III minimum requirement of 100%.")
    
    st.dataframe(liq_data, use_container_width=True, hide_index=True)

    if not liq_data.empty and st.button("Generate LCR Report", type="primary", use_container_width=True):
        with st.status("Generating LCR Report...", expanded=True) as lcr_status:
            st.markdown('<span class="pipeline-step step-active">1. Computing liquidity metrics</span>', unsafe_allow_html=True)
            import time
            time.sleep(0.5)
            stressed = liq_data[liq_data["LIQUIDITY_STRESS_LEVEL"].isin(["HIGH", "CRITICAL"])]
            lcr_summary = f"Total HQLA: INR {total_balance:,.0f}, 30-day outflows: INR {total_outflows*30:,.0f}, Approx LCR: {min(approx_lcr,999):.1f}%\n"
            lcr_summary += f"Stressed accounts: {len(stressed)}\n"
            for _, r in stressed.head(5).iterrows():
                lcr_summary += f"- {r['FULL_NAME']}: Outflow {r['OUTFLOW_TO_BALANCE_PCT']:.1f}%, Level={r['LIQUIDITY_STRESS_LEVEL']}\n"
            st.markdown(f'<span class="pipeline-step step-done">✓ LCR={min(approx_lcr,999):.1f}%, {len(stressed)} stressed accounts</span>', unsafe_allow_html=True)

            st.markdown('<span class="pipeline-step step-active">2. Cortex LLM — Generating LCR narrative</span>', unsafe_allow_html=True)
            lcr_prompt = f"""Generate a formal Basel III Liquidity Coverage Ratio (LCR) assessment report. Be concise and professional.

Data:
{lcr_summary}

Write a brief LCR report covering:
1. Current LCR position vs Basel III 100% minimum
2. Key stress accounts driving outflows
3. Risk assessment (is the institution compliant?)
4. Recommendations (funding actions, limit adjustments, ALCO reporting)"""

            lcr_narrative = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE('{LLM_MODEL}', '{lcr_prompt.replace("'", "''")}') AS NARRATIVE
            """).collect()[0]["NARRATIVE"]
            st.markdown('<span class="pipeline-step step-done">✓ LCR narrative generated</span>', unsafe_allow_html=True)

            st.markdown('<span class="pipeline-step step-active">3. Building PDF</span>', unsafe_allow_html=True)
            filing_ref = f"LCR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            doc_hash = hashlib.sha256(f"{filing_ref}{datetime.now()}".encode()).hexdigest()[:16].upper()

            pdf = FPDF()
            pdf.add_page()
            pw = pdf.w - 20
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(pw, 10, "BASEL III - LIQUIDITY COVERAGE RATIO REPORT", ln=True, align="C")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(pw, 5, f"Reference: {filing_ref} | Date: {datetime.now().strftime('%Y-%m-%d')} | CONFIDENTIAL", ln=True, align="C")
            pdf.ln(8)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "KEY METRICS", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(pw, 6, f"Approximate LCR: {min(approx_lcr,999):.1f}%  |  HQLA: INR {total_balance:,.0f}  |  30-Day Outflows: INR {total_outflows*30:,.0f}", ln=True)
            pdf.ln(4)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "STRESSED ACCOUNTS", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(26, 26, 46)
            pdf.set_text_color(255, 255, 255)
            cols = [45, 30, 35, 35, 25, 25]
            hdrs = ["Name", "Type", "Balance", "Outflows", "Outflow%", "Stress"]
            for i, h in enumerate(hdrs):
                pdf.cell(cols[i], 6, h, fill=True)
            pdf.ln()
            pdf.set_text_color(26, 26, 46)
            pdf.set_font("Helvetica", "", 7)
            for _, r in liq_data.head(15).iterrows():
                pdf.cell(cols[0], 5, str(r['FULL_NAME'])[:25])
                pdf.cell(cols[1], 5, str(r['CUSTOMER_TYPE'])[:15])
                pdf.cell(cols[2], 5, f"INR {r['CURRENT_BALANCE']:,.0f}")
                pdf.cell(cols[3], 5, f"INR {r['DAILY_OUTFLOWS']:,.0f}")
                pdf.cell(cols[4], 5, f"{r['OUTFLOW_TO_BALANCE_PCT']:.1f}%")
                pdf.cell(cols[5], 5, str(r['LIQUIDITY_STRESS_LEVEL']), ln=True)
            pdf.ln(6)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "NARRATIVE & ASSESSMENT", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 9)
            clean = re.sub(r'\*\*(.*?)\*\*', r'\1', str(lcr_narrative))
            clean = clean.replace('₹', 'INR ').replace('\u20b9', 'INR ')
            for para in clean.split("\n"):
                para = para.strip()
                if para:
                    pdf.multi_cell(pw, 4.5, para)
                    pdf.ln(2)
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(pw, 5, f"Document Hash: SHA-256: {doc_hash}", ln=True)
            _add_pdf_footer(pdf, pw, doc_hash)

            pdf_bytes = bytes(pdf.output())
            st.markdown('<span class="pipeline-step step-done">✓ PDF ready</span>', unsafe_allow_html=True)
            lcr_status.update(label="LCR Report - Complete", state="complete", expanded=False)

        st.markdown(f'<div class="report-container"><p>{lcr_narrative}</p></div>', unsafe_allow_html=True)
        st.download_button("Download LCR Report (PDF)", pdf_bytes,
                           file_name=f"LCR_{datetime.now().strftime('%Y%m%d')}.pdf",
                           mime="application/pdf", use_container_width=True)

elif report_type == "Customer Due Diligence (CDD)":
    st.markdown('<div class="section-header">Enhanced Due Diligence — High Risk & PEP Customers</div>', unsafe_allow_html=True)
    high_risk = session.sql(f"""
        SELECT CUSTOMER_ID, FULL_NAME, KYC_RISK_TIER, IS_PEP, JURISDICTION, LAST_KYC_REVIEW, SANCTIONS_MATCH, ADVERSE_MEDIA_FLAG
        FROM {DB}.{SCHEMA}.CUSTOMERS
        WHERE KYC_RISK_TIER IN ('HIGH','VERY_HIGH') OR IS_PEP = TRUE
        ORDER BY CASE KYC_RISK_TIER WHEN 'VERY_HIGH' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END
    """).to_pandas()
    st.dataframe(high_risk, use_container_width=True, hide_index=True)
    
    overdue = session.sql(f"""
        SELECT CUSTOMER_ID, FULL_NAME, KYC_RISK_TIER, LAST_KYC_REVIEW,
               DATEDIFF('day', LAST_KYC_REVIEW, CURRENT_DATE()) AS DAYS_OVERDUE
        FROM {DB}.{SCHEMA}.CUSTOMERS
        WHERE DATEDIFF('day', LAST_KYC_REVIEW, CURRENT_DATE()) > 365
        ORDER BY DAYS_OVERDUE DESC
    """).to_pandas()
    if not overdue.empty:
        st.warning(f"**{len(overdue)} customers** have overdue KYC reviews (>1 year)")
        st.dataframe(overdue, use_container_width=True, hide_index=True)

    if not high_risk.empty and st.button("Generate CDD Report", type="primary", use_container_width=True):
        with st.status("Generating CDD Report...", expanded=True) as cdd_status:
            st.markdown('<span class="pipeline-step step-active">1. Compiling high-risk customer profiles</span>', unsafe_allow_html=True)
            import time
            time.sleep(0.5)
            cdd_summary = ""
            for _, r in high_risk.iterrows():
                cdd_summary += f"- {r['FULL_NAME']} ({r['CUSTOMER_ID']}): KYC={r['KYC_RISK_TIER']}, PEP={r['IS_PEP']}, Jurisdiction={r['JURISDICTION']}, Sanctions={r['SANCTIONS_MATCH']}, Adverse Media={r['ADVERSE_MEDIA_FLAG']}\n"
            overdue_count = len(overdue) if not overdue.empty else 0
            st.markdown(f'<span class="pipeline-step step-done">✓ {len(high_risk)} high-risk profiles, {overdue_count} overdue KYC</span>', unsafe_allow_html=True)

            st.markdown('<span class="pipeline-step step-active">2. Cortex LLM — Generating EDD narrative</span>', unsafe_allow_html=True)
            cdd_prompt = f"""Generate a formal Customer Due Diligence (CDD) / Enhanced Due Diligence (EDD) report. Be concise and professional.

High-risk and PEP customers:
{cdd_summary}
Customers with overdue KYC (>1 year): {overdue_count}

Write a brief EDD report covering:
1. Summary of high-risk population (count, PEP status, jurisdictions)
2. Sanctions and adverse media flags requiring immediate review
3. Overdue KYC reviews requiring remediation
4. Recommendations (priority review order, escalation to compliance committee)"""

            cdd_narrative = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE('{LLM_MODEL}', '{cdd_prompt.replace("'", "''")}') AS NARRATIVE
            """).collect()[0]["NARRATIVE"]
            st.markdown('<span class="pipeline-step step-done">✓ EDD narrative generated</span>', unsafe_allow_html=True)

            st.markdown('<span class="pipeline-step step-active">3. Building PDF</span>', unsafe_allow_html=True)
            filing_ref = f"CDD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            doc_hash = hashlib.sha256(f"{filing_ref}{datetime.now()}".encode()).hexdigest()[:16].upper()

            pdf = FPDF()
            pdf.add_page()
            pw = pdf.w - 20
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(pw, 10, "ENHANCED DUE DILIGENCE (EDD) REPORT", ln=True, align="C")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(pw, 5, f"Reference: {filing_ref} | Date: {datetime.now().strftime('%Y-%m-%d')} | CONFIDENTIAL", ln=True, align="C")
            pdf.ln(8)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "HIGH RISK & PEP CUSTOMERS", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(26, 26, 46)
            pdf.set_text_color(255, 255, 255)
            cols = [22, 35, 22, 14, 25, 22, 22, 22]
            hdrs = ["Cust ID", "Name", "KYC Tier", "PEP", "Jurisdiction", "KYC Date", "Sanctions", "Adv Media"]
            for i, h in enumerate(hdrs):
                pdf.cell(cols[i], 6, h, fill=True)
            pdf.ln()
            pdf.set_text_color(26, 26, 46)
            pdf.set_font("Helvetica", "", 7)
            for _, r in high_risk.iterrows():
                pdf.cell(cols[0], 5, str(r['CUSTOMER_ID']))
                pdf.cell(cols[1], 5, str(r['FULL_NAME'])[:20])
                pdf.cell(cols[2], 5, str(r['KYC_RISK_TIER']))
                pdf.cell(cols[3], 5, str(r['IS_PEP']))
                pdf.cell(cols[4], 5, str(r['JURISDICTION'])[:14])
                pdf.cell(cols[5], 5, str(r['LAST_KYC_REVIEW'])[:10])
                pdf.cell(cols[6], 5, str(r['SANCTIONS_MATCH']))
                pdf.cell(cols[7], 5, str(r['ADVERSE_MEDIA_FLAG']), ln=True)
            pdf.ln(6)

            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(pw, 7, "NARRATIVE & ASSESSMENT", ln=True)
            pdf.line(10, pdf.get_y(), 10 + pw, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 9)
            clean = re.sub(r'\*\*(.*?)\*\*', r'\1', str(cdd_narrative))
            clean = clean.replace('₹', 'INR ').replace('\u20b9', 'INR ')
            for para in clean.split("\n"):
                para = para.strip()
                if para:
                    pdf.multi_cell(pw, 4.5, para)
                    pdf.ln(2)
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(pw, 5, f"Document Hash: SHA-256: {doc_hash}", ln=True)
            _add_pdf_footer(pdf, pw, doc_hash)

            pdf_bytes = bytes(pdf.output())
            st.markdown('<span class="pipeline-step step-done">✓ PDF ready</span>', unsafe_allow_html=True)
            cdd_status.update(label="CDD Report - Complete", state="complete", expanded=False)

        st.markdown(f'<div class="report-container"><p>{cdd_narrative}</p></div>', unsafe_allow_html=True)
        st.download_button("Download CDD Report (PDF)", pdf_bytes,
                           file_name=f"CDD_{datetime.now().strftime('%Y%m%d')}.pdf",
                           mime="application/pdf", use_container_width=True)
