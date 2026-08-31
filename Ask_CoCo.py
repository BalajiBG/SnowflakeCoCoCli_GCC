import streamlit as st
import json
import _snowflake
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CoCoIceberg | Ask CoCo", page_icon="🧊", layout="wide", initial_sidebar_state="expanded")

session = get_active_session()

# --- Constants ---
DB = "RISK_COPILOT_DB"
SCHEMA = "RISK_COPILOT"
LLM_MODEL = "llama3.1-70b"
SEARCH_SERVICE = "POLICY_SEARCH_SERVICE"
SEMANTIC_VIEW = "RISK_COPILOT_DB.RISK_COPILOT.SV_RISK_COPILOT"

# --- Modern UI Styling ---
st.markdown("""
<style>
    /* Global */
    .stApp { background-color: #ffffff; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    section[data-testid="stSidebar"] { background-color: #f8fbff; border-right: 1px solid #e8f4fd; }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0rem; }
    [data-testid="stSidebarNav"] { padding-top: 0rem; }
    
    /* Typography */
    h1, h2, h3 { color: #1a1a2e; font-weight: 700; }
    .brand-header {
        display: flex; align-items: center; gap: 12px;
        padding: 0; margin-bottom: 4px;
    }
    .brand-title {
        font-size: 2rem; font-weight: 800; color: #1a1a2e;
        letter-spacing: -0.5px;
    }
    .brand-title span { color: #29B5E8; }
    .brand-tagline {
        font-size: 0.95rem; color: #6b7280; font-weight: 400;
        margin: 0; padding: 0;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 20px; text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .kpi-card:hover { box-shadow: 0 4px 12px rgba(41,181,232,0.12); }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1a1a2e; }
    .kpi-label { font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
    .kpi-critical .kpi-value { color: #dc2626; }
    .kpi-warning .kpi-value { color: #f59e0b; }
    .kpi-info .kpi-value { color: #29B5E8; }
    
    /* Chat Messages */
    .stChatMessage { border-radius: 12px; }
    [data-testid="stChatMessageContent"] { font-size: 0.95rem; line-height: 1.6; }
    
    /* Status/Pipeline */
    .pipeline-step {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.8rem;
        font-weight: 500; margin-right: 8px;
    }
    .step-active { background: #e8f4fd; color: #0c7cd5; border: 1px solid #29B5E8; }
    .step-done { background: #ecfdf5; color: #059669; border: 1px solid #6ee7b7; }
    .step-pending { background: #f9fafb; color: #9ca3af; border: 1px solid #e5e7eb; }
    
    /* Evidence Panel */
    .evidence-panel {
        background: #f8fbff; border: 1px solid #e8f4fd;
        border-radius: 12px; padding: 20px; margin-top: 16px;
    }
    .confidence-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    }
    .conf-high { background: #ecfdf5; color: #059669; }
    .conf-medium { background: #fffbeb; color: #d97706; }
    .conf-low { background: #fef2f2; color: #dc2626; }
    
    /* Sidebar Buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: #f8fbff; border: 1px solid #e8f4fd;
        color: #1a1a2e; font-size: 0.82rem; text-align: left;
        border-radius: 8px; padding: 10px 14px;
        transition: all 0.15s;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #e8f4fd; border-color: #29B5E8;
    }
    
    /* Expander */
    .streamlit-expanderHeader { font-weight: 600; color: #1a1a2e; }
    
    /* Hide default streamlit footer */
    footer { display: none; }
    #MainMenu { visibility: hidden; }
</style>
<script>
    window.addEventListener('load', function() {
        window.scrollTo(0, 0);
    });
</script>
""", unsafe_allow_html=True)

st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

# --- Core Engine ---

