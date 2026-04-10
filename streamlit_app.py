"""
streamlit_app.py
────────────────────────────────────────────────────────────────────────────────
Streamlit Chatbot Frontend for the NL2SQL Clinic Intelligence API.

Features:
  ✅ Chat-style UI with message history
  ✅ Displays SQL query (syntax-highlighted)
  ✅ Displays result table (scrollable)
  ✅ Renders Plotly charts inline
  ✅ Shows row counts & performance info
  ✅ Quick-question sidebar
  ✅ Cache indicator badge
  ✅ Error display with friendly messages

Run:  streamlit run streamlit_app.py
      (Make sure the FastAPI server is running on port 8000 first)
"""

import json
import time
import requests
import pandas as pd
import streamlit as st
import plotly.io as pio

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏥 Clinic Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark clinic theme */
  .stApp { background: #0f172a; color: #e2e8f0; }

  /* Chat bubbles */
  .user-bubble {
    background: linear-gradient(135deg, #1e40af, #1d4ed8);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 20%;
    color: white;
    font-size: 0.95rem;
    box-shadow: 0 2px 8px rgba(29,78,216,0.3);
  }
  .assistant-bubble {
    background: #1e293b;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 20% 8px 0;
    color: #e2e8f0;
    border-left: 3px solid #0f766e;
    font-size: 0.95rem;
  }

  /* SQL code block */
  .sql-block {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.85rem;
    color: #79c0ff;
    overflow-x: auto;
    margin: 8px 0;
  }

  /* Metric badges */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
  }
  .badge-green  { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid #10b981; }
  .badge-blue   { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid #3b82f6; }
  .badge-purple { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid #8b5cf6; }
  .badge-orange { background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid #f97316; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e293b; }
  [data-testid="stSidebar"] .stButton > button {
    background: #1e293b; color: #94a3b8;
    border: 1px solid #334155; border-radius: 8px;
    width: 100%; text-align: left; font-size: 0.85rem;
    padding: 8px 12px; margin: 2px 0;
    transition: all 0.2s;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: #0f766e; color: white; border-color: #0f766e;
  }

  /* Input */
  .stTextInput > div > div > input {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
  }

  /* Send button */
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0f766e, #0891b2);
    color: white; border: none; border-radius: 10px;
    font-weight: 600; padding: 10px 24px;
  }

  /* Header */
  .clinic-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f766e 100%);
    padding: 20px 28px; border-radius: 12px;
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 16px;
  }
  .clinic-header h1 { margin: 0; font-size: 1.6rem; color: white; }
  .clinic-header p  { margin: 4px 0 0; color: rgba(255,255,255,0.7); font-size: 0.9rem; }

  /* Table */
  .stDataFrame { border-radius: 8px; overflow: hidden; }

  /* Error */
  .error-box {
    background: rgba(239,68,68,0.1);
    border: 1px solid #ef4444;
    border-radius: 8px; padding: 12px 16px; color: #fca5a5;
  }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

QUICK_QUESTIONS = [
    "How many patients do we have?",
    "List all doctors and their specializations",
    "Which doctor has the most appointments?",
    "What is the total revenue?",
    "Show revenue by doctor",
    "Top 5 patients by spending",
    "Which city has the most patients?",
    "Show unpaid invoices",
    "Average treatment cost by specialization",
    "Show monthly appointment count for the past 6 months",
    "What percentage of appointments are no-shows?",
    "List patients who visited more than 3 times",
    "Show revenue trend by month",
    "Compare revenue between departments",
    "Show patient registration trend by month",
]

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""


# ── Callback for input handling ────────────────────────────────────────────────
def on_input_change():
    """Callback triggered when user presses Enter or interacts with input"""
    user_text = st.session_state.get("chat_input", "").strip()
    if user_text:
        st.session_state.pending_question = user_text
        st.session_state.chat_input = ""  # Clear input
        st.rerun()


def on_quick_question(question: str):
    """Callback triggered when user clicks a quick question"""
    st.session_state.pending_question = question
    st.rerun()


# ── Helper functions ──────────────────────────────────────────────────────────

def check_api_health() -> dict | None:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def ask_question(question: str) -> dict:
    t0 = time.perf_counter()
    try:
        r = requests.post(
            f"{API_BASE}/chat",
            json={"question": question},
            timeout=60,
        )
        elapsed = round((time.perf_counter() - t0) * 1000)
        data = r.json()
        data["_elapsed_ms"] = elapsed
        return data
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Is the FastAPI server running on port 8000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The AI might be processing — try again."}
    except Exception as e:
        return {"error": str(e)}


def render_message(msg: dict):
    role = msg["role"]
    if role == "user":
        st.markdown(
            f'<div class="user-bubble">👤 {msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        data = msg.get("data", {})
        error = data.get("error")

        st.markdown('<div class="assistant-bubble">', unsafe_allow_html=True)

        if error:
            st.markdown(
                f'<div class="error-box">⚠️ {error}</div>',
                unsafe_allow_html=True,
            )
        else:
            # Message text
            st.markdown(f"🤖 **{data.get('message', '')}**")

            # Badges row
            badges = ""
            if data.get("row_count") is not None:
                badges += f'<span class="badge badge-green">📊 {data["row_count"]} rows</span>'
            if data.get("chart_type") and data["chart_type"] != "none":
                badges += f'<span class="badge badge-purple">📈 {data["chart_type"]} chart</span>'
            if data.get("cached"):
                badges += '<span class="badge badge-orange">⚡ cached</span>'
            if data.get("_elapsed_ms"):
                badges += f'<span class="badge badge-blue">⏱ {data["_elapsed_ms"]}ms</span>'
            if badges:
                st.markdown(badges, unsafe_allow_html=True)

            # SQL query
            if data.get("sql_query"):
                with st.expander("🔍 View Generated SQL", expanded=False):
                    st.code(data["sql_query"], language="sql")

            # Data table
            if data.get("rows") and data.get("columns"):
                df = pd.DataFrame(data["rows"], columns=data["columns"])
                st.dataframe(df, use_container_width=True, hide_index=True)

            # Plotly chart
            if data.get("chart") and data["chart"] != "none":
                try:
                    fig = pio.from_json(json.dumps(data["chart"]))
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Chart render failed: {e}")

        st.markdown('</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 NL2SQL Clinic AI")
    st.markdown("---")

    # API health
    health = check_api_health()
    if health:
        st.success(f"✅ API Online  |  🧠 {health.get('agent_memory_items', 0)} memories")
        st.caption(f"LLM: {health.get('llm_provider', 'unknown').upper()}")
    else:
        st.error("❌ API Offline — Start server first:\n`uvicorn main:app --port 8000`")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Questions")
    st.caption("Click to ask instantly:")

    for q in QUICK_QUESTIONS:
        if st.button(q, key=f"quick_{hash(q)}", use_container_width=True):
            on_quick_question(q)

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📚 Resources")
    st.markdown(
        "- [API Docs](http://localhost:8000/docs)\n"
        "- [ReDoc](http://localhost:8000/redoc)\n"
        "- [Vanna Docs](https://vanna.ai/docs)"
    )


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="clinic-header">
  <div>
    <h1>🏥 Clinic Intelligence Assistant</h1>
    <p>Ask questions in plain English — get instant answers from the clinic database</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Message history ───────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #475569;">
          <div style="font-size: 3rem; margin-bottom: 12px;">💬</div>
          <div style="font-size: 1.1rem; font-weight: 600; color: #64748b;">
            Ask anything about your clinic data
          </div>
          <div style="font-size: 0.9rem; margin-top: 8px; color: #475569;">
            Try: "How many patients do we have?" or click a quick question →
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            render_message(msg)

# ── Input Row ─────────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    st.text_input(
        label="Question",
        placeholder="e.g. Show me the top 5 patients by total spending…",
        label_visibility="collapsed",
        key="chat_input",
        on_change=on_input_change,
    )

with col2:
    if st.button("Send ➤", type="primary", use_container_width=True):
        on_input_change()

# ── Process Input ─────────────────────────────────────────────────────────────
# Handle pending question (from quick question or Enter key)
question = st.session_state.get("pending_question", "").strip()

if question:
    # Clear the pending question
    st.session_state.pending_question = ""
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Get AI response
    with st.spinner("🤖 Thinking…"):
        response = ask_question(question)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "data": response})
    st.rerun()
