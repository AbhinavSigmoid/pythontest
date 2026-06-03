import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import streamlit as st

from rag.chatbot import ask_question
from agents.health_agent import get_pipeline_health


st.set_page_config(
    page_title="GenAI Data Engineering Assistant",
    page_icon="🚀",
    layout="wide"
)

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("📊 System Dashboard")

    st.success("🤖 Gemini Connected")

    st.success("☁️ S3 Connected")

    st.success("🧠 ChromaDB Active")

    st.markdown("---")

    st.metric(
        "Documents Indexed",
        "6+"
    )

    st.metric(
        "Knowledge Sources",
        "PDF + TXT"
    )

    st.metric(
        "Vector Database",
        "Active"
    )

    st.markdown("---")

    st.subheader("System Flow")

    st.markdown("""
OneDrive
   ↓
Watcher
   ↓
AWS S3
   ↓
PDF Processing
   ↓
ChromaDB
   ↓
Gemini
""")

# =====================================
# MAIN PAGE
# =====================================

st.title(
    "🚀 GenAI Data Engineering Assistant"
)

st.caption(
    "Enterprise Knowledge Assistant for Data Engineering Teams"
)

tab1, tab2 = st.tabs(
    [
        "🤖 Chat Assistant",
        "📊 Pipeline Health"
    ]
)

# =====================================
# CHAT TAB
# =====================================

with tab1:

    if "messages" not in st.session_state:

        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    query = st.chat_input(
        "Ask about pipelines, metadata, lineage, SLAs..."
    )

    if query:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": query
            }
        )

        with st.chat_message("user"):

            st.write(query)

        answer = ask_question(query)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):

            st.write(answer)

# =====================================
# PIPELINE HEALTH TAB
# =====================================

with tab2:

    health = get_pipeline_health()

    st.subheader(
        "Pipeline Status"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            "🟢 Orders Pipeline"
        )

        st.write(
            f"Availability: {health['orders_pipeline']['availability']}"
        )

        st.write(
            f"Last Run: {health['orders_pipeline']['last_run']}"
        )

        st.write(
            f"SLA: {health['orders_pipeline']['sla']}"
        )

    with col2:

        st.success(
            "🟢 Customer Pipeline"
        )

        st.write(
            f"Availability: {health['customer_pipeline']['availability']}"
        )

        st.write(
            f"Last Run: {health['customer_pipeline']['last_run']}"
        )

        st.write(
            f"SLA: {health['customer_pipeline']['sla']}"
        )

    st.markdown("---")

    st.subheader(
        "Recent Incident"
    )

    incident = health["recent_incident"]

    st.warning(
        f"""
Incident ID: {incident['incident_id']}

Pipeline: {incident['pipeline']}

Status: {incident['status']}

Impact: {incident['impact']}
"""
    )

# =====================================
# FOOTER
# =====================================

st.markdown("---")

st.caption(
    "Built with Gemini • ChromaDB • AWS S3 • Streamlit"
)