def classify_intent(question):
    """Semantic intent classification using AI_CLASSIFY."""
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.AI_CLASSIFY(
            '{question.replace("'", "''")}',
            ['FRAUD_AND_AML', 'CREDIT_RISK', 'LIQUIDITY_RISK', 'REGULATORY_POLICY', 'REPORT_GENERATION', 'GENERAL_INQUIRY']
        ) AS intent
    """).collect()
    intent_json = json.loads(result[0]["INTENT"])
    return intent_json.get("labels", ["GENERAL_INQUIRY"])[0]


def query_analyst(question):
    """Query Cortex Analyst using the semantic view."""
    body = json.dumps({
        "messages": [{"role": "user", "content": [{"type": "text", "text": question}]}],
        "semantic_view": SEMANTIC_VIEW
    })
    try:
        response = _snowflake.send_snow_api_request(
            "POST", "/api/v2/cortex/analyst/message", {}, {}, body, {}, 30000
        )
        resp_json = json.loads(response["content"])
        for msg in resp_json.get("messages", []):
            for block in msg.get("content", []):
                if block.get("type") == "sql":
                    return {"sql": block.get("statement", ""), "explanation": block.get("explanation", ""), "success": True}
                elif block.get("type") == "text":
                    text = block.get("text", "")
                    if "```sql" in text:
                        sql = text.split("```sql")[1].split("```")[0].strip()
                        return {"sql": sql, "explanation": text.split("```sql")[0].strip(), "success": True}
                    return {"sql": "", "explanation": text, "success": False}
        return {"sql": "", "explanation": "No response from analyst", "success": False}
    except Exception as e:
        return {"sql": "", "explanation": str(e), "success": False}


def search_policies(query, limit=3):
    """Search regulatory policies using Cortex Search."""
    result = session.sql(f"""
        SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                '{DB}.{SCHEMA}.{SEARCH_SERVICE}',
                '{{"query": "{query.replace(chr(39), chr(39)+chr(39))}", "columns": ["CONTENT","REGULATION_NAME","SECTION_TITLE","CATEGORY"], "limit": {limit}}}'
            )
        )['results'] AS results
    """).collect()
    if result and result[0]["RESULTS"]:
        return json.loads(result[0]["RESULTS"])
    return []


def execute_sql_safely(sql):
    """Execute SQL with error handling."""
    try:
        clean_sql = sql.replace("-- Generated by Cortex Analyst", "").strip().rstrip(";")
        df = session.sql(clean_sql).collect()
        return [row.as_dict() for row in df], None
    except Exception as e:
        return [], str(e)


def assess_confidence(sql_result, policy_results, intent):
    """Assess answer confidence based on evidence."""
    has_data = len(sql_result) > 0
    has_policy = len(policy_results) > 0
    if intent == "REGULATORY_POLICY":
        return ("HIGH", "Grounded in regulatory source documents") if has_policy else ("LOW", "No matching regulatory documents found")
    if has_data and has_policy:
        return "HIGH", "Supported by data evidence and regulatory context"
    elif has_data:
        return "MEDIUM", "Data evidence found; no regulatory citation applicable"
    return "LOW", "Query returned no matching data"


def generate_governed_answer(question, intent, sql_result, policy_results, confidence_level, confidence_reason, analyst_explanation=""):
    """Generate a governed, explainable answer with evidence citations and conversation context."""
    data_summary = json.dumps(sql_result[:8], default=str) if sql_result else "No data found"
    policy_context = ""
    if policy_results:
        for p in policy_results:
            policy_context += f"\n- [{p.get('REGULATION_NAME','')}, {p.get('SECTION_TITLE','')}]: {p.get('CONTENT','')[:400]}"

    # Build conversation history for context retention (last 6 messages)
    conversation_history = ""
    recent_msgs = st.session_state.messages[-6:] if len(st.session_state.messages) > 0 else []
    if recent_msgs:
        conversation_history = "\nPREVIOUS CONVERSATION (for context):\n"
        for msg in recent_msgs:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_history += f"{role}: {msg['content'][:300]}\n"

    prompt = f"""You are a senior compliance officer AI copilot. Be CONCISE and DIRECT.

RULES:
- Maximum 2-3 sentences per section. No filler words.
- Use bullet points, not paragraphs.
- Cite specific numbers: amounts, dates, IDs, scores.
- If evidence is insufficient, say so in one line.
- If the user refers to prior conversation, use context below.
{conversation_history}
QUERY: {question}
Intent: {intent} | Confidence: {confidence_level}
Analyst: {analyst_explanation}

DATA:
{data_summary}

REGULATION:{policy_context if policy_context else ' None.'}

Respond in EXACTLY this format (keep each section to 2-4 bullet points max):

**🎯 Finding**
• [One clear sentence answering the question]
• [Key data point if needed]

