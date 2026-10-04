import streamlit as st
import json
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Agent Skills", page_icon="🧊", layout="wide")
session = get_active_session()

DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"
AGENT_NAME = "RISK_COPILOT_AGENT"

with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ This Page — Powered by</div>
        <div title="Cortex Agent with multi-tool orchestration" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🤖 <strong>Cortex Agent</strong> <span style="color:#6b7280;">— Agentic AI orchestration</span>
        </div>
        <div title="Agent Skills on Snowflake Stage" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🧩 <strong>Agent Skills</strong> <span style="color:#6b7280;">— AML, Reporting, Analytics</span>
        </div>
        <div title="Cortex Analyst via Semantic View for NL-to-SQL" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>Cortex Analyst</strong> <span style="color:#6b7280;">— NL-to-SQL via SV_RISK_COPILOT</span>
        </div>
        <div title="Cortex Search for regulatory policy RAG" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🔍 <strong>Cortex Search</strong> <span style="color:#6b7280;">— Policy RAG retrieval</span>
        </div>
        <div title="Data to Chart for visual responses" style="cursor:help; padding:3px 0;">
            📈 <strong>Data to Chart</strong> <span style="color:#6b7280;">— Auto-generated visualizations</span>
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
    .skill-card {
        background: #f8fbff; border: 1px solid #e8f4fd; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 12px; transition: box-shadow 0.2s;
    }
    .skill-card:hover { box-shadow: 0 4px 12px rgba(41,181,232,0.15); }
    .skill-icon { font-size: 1.5rem; margin-right: 10px; }
    .skill-name { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
    .skill-desc { font-size: 0.82rem; color: #6b7280; margin-top: 4px; line-height: 1.5; }
    .skill-tag {
        display: inline-block; font-size: 0.65rem; font-weight: 600;
        padding: 2px 8px; border-radius: 10px; margin-right: 4px; margin-top: 8px;
    }
    .tag-tool { background: #dbeafe; color: #1d4ed8; }
    .tag-skill { background: #d1fae5; color: #065f46; }
    .tag-search { background: #fef3c7; color: #92400e; }
    .arch-box {
        background: linear-gradient(135deg, #f8fbff 0%, #eef6fd 100%);
        border: 1px solid #d1e9f9; border-radius: 12px;
        padding: 24px; margin: 16px 0; font-family: monospace; font-size: 0.78rem;
        line-height: 1.8; color: #1a1a2e;
    }
    .grounding-box {
        background: #f8fbff; border: 1px solid #e8f4fd; border-radius: 10px;
        padding: 16px 20px; margin-top: 24px;
    }
    .grounding-title { font-size: 0.75rem; font-weight: 700; color: #29B5E8; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
    .grounding-item { font-size: 0.78rem; color: #374151; padding: 3px 0; border-bottom: 1px dotted #e5e7eb; }
    .grounding-item:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <span style="font-size:1.8rem; font-weight:800; color:#1a1a2e;">🧩 Cortex Agent <span style="color:#29B5E8;">Skills</span></span>
</div>
<p style="color:#6b7280; margin-top:0;">Snowflake-native agentic AI — the Risk Copilot Agent uses Skills for domain-specific compliance workflows, Cortex Analyst for data queries, and Cortex Search for regulatory policy retrieval.</p>
""", unsafe_allow_html=True)

# --- Architecture Diagram ---
st.markdown('<div class="section-header">Agent Architecture</div>', unsafe_allow_html=True)

arch_counts = session.sql(f"""
    SELECT
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.CUSTOMERS) AS c,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ACCOUNTS) AS a,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.TRANSACTIONS) AS t,
        (SELECT COUNT(*) FROM {DB}.{SCHEMA}.ALERTS) AS al
""").collect()[0]

st.markdown(f"""
<div style="max-width:720px; margin:0 auto 24px;">

  <!-- Agent (top) -->
  <div style="background:linear-gradient(135deg,#1a1a2e,#29B5E8); color:#fff; border-radius:14px; padding:18px 24px; text-align:center; box-shadow:0 4px 16px rgba(41,181,232,0.25);">
    <div style="font-size:1.3rem; font-weight:800;">🧊 RISK_COPILOT_AGENT</div>
    <div style="font-size:0.8rem; opacity:0.9; margin-top:4px;">Cortex Agent &nbsp;·&nbsp; Orchestrator &nbsp;·&nbsp; Model: auto</div>
    <div style="font-size:0.7rem; opacity:0.7; margin-top:2px;">Plan → Execute → Reflect → Respond</div>
  </div>

  <!-- Connector line -->
  <div style="display:flex; justify-content:center;"><div style="width:2px; height:20px; background:#29B5E8;"></div></div>

  <!-- Three pillars -->
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
    <!-- Skills -->
    <div style="background:#d1fae5; border:1px solid #6ee7b7; border-radius:10px; padding:14px; text-align:center;">
      <div style="font-size:1.1rem;">🧩</div>
      <div style="font-size:0.82rem; font-weight:700; color:#065f46; margin:4px 0;">SKILLS (3)</div>
      <div style="font-size:0.72rem; color:#065f46; line-height:1.6; text-align:left;">
        • AML Investigation<br>• Regulatory Reporting<br>• Risk Analytics
      </div>
    </div>
    <!-- Tools -->
    <div style="background:#dbeafe; border:1px solid #93c5fd; border-radius:10px; padding:14px; text-align:center;">
      <div style="font-size:1.1rem;">🔧</div>
      <div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin:4px 0;">TOOLS (3)</div>
      <div style="font-size:0.72rem; color:#1e40af; line-height:1.6; text-align:left;">
        • Cortex Analyst<br>• Cortex Search<br>• Data to Chart
      </div>
    </div>
    <!-- Instructions -->
    <div style="background:#fef3c7; border:1px solid #fcd34d; border-radius:10px; padding:14px; text-align:center;">
      <div style="font-size:1.1rem;">📋</div>
      <div style="font-size:0.82rem; font-weight:700; color:#92400e; margin:4px 0;">INSTRUCTIONS</div>
      <div style="font-size:0.72rem; color:#92400e; line-height:1.6; text-align:left;">
        • Response style<br>• Evidence citing<br>• INR formatting
      </div>
    </div>
  </div>

  <!-- Connector line -->
  <div style="display:flex; justify-content:center;"><div style="width:2px; height:20px; background:#29B5E8;"></div></div>

  <!-- Tool Resources -->
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
    <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; padding:14px; text-align:center;">
      <div style="font-size:0.82rem; font-weight:700; color:#0c4a6e;">📊 SV_RISK_COPILOT</div>
      <div style="font-size:0.7rem; color:#0c4a6e; margin-top:4px;">Semantic View &nbsp;·&nbsp; Cortex Analyst</div>
      <div style="font-size:0.68rem; color:#6b7280; margin-top:4px;">4 tables &nbsp;·&nbsp; 35 dimensions &nbsp;·&nbsp; 9 metrics</div>
    </div>
    <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; padding:14px; text-align:center;">
      <div style="font-size:0.82rem; font-weight:700; color:#0c4a6e;">🔍 POLICY_SEARCH_SERVICE</div>
      <div style="font-size:0.7rem; color:#0c4a6e; margin-top:4px;">Cortex Search &nbsp;·&nbsp; RAG Retrieval</div>
      <div style="font-size:0.68rem; color:#6b7280; margin-top:4px;">10 regulatory docs &nbsp;·&nbsp; PMLA, RBI, FATF, Basel</div>
    </div>
  </div>

  <!-- Connector line -->
  <div style="display:flex; justify-content:center;"><div style="width:2px; height:20px; background:#29B5E8;"></div></div>

  <!-- Data Layer -->
  <div style="background:#1a1a2e; border-radius:10px; padding:14px 20px; text-align:center;">
    <div style="font-size:0.75rem; font-weight:700; color:#29B5E8; letter-spacing:1px; margin-bottom:8px;">SNOWFLAKE DATA LAYER</div>
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:8px;">
      <div style="background:#29B5E820; border-radius:6px; padding:8px;">
        <div style="font-size:0.75rem; font-weight:600; color:#fff;">CUSTOMERS</div>
        <div style="font-size:0.65rem; color:#94a3b8;">{arch_counts['C']:,} customers</div>
      </div>
      <div style="background:#29B5E820; border-radius:6px; padding:8px;">
        <div style="font-size:0.75rem; font-weight:600; color:#fff;">ACCOUNTS</div>
        <div style="font-size:0.65rem; color:#94a3b8;">{arch_counts['A']:,} accounts</div>
      </div>
      <div style="background:#29B5E820; border-radius:6px; padding:8px;">
        <div style="font-size:0.75rem; font-weight:600; color:#fff;">TRANSACTIONS</div>
        <div style="font-size:0.65rem; color:#94a3b8;">{arch_counts['T']:,} txns</div>
      </div>
      <div style="background:#29B5E820; border-radius:6px; padding:8px;">
        <div style="font-size:0.75rem; font-weight:600; color:#fff;">ALERTS</div>
        <div style="font-size:0.65rem; color:#94a3b8;">{arch_counts['AL']:,} alerts</div>
      </div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# --- Skills Catalog ---
st.markdown('<div class="section-header">Skills Catalog</div>', unsafe_allow_html=True)

skills = [
    {
        "icon": "🔍",
        "name": "AML Investigation",
        "desc": "End-to-end AML investigation workflow — customer risk profiling, transaction pattern analysis, alert triage, and STR/SAR filing recommendations. Follows a 5-step process from customer KYC review through regulatory assessment.",
        "tags": [("Cortex Analyst", "tag-tool"), ("Cortex Search", "tag-search"), ("Skill", "tag-skill")],
        "prompts": ["Investigate customer CUST003 for AML concerns", "Should we file an STR for Offshore Holdings Ltd?", "What suspicious patterns exist for high-risk corporate accounts?"]
    },
    {
        "icon": "📋",
        "name": "Regulatory Reporting",
        "desc": "Generates formal regulatory compliance reports — STR (Suspicious Transaction Report), CTR (Cash Transaction Report), LCR (Liquidity Coverage Ratio), and CDD/EDD (Customer Due Diligence). Structures output per FIU-IND and RBI guidelines.",
        "tags": [("Cortex Search", "tag-search"), ("Cortex Analyst", "tag-tool"), ("Skill", "tag-skill")],
        "prompts": ["Generate a CTR report for accounts exceeding INR 10 lakh", "Prepare an LCR assessment for Basel III compliance", "Which customers need enhanced due diligence reports?"]
    },
    {
        "icon": "📊",
        "name": "Risk Analytics",
        "desc": "Executive-level risk intelligence — portfolio health scoring (0-100), daily trend analysis, risk concentration identification, and CRO-ready executive briefs with specific metrics and actionable recommendations.",
        "tags": [("Cortex Analyst", "tag-tool"), ("Data to Chart", "tag-tool"), ("Skill", "tag-skill")],
        "prompts": ["Give me a portfolio health score", "What are the top risk concentrations?", "Executive brief on current risk posture"]
    }
]

for skill in skills:
    tags_html = "".join(f'<span class="skill-tag {t[1]}">{t[0]}</span>' for t in skill["tags"])
    st.markdown(f"""
    <div class="skill-card">
        <div style="display:flex; align-items:center;">
            <span class="skill-icon">{skill["icon"]}</span>
            <span class="skill-name">{skill["name"]}</span>
        </div>
        <div class="skill-desc">{skill["desc"]}</div>
        <div>{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Interactive Agent Chat ---
st.markdown('<div class="section-header">Talk to the Agent</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px 14px; margin-bottom:16px;">
    <span style="font-size:0.8rem; color:#92400e;">
        <strong>How it works:</strong> Your question goes to the Cortex Agent, which autonomously decides whether to use 
        Cortex Analyst (data queries), Cortex Search (regulatory policies), or a Skill (investigation/reporting workflow) 
        — then combines the results into a single governed response.
    </span>
</div>
""", unsafe_allow_html=True)

# Suggested prompts
st.caption("Try a suggested prompt:")
prompt_cols = st.columns(3)
suggested = [
    "Investigate CUST007 for AML risk",
    "What is the portfolio health score?",
    "Which regulations apply to structuring?"
]
selected_prompt = None
for i, prompt in enumerate(suggested):
    with prompt_cols[i]:
        if st.button(prompt, key=f"suggest_{i}", use_container_width=True):
            selected_prompt = prompt

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

for msg in st.session_state.agent_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask the Risk Copilot Agent...") or selected_prompt

if user_input:
    st.session_state.agent_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.status("Agent reasoning...", expanded=True) as agent_status:
            st.markdown('<span style="font-size:0.8rem; color:#6b7280;">Routing to Cortex Agent with Skills...</span>', unsafe_allow_html=True)

            try:
                import _snowflake
                body = json.dumps({
                    "messages": [{"role": "user", "content": [{"type": "text", "text": user_input}]}],
                    "agent": f"{DB}.{SCHEMA}.{AGENT_NAME}"
                })
                response = _snowflake.send_snow_api_request(
                    "POST", "/api/v2/cortex/agent:run", {}, {}, body, {}, 60000
                )
                resp_content = json.loads(response.get("content", "{}"))

                answer_parts = []
                tools_used = []
                for msg in resp_content.get("messages", []):
                    for block in msg.get("content", []):
                        if block.get("type") == "text":
                            answer_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            tools_used.append(block.get("name", "unknown"))
                        elif block.get("type") == "tool_results":
                            for result in block.get("content", []):
                                if result.get("type") == "text":
                                    answer_parts.append(result.get("text", ""))

                answer = "\n\n".join(answer_parts) if answer_parts else "The agent processed your request but returned no text content."

                if tools_used:
                    st.markdown(f'<span style="font-size:0.75rem; color:#29B5E8;">Tools used: {", ".join(tools_used)}</span>', unsafe_allow_html=True)

                agent_status.update(label="Agent complete", state="complete", expanded=False)

            except ImportError:
                # Fallback: use Cortex Complete with skill-aware prompt
                skill_context = """You are the CoCoIceberg Risk Copilot Agent with 3 skills:
1. AML Investigation: customer profiling, transaction analysis, alert triage, STR/SAR recommendations
2. Regulatory Reporting: STR, CTR, LCR, CDD/EDD report generation per PMLA/RBI/FATF
3. Risk Analytics: portfolio health scoring, trend analysis, risk concentration, executive briefs

You also have access to:
- Cortex Analyst (SV_RISK_COPILOT semantic view with CUSTOMERS, ACCOUNTS, TRANSACTIONS, ALERTS)
- Cortex Search (POLICY_SEARCH_SERVICE with 10 regulatory policy documents)"""

                # Get relevant data based on the question
                data_context = ""
                try:
                    top_risks = session.sql(f"""
                        SELECT FULL_NAME, CUSTOMER_TYPE, KYC_RISK_TIER, COMPOSITE_AML_SCORE, CRITICAL_ALERTS, RECOMMENDED_ACTION
                        FROM {DB}.{SCHEMA}.V_AML_SCORING ORDER BY COMPOSITE_AML_SCORE DESC LIMIT 5
                    """).collect()
                    data_context = "Top AML risks:\n" + "\n".join(
                        f"- {r['FULL_NAME']}: AML={r['COMPOSITE_AML_SCORE']}, Type={r['CUSTOMER_TYPE']}, Tier={r['KYC_RISK_TIER']}, Action={r['RECOMMENDED_ACTION']}"
                        for r in top_risks
                    )

                    alert_summary = session.sql(f"""
                        SELECT ALERT_CATEGORY, SEVERITY, COUNT(*) AS CNT
                        FROM {DB}.{SCHEMA}.ALERTS WHERE STATUS != 'CLOSED'
                        GROUP BY ALERT_CATEGORY, SEVERITY ORDER BY CNT DESC
                    """).collect()
                    data_context += "\n\nOpen alerts:\n" + "\n".join(
                        f"- {r['ALERT_CATEGORY']} {r['SEVERITY']}: {r['CNT']}" for r in alert_summary
                    )

                    portfolio = session.sql(f"""
                        SELECT COUNT(DISTINCT c.CUSTOMER_ID) AS customers,
                               SUM(a.CURRENT_BALANCE) AS aum,
                               COUNT(CASE WHEN a.NPA_STATUS != 'STANDARD' THEN 1 END) AS npa_count
                        FROM {DB}.{SCHEMA}.CUSTOMERS c
                        JOIN {DB}.{SCHEMA}.ACCOUNTS a ON c.CUSTOMER_ID = a.CUSTOMER_ID
                    """).collect()[0]
                    data_context += f"\n\nPortfolio: {portfolio['CUSTOMERS']} customers, AUM INR {(portfolio['AUM'] or 0)/10000000:.0f} Cr, {portfolio['NPA_COUNT']} NPA accounts"
                except Exception:
                    pass

                prompt = f"""{skill_context}

DATA CONTEXT:
{data_context}

USER QUESTION: {user_input}

Respond as if you are the Cortex Agent using the appropriate skill. Be concise, cite specific data, and structure your response with clear sections."""

                escaped = prompt.replace("'", "''")
                result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', '{escaped}') AS response
                """).collect()
                answer = result[0]["RESPONSE"]
                agent_status.update(label="Agent complete", state="complete", expanded=False)

            except Exception as e:
                answer = f"Agent encountered an error: {str(e)[:200]}"
                agent_status.update(label="Agent error", state="error", expanded=False)

        st.markdown(answer)
        st.session_state.agent_messages.append({"role": "assistant", "content": answer})

# --- How Skills Work ---
st.markdown('<div class="section-header">How Cortex Agent Skills Work</div>', unsafe_allow_html=True)

col_how1, col_how2 = st.columns(2)
with col_how1:
    st.markdown("""
    **Snowflake-Native Architecture:**
    - Skills are `SKILL.md` files stored on a **Snowflake Stage**
    - The agent discovers skills automatically via stage scanning
    - No external infrastructure — everything runs inside Snowflake
    - Skills are versioned, shareable, and governed by RBAC
    """)
with col_how2:
    st.markdown("""
    **Agent Orchestration Loop:**
    1. **Plan** — Agent parses the query, selects tools & skills
    2. **Execute** — Calls Cortex Analyst, Search, or runs a skill
    3. **Reflect** — Evaluates results, decides if more steps needed
    4. **Respond** — Combines evidence into a governed answer
    """)

# --- Grounding ---
st.markdown(f"""
<div class="grounding-box">
    <div class="grounding-title">Data Grounding — Snowflake-Native AI Stack</div>
    <div class="grounding-item">🤖 <strong>{DB}.{SCHEMA}.RISK_COPILOT_AGENT</strong> — Cortex Agent with multi-tool orchestration (CREATE AGENT)</div>
    <div class="grounding-item">🧩 <strong>@{DB}.{SCHEMA}.SKILL_STAGE/skills/</strong> — 3 Agent Skills: AML Investigation, Regulatory Reporting, Risk Analytics</div>
    <div class="grounding-item">📊 <strong>{DB}.{SCHEMA}.SV_RISK_COPILOT</strong> — Semantic View powering Cortex Analyst (NL-to-SQL)</div>
    <div class="grounding-item">🔍 <strong>{DB}.{SCHEMA}.POLICY_SEARCH_SERVICE</strong> — Cortex Search for regulatory policy RAG</div>
    <div class="grounding-item">📈 <strong>Data to Chart</strong> — Cortex Agent built-in tool for auto-generated visualizations</div>
    <div class="grounding-item">⚡ <strong>Model: auto</strong> — Snowflake automatically selects the best available LLM for orchestration</div>
</div>
""", unsafe_allow_html=True)
