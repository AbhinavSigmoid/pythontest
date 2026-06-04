import sys
import os
import json
import plotly.graph_objects as go

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
from rag.voice_transcriber import transcribe_audio

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)


st.set_page_config(
    page_title="GenAI Data Engineering Assistant",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Main App Font and Light Colors */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}

/* Sidebar Custom Background and Borders (Light Theme - Light Beige) */
section[data-testid="stSidebar"] {
    background-color: #F2EBD9 !important;
    border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
}

/* Force dark text for headings, list items, and standard texts globally */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4, [data-testid="stMarkdownContainer"] h5, [data-testid="stMarkdownContainer"] h6 {
    color: #0F172A !important;
}

.stMarkdown p, .stMarkdown li, .stMarkdown span,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] span {
    color: #1E293B !important;
}

/* Specifically style the sidebar title, subheaders and labels to ensure they are readable on light beige */
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 {
    color: #0F172A !important;
}
[data-testid="stSidebar"] p:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] li:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] span:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] label:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] small:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *) {
    color: #1E293B !important;
}

/* Except explicit classes and status indicators */
.dashboard-header h1, .dashboard-header h1 * {
    color: #FFFFFF !important;
}
.dashboard-header p, .dashboard-header p * {
    color: #93C5FD !important;
}
.stMarkdown span.pill-badge {
    color: #4F46E5 !important;
}
.stMarkdown span.pii-badge {
    color: #DC2626 !important;
}
.stMarkdown span.status-badge {
    color: #059669 !important;
}

/* Chat Message Text legibility */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.85) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
}
[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] span, 
[data-testid="stChatMessage"] li {
    color: #0F172A !important;
}

/* Streamlit widgets labels (selectboxes, file uploaders, inputs) */
label, .stWidgetLabel, [data-testid="stWidgetLabel"] p {
    color: #0F172A !important;
}

/* TextInput / ChatInput text color */
input, textarea, [data-testid="stChatInput"] textarea {
    color: #0F172A !important;
}

/* Caption and Small elements */
small, [data-testid="stCaptionContainer"], .stCaptionContainer {
    color: #475569 !important;
}

/* Glassmorphism Card Style (Light Theme) */
.custom-card {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    margin-bottom: 20px;
    color: #1E293B !important;
}

/* Premium Gradient Header (Light Theme Colors) */
.dashboard-header {
    background: linear-gradient(135deg, #2563EB 0%, #10B981 100%);
    border-radius: 16px;
    padding: 30px 40px;
    margin-bottom: 30px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15);
}

/* Status Indicator pulsing dot */
.pulse-dot {
    width: 10px;
    height: 10px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5);
    animation: pulse 1.8s infinite;
    vertical-align: middle;
    margin-right: 6px;
}
@keyframes pulse {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

/* Style Streamlit Metrics (Light Theme) */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(37, 99, 235, 0.3) !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.06) !important;
}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0F172A !important;
}

/* Navigation buttons in the sidebar (Light Theme) - Inactive buttons */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    text-align: left !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    transition: all 0.2s ease-in-out !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    margin-bottom: 6px !important;
}
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"] p,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"] span,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span {
    color: #0F172A !important;
}
[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background-color: #F1ECE4 !important;
    border-color: rgba(0, 0, 0, 0.15) !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] button:hover p,
[data-testid="stSidebar"] button:hover span,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover p,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover span,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover p,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover span {
    color: #2563EB !important;
}

/* Sidebar navigation buttons - Active primary button */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] [data-testid="baseButton-primary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-left: 4px solid #2563EB !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08) !important;
}
[data-testid="stSidebar"] button[kind="primary"] p,
[data-testid="stSidebar"] button[kind="primary"] span,
[data-testid="stSidebar"] [data-testid="baseButton-primary"] p,
[data-testid="stSidebar"] [data-testid="baseButton-primary"] span,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] span {
    color: #2563EB !important;
}

/* Sidebar container boxes (Status card) - White background instead of default brown/beige */
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stSidebar"] div[style*="border"] {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] span,
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stSidebar"] div[style*="border"] p,
[data-testid="stSidebar"] div[style*="border"] span,
[data-testid="stSidebar"] div[style*="border"] label {
    color: #0F172A !important;
}


/* Custom pills/buttons for prompt options (Light Theme) */
.prompt-pill {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.08);
    color: #2563EB;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-block;
    margin: 4px;
}
.prompt-pill:hover {
    background: rgba(37, 99, 235, 0.05);
    border-color: rgba(37, 99, 235, 0.3);
    color: #1D4ED8;
    transform: translateY(-1px);
}

