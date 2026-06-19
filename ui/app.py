"""
ui/app.py  —  HR Agent Streamlit Chat UI

Run:  streamlit run ui/app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import logger
import streamlit as st
from agent.hr_agent import run_agent

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Assistant",
    page_icon="🏢",
    layout="centered",
)

logger.info("APP_START | Streamlit HR Assistant started")  # ✅ LOG

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Tool call pill */
.tool-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f0f4ff; border: 1px solid #c7d4f7;
    border-radius: 20px; padding: 3px 12px;
    font-size: 12px; color: #3b5bdb; font-weight: 500;
    margin: 2px 0;
}
.tool-pill.result {
    background: #f0faf4; border-color: #b2dfce; color: #1e7a4a;
}
/* Sidebar employee card */
.emp-card {
    background: #f8f9fa; border-radius: 10px;
    padding: 12px 14px; margin-bottom: 8px;
    border-left: 3px solid #4c6ef5;
    font-size: 13px; line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏢 HR Assistant")
    st.markdown("---")

    st.markdown("**Demo employees**")
    st.markdown("""
<div class='emp-card'>
<b>E001</b> — Aisha Sharma<br>
Engineering · Software Engineer
</div>
<div class='emp-card'>
<b>E002</b> — Rohan Patel<br>
Marketing · Marketing Analyst
</div>
<div class='emp-card'>
<b>E003</b> — Sneha Iyer<br>
HR · HR Executive
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Try asking**")
    example_qs = [
        "How many casual leaves do I get?",
        "Check leave balance for E001",
        "Apply casual leave for E002 from 2025-07-20 to 2025-07-21",
        "Show payslip for E001 for May 2025",
        "What is the WFH policy?",
        "What is the password policy?",
    ]
    for q in example_qs:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.pending_input = q

    st.markdown("---")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history  = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("### 🏢 HR Assistant")
st.caption("Ask about policies, leave balances, payslips, or apply for leave.")

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            # Show tool activity if any
            if msg.get("tool_activity"):
                with st.expander("🔧 Agent activity", expanded=False):
                    for step in msg["tool_activity"]:
                        if step["type"] == "tool_call":
                            st.markdown(
                                f"<span class='tool-pill'>⚡ Called <b>{step['tool']}</b>"
                                f" with {step['inputs']}</span>",
                                unsafe_allow_html=True
                            )
                        elif step["type"] == "tool_result":
                            st.markdown(
                                f"<span class='tool-pill result'>✅ Result from <b>{step['tool']}</b></span>",
                                unsafe_allow_html=True
                            )
                            st.code(step["result"], language=None)
            st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])

# ── Input handling ────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask an HR question...")
if st.session_state.pending_input:
    prompt = st.session_state.pending_input
    st.session_state.pending_input = None

if prompt:

    # ✅ LOG — capture every question the user submits
    logger.info(f"UI_INPUT | message={prompt}")

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent
    with st.chat_message("assistant"):
        tool_activity = []
        final_text    = ""
        error_text    = ""

        status_box    = st.empty()
        answer_box    = st.empty()

        try:
            for event in run_agent(prompt, st.session_state.history):
                if event["type"] == "tool_call":
                    tool_activity.append(event)
                    status_box.markdown(
                        f"<span class='tool-pill'>⚡ Calling <b>{event['tool']}</b>…</span>",
                        unsafe_allow_html=True
                    )
                elif event["type"] == "tool_result":
                    tool_activity.append(event)
                    status_box.markdown(
                        f"<span class='tool-pill result'>✅ Got result from <b>{event['tool']}</b></span>",
                        unsafe_allow_html=True
                    )
                elif event["type"] == "final":
                    final_text = event["text"]
                elif event["type"] == "error":
                    error_text = event["text"]

        except Exception as e:
            error_text = str(e)
            logger.error(f"UI_CRASH | message={prompt} | error={str(e)}")  # ✅ LOG


        status_box.empty()

        # Render tool activity collapsible
        if tool_activity:
            with st.expander("🔧 Agent activity", expanded=False):
                for step in tool_activity:
                    if step["type"] == "tool_call":
                        st.markdown(
                            f"<span class='tool-pill'>⚡ Called <b>{step['tool']}</b>"
                            f" with {step['inputs']}</span>",
                            unsafe_allow_html=True
                        )
                    elif step["type"] == "tool_result":
                        st.markdown(
                            f"<span class='tool-pill result'>✅ Result from <b>{step['tool']}</b></span>",
                            unsafe_allow_html=True
                        )
                        st.code(step["result"], language=None)

        if error_text:
            reply = f"⚠️ Error: {error_text}"
            logger.warning(f"UI_ERROR_REPLY | error={error_text}")          
        else:
            reply = final_text or "I couldn't find an answer. Please try rephrasing."
            logger.info(f"UI_REPLY | reply={reply[:200]}")  
        answer_box.markdown(reply)

    # Save to session
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "tool_activity": tool_activity,
    })

    # Update agent history (for multi-turn memory)
    st.session_state.history.append({"role": "user",      "content": prompt})
    st.session_state.history.append({"role": "assistant",  "content": reply})