**📋 Evidence**
• [Specific: TXN_ID / amount / date / name / score]
• [Another data point]
• [Max 4 bullets]

**⚖️ Regulatory Basis**
• [Regulation name + section, or "N/A — operational query"]

**➡️ Action Required**
• [One concrete next step]
• [Second step if needed]"""

    escaped = prompt.replace("'", "''")
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE('{LLM_MODEL}', '{escaped}') AS response
    """).collect()
    return result[0]["RESPONSE"]


# --- Header ---
st.markdown("""
<div class="brand-header">
    <div>
        <div class="brand-title">🧊 CoCo<span>Iceberg</span></div>
        <div class="brand-tagline">Cortex-powered copilot surfacing hidden fraud, liquidity & regulatory risk</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Chat History Management ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.active_session_id = "default"
    st.session_state.chat_sessions["default"] = {"name": "New Chat", "messages": [], "created": datetime.now().strftime("%b %d, %H:%M")}
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.chat_sessions.get(st.session_state.get("active_session_id", "default"), {}).get("messages", [])

def get_active_messages():
    sid = st.session_state.active_session_id
    return st.session_state.chat_sessions.get(sid, {}).get("messages", [])

def save_active_messages():
    sid = st.session_state.active_session_id
    st.session_state.chat_sessions[sid]["messages"] = st.session_state.messages

def create_new_chat():
    import time
    # Always allow new chat if current has messages
    current_sid = st.session_state.active_session_id
    current_msgs = st.session_state.chat_sessions[current_sid]["messages"]
    if not current_msgs:
        return  # Already on an empty chat, no need to create another
    
    # Save current chat first
    save_active_messages()
    new_id = f"chat_{int(time.time())}"
    st.session_state.chat_sessions[new_id] = {"name": "New Chat", "messages": [], "created": datetime.now().strftime("%b %d, %H:%M")}
    st.session_state.active_session_id = new_id
    st.session_state.messages = []

def switch_chat(session_id):
    save_active_messages()
    st.session_state.active_session_id = session_id
    st.session_state.messages = st.session_state.chat_sessions[session_id]["messages"]

def auto_name_chat(messages):
    if messages and len(messages) >= 1:
        first_msg = messages[0]["content"]
        return first_msg[:40] + ("..." if len(first_msg) > 40 else "")
    return "New Chat"

# --- Sidebar (Conversations + Powered by only) ---
with st.sidebar:
    # Chat History Section
    st.markdown("### Conversations")
    
    # List previous chats (only show chats that have messages)
    chats_with_messages = {sid: data for sid, data in st.session_state.chat_sessions.items() if data["messages"]}
    for sid, chat_data in sorted(chats_with_messages.items(), key=lambda x: x[1].get("created", ""), reverse=True):
        chat_name = auto_name_chat(chat_data["messages"])
        is_active = sid == st.session_state.active_session_id
        msg_count = len([m for m in chat_data["messages"] if m["role"] == "user"])
        
        btn_label = f"{'→ ' if is_active else ''}{chat_name}"
        if msg_count > 0:
            btn_label += f" ({msg_count})"
        
        if st.button(btn_label, key=f"chat_{sid}", use_container_width=True, disabled=is_active):
            switch_chat(sid)
            st.rerun()
    
    if not chats_with_messages:
        st.caption("No conversations yet. Ask a question to start.")
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">📑 Pages — Powered By</div>
        <div title="Cortex Analyst (NL-to-SQL via Semantic View), AI_CLASSIFY (intent routing), Cortex Search (policy RAG), Cortex Complete (governed LLM)" style="cursor:help; padding:4px 0; border-bottom:1px dotted #e5e7eb;">
            💬 <strong>Ask CoCo</strong> <span style="color:#6b7280;">— Analyst + AI_CLASSIFY + Search + Complete</span>
        </div>
        <div title="Cortex Analyst for NL-to-SQL queries on AML scoring view, Dynamic Tables for real-time composite risk scores, Semantic View for data ontology" style="cursor:help; padding:4px 0; border-bottom:1px dotted #e5e7eb;">
            🚨 <strong>AML Fraud</strong> <span style="color:#6b7280;">— Cortex Analyst + Dynamic Tables + Semantic View</span>
        </div>
        <div title="Cortex Analyst for credit risk queries, V_CREDIT_RISK dynamic table for NPA scoring" style="cursor:help; padding:4px 0; border-bottom:1px dotted #e5e7eb;">
            💳 <strong>Credit Risk</strong> <span style="color:#6b7280;">— Cortex Analyst + Dynamic Tables</span>
        </div>
        <div title="Cortex Analyst for liquidity queries, V_LIQUIDITY_RISK dynamic table for LCR computation" style="cursor:help; padding:4px 0; border-bottom:1px dotted #e5e7eb;">
            💧 <strong>Liquidity Risk</strong> <span style="color:#6b7280;">— Cortex Analyst + Dynamic Tables</span>
        </div>
        <div title="Cortex Analyst for velocity anomaly detection, Dynamic Tables for real-time velocity scoring" style="cursor:help; padding:4px 0; border-bottom:1px dotted #e5e7eb;">
            ⚡ <strong>Velocity Anomalies</strong> <span style="color:#6b7280;">— Cortex Analyst + Dynamic Tables</span>
        </div>
        <div title="Cortex Complete (AI investigation reports), V_AML_SCORING (composite risk), MCP Jira integration (ticket creation), Cross-table SQL evidence joins" style="cursor:help; padding:4px 0; border-bottom:1px dotted #e5e7eb;">
            🔍 <strong>Investigation</strong> <span style="color:#6b7280;">— Cortex Complete + MCP (Jira) + SQL Joins</span>
        </div>
        <div title="Cortex Complete (regulatory narratives), Cortex Search (policy citation retrieval), AI_PARSE_DOCUMENT (doc processing), SHA-256 document authentication" style="cursor:help; padding:4px 0;">
            📝 <strong>Report Generator</strong> <span style="color:#6b7280;">— Complete + Search + Document AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.7rem; padding: 8px 0;">
        <div style="color:#29B5E8; font-weight:700; margin-bottom:6px;">⚡ Snowflake Features Used</div>
        <div title="AI_CLASSIFY semantic intent routing" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🧠 <strong>AI_CLASSIFY</strong> <span style="color:#6b7280;">— Semantic intent routing</span>
        </div>
        <div title="Cortex Analyst NL-to-SQL via Semantic View" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📊 <strong>Cortex Analyst</strong> <span style="color:#6b7280;">— NL→SQL (Semantic View)</span>
        </div>
        <div title="Cortex Search RAG over regulatory policy documents" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🔍 <strong>Cortex Search</strong> <span style="color:#6b7280;">— Policy RAG retrieval</span>
        </div>
        <div title="CORTEX.COMPLETE with governance guardrails" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🤖 <strong>Cortex Complete</strong> <span style="color:#6b7280;">— Governed LLM answers</span>
        </div>
        <div title="Dynamic Tables for real-time risk signal computation" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            ⚡ <strong>Dynamic Tables</strong> <span style="color:#6b7280;">— Real-time pipelines</span>
        </div>
        <div title="Semantic View with measures, dimensions, relationships" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🏗️ <strong>Semantic View</strong> <span style="color:#6b7280;">— Data ontology</span>
        </div>
        <div title="Streamlit-in-Snowflake deployment" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            📱 <strong>Streamlit in Snowflake</strong> <span style="color:#6b7280;">— App hosting</span>
        </div>
        <div title="MCP Server integration with Jira for ticket creation" style="cursor:help; padding:3px 0; border-bottom:1px dotted #e5e7eb;">
            🔗 <strong>MCP (Jira)</strong> <span style="color:#6b7280;">— External tool actions</span>
        </div>
        <div title="AI_PARSE_DOCUMENT and AI_EXTRACT for unstructured processing" style="cursor:help; padding:3px 0;">
            📄 <strong>Document AI</strong> <span style="color:#6b7280;">— Unstructured processing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Chat Interface ---

# New Chat button — always at top when messages exist
if st.session_state.messages:
    if st.button("+ New Chat", key="new_chat_main"):
        create_new_chat()
        st.rerun()

# Quick Questions (shown only when no messages)
if not st.session_state.messages:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%); border: 1px solid #e0edff; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px;">
        <div style="text-align:center; margin-bottom:14px;">
            <span style="font-size:0.75rem; font-weight:700; color:#29B5E8; letter-spacing:1.5px; text-transform:uppercase;">Multi-Agent AI Pipeline</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:center; gap:0; flex-wrap:wrap;">
            <div style="text-align:center; padding:8px 12px;">
                <div style="background:#29B5E8; color:white; border-radius:8px; padding:6px 10px; font-size:0.7rem; font-weight:700; white-space:nowrap;">1. AI_CLASSIFY</div>
                <div style="font-size:0.6rem; color:#6b7280; margin-top:3px;">Intent Routing</div>
            </div>
            <div style="color:#29B5E8; font-size:1.2rem; font-weight:bold;">→</div>
            <div style="text-align:center; padding:8px 12px;">
                <div style="background:#0c7cd5; color:white; border-radius:8px; padding:6px 10px; font-size:0.7rem; font-weight:700; white-space:nowrap;">2. CORTEX ANALYST</div>
                <div style="font-size:0.6rem; color:#6b7280; margin-top:3px;">NL → SQL</div>
            </div>
            <div style="color:#29B5E8; font-size:1.2rem; font-weight:bold;">→</div>
            <div style="text-align:center; padding:8px 12px;">
                <div style="background:#1a1a2e; color:white; border-radius:8px; padding:6px 10px; font-size:0.7rem; font-weight:700; white-space:nowrap;">3. CORTEX SEARCH</div>
                <div style="font-size:0.6rem; color:#6b7280; margin-top:3px;">Policy RAG</div>
            </div>
            <div style="color:#29B5E8; font-size:1.2rem; font-weight:bold;">→</div>
            <div style="text-align:center; padding:8px 12px;">
                <div style="background:#f59e0b; color:white; border-radius:8px; padding:6px 10px; font-size:0.7rem; font-weight:700; white-space:nowrap;">4. CONFIDENCE</div>
                <div style="font-size:0.6rem; color:#6b7280; margin-top:3px;">Evidence Score</div>
            </div>
            <div style="color:#29B5E8; font-size:1.2rem; font-weight:bold;">→</div>
            <div style="text-align:center; padding:8px 12px;">
                <div style="background:#059669; color:white; border-radius:8px; padding:6px 10px; font-size:0.7rem; font-weight:700; white-space:nowrap;">5. GOVERNED LLM</div>
                <div style="font-size:0.6rem; color:#6b7280; margin-top:3px;">Synthesize Answer</div>
            </div>
        </div>
        <div style="text-align:center; margin-top:10px; font-size:0.65rem; color:#9ca3af;">
            Each query flows through all 5 agents with handoffs — watch the live status below as you ask a question
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding: 0 0 10px;">
        <div style="font-size:1.2rem; font-weight:600; color:#1a1a2e;">What can I help you investigate?</div>
        <div style="font-size:0.9rem; color:#6b7280; margin-top:4px;">Ask about fraud signals, risk exposure, regulatory policy, or generate compliance reports.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick question chips in the main area
    samples = [
        "Which customers have the highest AML risk scores?",
        "Are there signs of cash structuring?",
        "What does RBI mandate for STR filing?",
        "Show accounts at risk of NPA",
        "Explain the round-tripping pattern for Shell Holdings",
        "What is the liquidity stress across our portfolio?",
    ]
    qcol1, qcol2 = st.columns(2)
    for i, s in enumerate(samples):
        with qcol1 if i % 2 == 0 else qcol2:
            if st.button(s, key=f"q_{s}", use_container_width=True):
                st.session_state["user_question"] = s
                st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧊" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about fraud, risk, compliance, or regulations...")

if "user_question" in st.session_state:
    user_input = st.session_state.pop("user_question")

if user_input:
    # --- Guardrail: Input Validation ---
    user_input_clean = user_input.strip()
    if len(user_input_clean) < 5:
        st.warning("Please enter a more specific question (at least 5 characters).")
    elif len(user_input_clean) > 2000:
        st.warning("Question too long. Please keep it under 2000 characters.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input_clean})
        save_active_messages()
        with st.chat_message("user"):
            st.markdown(user_input_clean)

        with st.chat_message("assistant", avatar="🧊"):
            # Processing Pipeline
            try:
                with st.status("Processing your query...", expanded=True) as status:
                    # Step 1
                    st.markdown('<span class="pipeline-step step-active">1. Understanding Intent</span>', unsafe_allow_html=True)
                    intent = classify_intent(user_input_clean)
                    intent_display = intent.replace("_", " ").title()
                    st.markdown(f'<span class="pipeline-step step-done">✓ {intent_display}</span>', unsafe_allow_html=True)
                    
                    # Step 2
                    st.markdown('<span class="pipeline-step step-active">2. Cortex Analyst (NL→SQL)</span>', unsafe_allow_html=True)
                    analyst_result = query_analyst(user_input_clean)
                    sql_result = []
                    generated_sql = ""
                    analyst_explanation = analyst_result.get("explanation", "")
                    
                    if analyst_result["success"] and analyst_result["sql"]:
                        generated_sql = analyst_result["sql"]
                        sql_result, sql_error = execute_sql_safely(generated_sql)
                        if sql_error:
                            st.caption(f"Note: {sql_error[:80]}")
                        st.markdown(f'<span class="pipeline-step step-done">✓ {len(sql_result)} rows</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="pipeline-step step-pending">○ No SQL needed</span>', unsafe_allow_html=True)
                    
                    # Step 3
                    st.markdown('<span class="pipeline-step step-active">3. Regulatory Search</span>', unsafe_allow_html=True)
                    policy_results = search_policies(user_input_clean)
                    st.markdown(f'<span class="pipeline-step step-done">✓ {len(policy_results)} citations</span>', unsafe_allow_html=True)
                    
                    # Step 4
                    confidence_level, confidence_reason = assess_confidence(sql_result, policy_results, intent)
                    conf_class = {"HIGH": "conf-high", "MEDIUM": "conf-medium", "LOW": "conf-low"}[confidence_level]
                    st.markdown(f'<span class="confidence-badge {conf_class}">Confidence: {confidence_level}</span>', unsafe_allow_html=True)
                    
                    status.update(label="Analysis complete", state="complete")

                # Generate and display answer
                with st.spinner(""):
                    answer = generate_governed_answer(
                        user_input_clean, intent, sql_result, policy_results,
                        confidence_level, confidence_reason, analyst_explanation
                    )
                
                # --- Guardrail: LOW confidence warning ---
                if confidence_level == "LOW":
                    st.warning(f"Low confidence: {confidence_reason}. Results may be incomplete.")

                st.markdown(answer)

                # Evidence Panel
                with st.expander("Evidence & Audit Trail"):
                    tab1, tab2, tab3, tab4 = st.tabs(["Data Evidence", "Regulatory Citations", "Generated SQL", "Pipeline"])
                    
                    with tab1:
                        if sql_result:
                            st.dataframe(sql_result[:15], use_container_width=True)
                        else:
                            st.info("No data evidence retrieved for this query.")
                    
                    with tab2:
                        if policy_results:
                            for p in policy_results:
                                st.markdown(f"""
                                **{p.get('REGULATION_NAME','')}** — {p.get('SECTION_TITLE','')}
                                
                                > {p.get('CONTENT','')[:500]}
                                
                                ---
                                """)
                        else:
                            st.info("No regulatory citations retrieved.")
                    
                    with tab3:
                        if generated_sql:
                            st.code(generated_sql, language="sql")
                        else:
                            st.info("No SQL was generated for this query.")
                    
                    with tab4:
                        st.markdown(f"""
                        | Step | Component | Result |
                        |------|-----------|--------|
                        | 1 | **AI_CLASSIFY** (Intent) | `{intent}` |
                        | 2 | **Cortex Analyst** (NL→SQL) | {"Generated SQL" if generated_sql else "Skipped"} |
                        | 3 | **Cortex Search** (Policy RAG) | {len(policy_results)} documents |
                        | 4 | **Confidence Assessment** | {confidence_level} |
                        | 5 | **Governed LLM** (Answer) | Generated with guardrails |
                        """)
                        st.caption(f"Semantic View: `{SEMANTIC_VIEW}`")

            except Exception as e:
                answer = f"I encountered an issue processing your request. Please try rephrasing your question.\n\n*Error: {str(e)[:100]}*"
                st.error(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})
            save_active_messages()
            st.rerun()