/* Custom styled badge */
.pill-badge {
    background-color: rgba(99, 102, 241, 0.1);
    color: #4F46E5;
    border: 1px solid rgba(99, 102, 241, 0.2);
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.pii-badge {
    background-color: rgba(239, 68, 68, 0.1);
    color: #DC2626;
    border: 1px solid rgba(239, 68, 68, 0.2);
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
}

/* Agent Card and Pulse Radar styles */
.agent-status-card {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04) !important;
    margin-top: 15px !important;
    margin-bottom: 15px !important;
    transition: all 0.3s ease !important;
}
.agent-status-card:hover {
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.06) !important;
    transform: translateY(-2px) !important;
}
.active-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: rgba(16, 185, 129, 0.1);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.2);
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}
.radar-ping {
    width: 6px;
    height: 6px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    position: relative;
}
.radar-ping::after {
    content: '';
    width: 100%;
    height: 100%;
    background-color: #10B981;
    border-radius: 50%;
    position: absolute;
    top: 0;
    left: 0;
    animation: ping 1.2s ease-in-out infinite;
}
@keyframes ping {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    100% {
        transform: scale(2.5);
        opacity: 0;
    }
}
@keyframes progress-glow {
    0% {
        opacity: 0.85;
    }
    100% {
        opacity: 1;
        filter: drop-shadow(0 0 2px rgba(16, 185, 129, 0.5));
    }
}
</style>
""",
unsafe_allow_html=True)
# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("🚀 Data Platform")
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "🏠 Dashboard"

    pages = [
        "🏠 Dashboard",
        "🤖 AI Assistant",
        "📊 Pipeline Health",
        "📋 Data Catalog",
        "🔄 Lineage Explorer",
        "📂 Upload Center",
        "🏗️ Architecture"
    ]

    for p in pages:
        btn_type = "primary" if st.session_state.page == p else "secondary"
        if st.button(p, use_container_width=True, type=btn_type):
            st.session_state.page = p
            st.rerun()

    page = st.session_state.page

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<span style='color: #475569; font-size: 11px; font-weight: 600; text-transform: uppercase;'>🛡️ ENTERPRISE AGENT STATUS</span>", unsafe_allow_html=True)
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.markdown("<span style='color: #0F172A;'>🟢 <b>Gemini AI</b> (1.5 Pro)</span>", unsafe_allow_html=True)
        st.markdown("<span style='color: #0F172A;'>🟢 <b>AWS S3 Sync</b> (Connected)</span>", unsafe_allow_html=True)
        st.markdown("<span style='color: #0F172A;'>🟢 <b>ChromaDB Vector</b> (Ready)</span>", unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    try:

        with open(
            "metadata/tables.json",
            "r"
        ) as file:

            tables = json.load(file)

        total_tables = len(tables)

        pii_tables = len(
            [
                t for t in tables
                if t["contains_pii"]
            ]
        )

    except:

        total_tables = 0
        pii_tables = 0

    try:

        upload_files = [
            f
            for f in os.listdir("uploads")
            if f.endswith(".pdf")
        ]

        total_uploads = len(
            upload_files
        )

    except:

        total_uploads = 0

# =====================================
# MAIN PAGE
# =====================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="dashboard-header">
        <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
            🚀 GenAI Data Engineering Assistant
        </h1>
        <p style="color: #93C5FD; margin: 8px 0 0 0; font-size: 16px; font-weight: 400; opacity: 0.9;">
            AI-Powered Data Platform Command Center & Knowledge Engine
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Active Pipelines",
            value="2",
            delta="Operational"
        )

    with col2:
        st.metric(
            label="Indexed Documents",
            value=str(total_uploads),
            delta="Updated"
        )

    with col3:
        st.metric(
            label="PII Tables Detected",
            value=str(pii_tables),
            delta="Secured"
        )

    with col4:
        st.metric(
            label="Open Incidents",
            value="1",
            delta="-1 Resolving",
            delta_color="inverse"
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        summary_html = f"""
        <div class="custom-card" style="height: 100%;">
            <h3 style="margin-top:0; color: #0F172A; font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid rgba(0,0,0,0.06); padding-bottom: 10px;">📊 Platform Resource Summary</h3>
            <div style="display: grid; gap: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 8px;">
                    <span style="color: #475569; font-weight: 500;">Cataloged Tables</span>
                    <span style="font-weight: 600; font-size: 16px; color: #2563EB;">{total_tables}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 8px;">
                    <span style="color: #475569; font-weight: 500;">PII Monitored Tables</span>
                    <span class="pii-badge">{pii_tables} PII</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.03); padding-bottom: 8px;">
                    <span style="color: #475569; font-weight: 500;">Data Catalog Schema Sync</span>
                    <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);">Active</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 4px;">
                    <span style="color: #475569; font-weight: 500;">Knowledge Base Files</span>
                    <span style="font-weight: 600; font-size: 16px; color: #059669;">{total_uploads} PDFs</span>
                </div>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

    with col_right:
        status_html = f"""
        <div class="custom-card" style="height: 100%;">
            <h3 style="margin-top:0; color: #0F172A; font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid rgba(0,0,0,0.06); padding-bottom: 10px;">🌐 System Health Monitor</h3>
            <div style="display: grid; gap: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(0,0,0,0.01); border-radius: 8px; border: 1px solid rgba(0,0,0,0.03);">
                    <span style="font-weight: 500; color: #1E293B;">Gemini AI Integration</span>
                    <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Active</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(0,0,0,0.01); border-radius: 8px; border: 1px solid rgba(0,0,0,0.03);">
                    <span style="font-weight: 500; color: #1E293B;">AWS S3 Cloud Sync</span>
                    <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Connected</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(0,0,0,0.01); border-radius: 8px; border: 1px solid rgba(0,0,0,0.03);">
                    <span style="font-weight: 500; color: #1E293B;">ChromaDB Vector Store</span>
                    <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Healthy</span>
                </div>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

# =====================================
# CHAT TAB
# =====================================

if page == "🤖 AI Assistant":

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #0F172A; font-weight: 600;">🤖 RAG AI Assistant</h2>
        <p style="margin: 6px 0 0 0; color: #475569; font-size: 14px;">
            Ask questions about data catalogs, schemas, pipelines SLAs, lineaging, or document indices. Backed by ChromaDB and Gemini.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Quick prompt pills above chat
    st.write("💡 **Quick Queries:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_query = None
    with q_col1:
        if st.button("🔍 List PII Tables", use_container_width=True):
            quick_query = "Which tables contain PII?"
    with q_col2:
        if st.button("📊 Pipeline Status", use_container_width=True):
            quick_query = "What is the health status and SLAs of my pipelines?"
    with q_col3:
        if st.button("🔄 Show Lineage", use_container_width=True):
            quick_query = "Show the lineage details of orders tables."
    with q_col4:
        if st.button("📋 View Data Catalog", use_container_width=True):
            quick_query = "List all tables cataloged in the system."

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Render previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # =====================================
    # VOICE INPUT SECTION
    # =====================================

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #EEF2FF 0%, #F0FDF4 100%);
        border: 1.5px solid #C7D2FE;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 14px;
    ">
        <p style="margin:0 0 10px 0; font-weight:600; color:#4338CA; font-size:15px;">
            🎙️ Voice Input — Speak your question
        </p>
        <p style="margin:0; color:#64748B; font-size:13px;">
            Click the microphone below, record your question, then click Stop.
            Your speech will be transcribed and sent to the assistant automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)

    audio_value = st.audio_input(
        label="Record your question",
        key="voice_input"
    )

    voice_query = None

    if audio_value is not None:
        import hashlib
        audio_bytes = audio_value.read()
        audio_hash  = hashlib.md5(audio_bytes).hexdigest()

        if "last_voice_hash" not in st.session_state:
            st.session_state.last_voice_hash = None

        if audio_hash != st.session_state.last_voice_hash:
            with st.spinner("🎙️ Transcribing your voice..."):
                transcribed = transcribe_audio(audio_bytes)

            if transcribed and not transcribed.startswith("[Voice Error"):
                st.success(f"✅ Transcribed: *\"{transcribed}\"*")
                voice_query = transcribed
                st.session_state.last_voice_hash = audio_hash
            elif transcribed.startswith("[Voice Error"):
                st.error(transcribed)
            else:
                st.warning("⚠️ Could not understand audio. Please speak clearly and try again.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # =====================================
    # TEXT INPUT SECTION
    # =====================================

    query = st.chat_input("Or type your question about pipelines, metadata, lineage, SLAs...")

    # Voice query takes priority if spoken; else use quick_query pill; else typed query
    if voice_query:
        query = voice_query
    elif quick_query:
        query = quick_query

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
        st.rerun()

# =====================================
# PIPELINE HEALTH TAB
# =====================================

if page == "📊 Pipeline Health":

    health = get_pipeline_health()

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #0F172A; font-weight: 600;">📊 Pipeline Health Monitor</h2>
        <p style="margin: 6px 0 0 0; color: #475569; font-size: 14px;">
            Real-time ingestion pipeline uptime, SLA achievements, and recent platform incident logs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    h_col1, h_col2 = st.columns(2)
    with h_col1:
        orders_card = f"""
        <div class="custom-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #0F172A; font-size: 16px; font-weight: 600;">📦 Orders Ingestion Pipeline</h4>
                <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Operational</span>
            </div>
            <div style="display: grid; gap: 10px; font-size: 14px;">
                <div style="display: flex; justify-content: space-between;"><span style="color: #475569;">Uptime Availability</span><span style="font-weight:600; color: #059669;">{health['orders_pipeline']['availability']}</span></div>
                <div style="display: flex; justify-content: space-between;"><span style="color: #475569;">Last Sync Time</span><span style="font-weight:500; color: #1E293B;">{health['orders_pipeline']['last_run']}</span></div>
                <div style="display: flex; justify-content: space-between;"><span style="color: #475569;">Target SLA</span><span style="font-weight:500; color: #2563EB;">{health['orders_pipeline']['sla']}</span></div>
            </div>
        </div>
        """
        st.markdown(orders_card, unsafe_allow_html=True)

    with h_col2:
        customer_card = f"""
        <div class="custom-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #0F172A; font-size: 16px; font-weight: 600;">👥 Customers Sync Pipeline</h4>
                <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Operational</span>
            </div>
            <div style="display: grid; gap: 10px; font-size: 14px;">
                <div style="display: flex; justify-content: space-between;"><span style="color: #475569;">Uptime Availability</span><span style="font-weight:600; color: #059669;">{health['customer_pipeline']['availability']}</span></div>
                <div style="display: flex; justify-content: space-between;"><span style="color: #475569;">Last Sync Time</span><span style="font-weight:500; color: #1E293B;">{health['customer_pipeline']['last_run']}</span></div>
                <div style="display: flex; justify-content: space-between;"><span style="color: #475569;">Target SLA</span><span style="font-weight:500; color: #2563EB;">{health['customer_pipeline']['sla']}</span></div>
            </div>
        </div>
        """
        st.markdown(customer_card, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Orders Ingestion Pipeline", "Customer Sync Pipeline"],
            y=[99.95, 99.90],
            marker_color=["#3B82F6", "#0D9488"],
            width=0.35
        )
    )
    fig.update_layout(
        title="Uptime Availability Actual vs Target (%)",
        yaxis_title="Availability %",
        yaxis_range=[99.8, 100.0],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0F172A', family='Outfit'),
        height=320,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
    
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    incident = health["recent_incident"]
    incident_html = f"""
    <div class="custom-card" style="border-left: 4px solid #D97706;">
        <h4 style="margin: 0; color: #D97706; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            ⚠️ Recent Platform Incident Logs
        </h4>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; font-size: 13px;">
            <div><span style="color: #64748B;">Incident ID:</span><br><strong style="color: #1E293B;">{incident['incident_id']}</strong></div>
            <div><span style="color: #64748B;">Impacted Pipeline:</span><br><strong style="color: #1E293B;">{incident['pipeline']}</strong></div>
            <div><span style="color: #64748B;">Current Status:</span><br><span class="pill-badge" style="background-color: rgba(245, 158, 11, 0.1); color: #D97706; border: 1px solid rgba(245, 158, 11, 0.2);">{incident['status']}</span></div>
            <div><span style="color: #64748B;">Incident Impact:</span><br><strong style="color: #EF4444;">{incident['impact']}</strong></div>
        </div>
    </div>
    """
    st.markdown(incident_html, unsafe_allow_html=True)

# =====================================
# DATA CATALOG TAB
# =====================================

if page == "📋 Data Catalog":

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #0F172A; font-weight: 600;">📋 Data Catalog Explorer</h2>
        <p style="margin: 6px 0 0 0; color: #475569; font-size: 14px;">
            Discover cataloged physical schemas, access policies, ownership metadata, and PII status details.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with open(
        "metadata/tables.json",
        "r"
    ) as file:

        tables = json.load(file)
    
    search_table = st.text_input(
        "🔍 Search Cataloged Tables",
        placeholder="Type table name to filter..."
    )

    if search_table:

        tables = [
            t
            for t in tables
            if search_table.lower()
            in t["table_name"].lower()
        ]

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    for table in tables:
        pii_status = "⚠️ Contains PII" if table['contains_pii'] else "✅ Secured"
        with st.expander(f"📁 {table['table_name']}  |  Owner: {table['owner']}  |  {pii_status}"):
            col_col1, col_col2 = st.columns(2)
            with col_col1:
                card_info = f"""
                <div style="padding: 16px; background: rgba(0,0,0,0.015); border-radius: 10px; border: 1px solid rgba(0,0,0,0.03); height: 100%;">
                    <span style="color: #64748B; font-size: 12px; font-weight: 500;">DATA OWNER</span><br>
                    <strong style="color: #1E293B; font-size: 15px;">{table['owner']}</strong>
                    <br><br>
                    <span style="color: #64748B; font-size: 12px; font-weight: 500;">SECURITY CLASSIFICATION</span><br>
                    {"<span class='pii-badge'>Contains PII Data</span>" if table['contains_pii'] else "<span class='pill-badge' style='background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);'>No Sensitive PII</span>"}
                </div>
                """
                st.markdown(card_info, unsafe_allow_html=True)
            with col_col2:
                st.markdown("<div style='font-size: 13px; font-weight:600; color: #64748B; margin-bottom: 8px;'>COLUMNS & PHYSICAL SCHEMA</div>", unsafe_allow_html=True)
                for col in table["columns"]:
                    st.markdown(f"- `<code style='color: #2563EB; background: transparent; padding: 0;'>{col}</code>`", unsafe_allow_html=True)

# =====================================
# LINEAGE TAB
# =====================================

if page == "🔄 Lineage Explorer":

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #0F172A; font-weight: 600;">🔄 Data Lineage Tracker</h2>
        <p style="margin: 6px 0 0 0; color: #475569; font-size: 14px;">
            Track upstream-to-downstream table flows and transformations across ingestion and serving layers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with open(
        "metadata/lineage.json",
        "r"
    ) as file:

        lineage_data = json.load(file)

    for table, lineage in lineage_data.items():

        st.markdown(f"#### 📍 Lineage Flow for `{table}`")
        
        flow_steps = []
        for idx, step in enumerate(lineage):
            flow_steps.append(f"""
            <div style="
                background: rgba(37, 99, 235, 0.08);
                border: 1px solid rgba(37, 99, 235, 0.3);
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                color: #1D4ED8;
                text-align: center;
                min-width: 140px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            ">
                {step}
            </div>
            """)
        
        flow_html = f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 15px;
            flex-wrap: wrap;
            padding: 20px;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            border: 1px solid rgba(0, 0, 0, 0.06);
            margin-bottom: 30px;
        ">
            {" <div style='color: #2563EB; font-weight: bold; font-size: 18px;'>➔</div> ".join(flow_steps)}
        </div>
        """
        st.markdown(flow_html, unsafe_allow_html=True)

# =====================================
# UPLOAD CENTER
# =====================================

if page == "📂 Upload Center":

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #0F172A; font-weight: 600;">📂 Document Index Center</h2>
        <p style="margin: 6px 0 0 0; color: #475569; font-size: 14px;">
            Monitor files synced to AWS S3. Sync operations trigger automated text extraction and vector embedding.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:

        files = os.listdir(
            UPLOAD_DIR
        )

        pdfs = [
            f
            for f in files
            if f.endswith(".pdf")
        ]

        if pdfs:

            cols = st.columns(3)
            for idx, pdf in enumerate(pdfs):

                file_path = os.path.join(
                    UPLOAD_DIR,
                    pdf
                )

                size_kb = round(
                    os.path.getsize(file_path) / 1024,
                    2
                )

                col_target = cols[idx % 3]
                with col_target:
                    card_html = f"""
                    <div class="custom-card" style="padding: 18px; margin-bottom: 15px; border-top: 3px solid #3B82F6; background: rgba(255, 255, 255, 0.85);">
                        <div style="font-size: 28px; margin-bottom: 8px;">📄</div>
                        <div style="font-weight: 600; color: #1E293B; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; font-size: 15px;" title="{pdf}">
                            {pdf}
                        </div>
                        <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #64748B; font-size: 12px; font-weight: 500;">{size_kb} KB</span>
                            <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);">Indexed</span>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

        else:

            st.warning(
                "No PDFs Found"
            )

    except:

        st.error(
            "Uploads folder not found"
        )

if page == "🏗️ Architecture":

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #0F172A; font-weight: 600;">🏗️ Platform System Architecture</h2>
        <p style="margin: 6px 0 0 0; color: #475569; font-size: 14px;">
            End-to-end data pipeline flow from local uploads and watchdog sync to ChromaDB vector search and Gemini AI serving.
        </p>
    </div>
    """, unsafe_allow_html=True)

    image_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "architecture.png"
    )

    st.image(
        image_path,
        use_container_width=True
    )

# =====================================
# FOOTER
# =====================================

st.markdown("---")

st.caption(
    "Built with Gemini • ChromaDB • AWS S3 • Streamlit"
)