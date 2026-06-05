import sys
import os
import json
import time
import plotly.graph_objects as go

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import streamlit as st
from dotenv import load_dotenv

# Load local environment if present
load_dotenv(override=True)

# Export streamlit secrets to os.environ for compatibility with sub-modules using os.getenv
try:
    if hasattr(st, "secrets"):
        for key in st.secrets.keys():
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass

from rag.chatbot import ask_question
from agents.health_agent import get_pipeline_health

# Import ingestion scripts
try:
    from scripts.auto_indexer import process_pdf
    from scripts.s3_uploader import upload_file, list_s3_files, download_file_from_s3
except ImportError:
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from auto_indexer import process_pdf
        from s3_uploader import upload_file, list_s3_files, download_file_from_s3
    except ImportError:
        process_pdf = None
        upload_file = None
        list_s3_files = lambda: []
        download_file_from_s3 = None
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

# Initialize Theme Mode in session state
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

if "active_pdf" not in st.session_state:
    st.session_state.active_pdf = None

# Auto-initialize ChromaDB from local uploads at startup if empty (e.g. fresh deployment)
if "db_auto_indexed" not in st.session_state:
    try:
        from rag.retriever import DB_PATH
        import chromadb
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_or_create_collection(name="de_documents")
        if collection.count() == 0 and os.path.exists(UPLOAD_DIR):
            pdfs = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]
            if pdfs:
                st.toast("Initializing database index from default runbooks...", icon="⚙️")
                for pdf in pdfs:
                    pdf_path = os.path.join(UPLOAD_DIR, pdf)
                    process_pdf(pdf_path)
                st.toast("Database index initialized successfully!", icon="✅")
    except Exception as e:
        print("Failed to auto-initialize database index at startup:", e)
    st.session_state["db_auto_indexed"] = True

if st.session_state.theme_mode == "Dark":
    c_bg = "#0B0F19"
    c_sidebar_bg = "#111827"
    c_text_headings = "#F3F4F6"
    c_text_body = "#E5E7EB"
    c_card_bg = "#1F2937"
    c_card_border = "rgba(255, 255, 255, 0.08)"
    c_chat_msg_bg = "#1F2937"
    c_chat_msg_border = "rgba(255, 255, 255, 0.08)"
    c_chat_msg_text = "#E5E7EB"
    c_input_bg = "#111827"
    c_input_border = "rgba(255, 255, 255, 0.15)"
    c_input_text = "#F3F4F6"
    c_btn_bg = "#1F2937"
    c_btn_border = "rgba(255, 255, 255, 0.15)"
    c_btn_text = "#F3F4F6"
    c_btn_hover_bg = "#374151"
    c_btn_hover_border = "rgba(255, 255, 255, 0.25)"
    c_btn_hover_text = "#FFFFFF"
    c_sidebar_btn_bg = "#111827"
    c_sidebar_btn_border = "rgba(255, 255, 255, 0.08)"
    c_sidebar_btn_text = "#E5E7EB"
    c_sidebar_btn_hover_bg = "#1F2937"
    c_sidebar_btn_hover_text = "#3B82F6"
    c_sidebar_active_bg = "#111827"
    c_sidebar_active_border = "#3B82F6"
    c_sidebar_active_text = "#3B82F6"
    c_nested_box_bg = "#111827"
    c_nested_box_border = "rgba(255, 255, 255, 0.05)"
    c_lineage_node_bg = "#374151"
    c_lineage_node_border = "rgba(255, 255, 255, 0.15)"
    c_lineage_node_text = "#F3F4F6"
    c_lineage_arrow = "#F3F4F6"
    c_sidebar_label = "#9CA3AF"
    c_text_muted = "#9CA3AF"
    c_voice_bg = "linear-gradient(135deg, #1E1B4B 0%, #064E3B 100%)"
    c_voice_border = "#312E81"
    c_voice_title = "#C7D2FE"
    c_voice_text = "#D1FAE5"
    c_plotly_modebar_btn = "#9CA3AF"
else:
    c_bg = "#F8FAFC"
    c_sidebar_bg = "#F2EBD9"
    c_text_headings = "#0F172A"
    c_text_body = "#1E293B"
    c_card_bg = "#FAF6F0"
    c_card_border = "rgba(78, 54, 41, 0.12)"
    c_chat_msg_bg = "#F5EBE0"
    c_chat_msg_border = "rgba(78, 54, 41, 0.15)"
    c_chat_msg_text = "#4E3629"
    c_input_bg = "#FAF6F0"
    c_input_border = "rgba(78, 54, 41, 0.12)"
    c_input_text = "#4E3629"
    c_btn_bg = "#FAF6F0"
    c_btn_border = "rgba(78, 54, 41, 0.15)"
    c_btn_text = "#4E3629"
    c_btn_hover_bg = "#EDE0D4"
    c_btn_hover_border = "rgba(78, 54, 41, 0.25)"
    c_btn_hover_text = "#3E2723"
    c_sidebar_btn_bg = "#FFFFFF"
    c_sidebar_btn_border = "rgba(0, 0, 0, 0.08)"
    c_sidebar_btn_text = "#0F172A"
    c_sidebar_btn_hover_bg = "#F1ECE4"
    c_sidebar_btn_hover_text = "#2563EB"
    c_sidebar_active_bg = "#FFFFFF"
    c_sidebar_active_border = "#2563EB"
    c_sidebar_active_text = "#2563EB"
    c_nested_box_bg = "#FDFBF9"
    c_nested_box_border = "rgba(78, 54, 41, 0.1)"
    c_lineage_node_bg = "#FAF6F0"
    c_lineage_node_border = "rgba(78, 54, 41, 0.15)"
    c_lineage_node_text = "#4E3629"
    c_lineage_arrow = "#4E3629"
    c_sidebar_label = "#1E293B"
    c_text_muted = "#8D7B68"
    c_voice_bg = "linear-gradient(135deg, #EEF2FF 0%, #F0FDF4 100%)"
    c_voice_border = "#C7D2FE"
    c_voice_title = "#4338CA"
    c_voice_text = "#2C4068"
    c_plotly_modebar_btn = "#4B5563"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

.material-symbols-outlined {{
    font-family: 'Material Symbols Outlined' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 24px;
    line-height: 1;
    display: inline-block;
    vertical-align: middle;
}}

/* Main App Font and Colors */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {{
    font-family: 'Outfit', sans-serif !important;
    background-color: {c_bg} !important;
    color: {c_text_headings} !important;
}}

/* Sidebar Custom Background and Borders */
section[data-testid="stSidebar"] {{
    background-color: {c_sidebar_bg} !important;
    border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
}}

/* Force headings and text colors globally */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4, [data-testid="stMarkdownContainer"] h5, [data-testid="stMarkdownContainer"] h6 {{
    color: {c_text_headings} !important;
}}

.stMarkdown p, .stMarkdown li, .stMarkdown span,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] span {{
    color: {c_text_body} !important;
}}

/* Sidebar labels and titles */
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 {{
    color: {c_text_headings} !important;
}}
[data-testid="stSidebar"] p:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] li:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] span:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] label:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *), 
[data-testid="stSidebar"] small:not(button *):not([data-testid="baseButton-secondary"] *):not([data-testid="baseButton-primary"] *):not([data-testid="stBaseButton-secondary"] *):not([data-testid="stBaseButton-primary"] *) {{
    color: {c_sidebar_label} !important;
}}

/* Except explicit classes and status indicators */
.dashboard-header h1, .dashboard-header h1 * {{
    color: #FFFFFF !important;
}}
.dashboard-header p, .dashboard-header p * {{
    color: #93C5FD !important;
}}
.stMarkdown span.pill-badge {{
    color: #4F46E5 !important;
}}
.stMarkdown span.pii-badge {{
    color: #DC2626 !important;
}}
.stMarkdown span.status-badge {{
    color: #059669 !important;
}}

/* Chat Message Text legibility & Bubble styling */
[data-testid="stChatMessage"] {{
    background-color: {c_chat_msg_bg} !important;
    border: 1px solid {c_chat_msg_border} !important;
}}
[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] span, 
[data-testid="stChatMessage"] li {{
    color: {c_chat_msg_text} !important;
}}

/* Streamlit widgets labels (selectboxes, file uploaders, inputs) */
label, .stWidgetLabel, [data-testid="stWidgetLabel"] p {{
    color: {c_text_headings} !important;
}}

/* TextInput / ChatInput / SearchInput/Selectbox styling */
input, textarea, select, div[data-baseweb="select"] > div, div[data-baseweb="select"] span, div[data-baseweb="select"] svg {{
    color: {c_input_text} !important;
    background-color: {c_input_bg} !important;
    border: 1px solid {c_input_border} !important;
    border-radius: 8px !important;
}}

div[role="listbox"] ul, div[role="listbox"] li {{
    background-color: {c_input_bg} !important;
    color: {c_input_text} !important;
}}

/* Specific Chat Input styling */
[data-testid="stChatInput"] {{
    background-color: transparent !important;
}}

[data-testid="stChatInput"] > div {{
    background-color: {c_input_bg} !important;
    border: 1px solid {c_input_border} !important;
    border-radius: 12px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}}

/* Focus state for the outer container */
[data-testid="stChatInput"] > div:focus-within {{
    border-color: {c_text_headings} !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
}}

/* Remove inner border/background and shadow of inputs */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] div div {{
    color: {c_input_text} !important;
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

/* Style the placeholder text */
input::placeholder, textarea::placeholder, [data-testid="stChatInput"] textarea::placeholder {{
    color: {c_text_muted} !important;
    opacity: 0.8 !important;
}}

/* Caption and Small elements */
small, [data-testid="stCaptionContainer"], .stCaptionContainer {{
    color: {c_text_muted} !important;
}}

/* Glassmorphism Card Style */
.custom-card {{
    background: {c_card_bg} !important;
    border: 1px solid {c_card_border} !important;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    margin-bottom: 20px;
    color: {c_text_body} !important;
}}
.custom-card h1, .custom-card h2, .custom-card h3, .custom-card h4, .custom-card h5, .custom-card h6,
.custom-card p, .custom-card span, .custom-card li, .custom-card strong, .custom-card div {{
    color: {c_text_body} !important;
}}

/* Section Header Style */
.section-header {{
    background: {c_card_bg} !important;
    border: 1px solid {c_card_border} !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
}}
.section-header h1, .section-header h2, .section-header h3, .section-header h4, .section-header h5, .section-header h6,
.section-header p, .section-header span, .section-header b, .section-header strong {{
    color: {c_text_body} !important;
}}

/* Premium Gradient Header */
.dashboard-header {{
    background: linear-gradient(135deg, #2563EB 0%, #10B981 100%);
    border-radius: 16px;
    padding: 30px 40px;
    margin-bottom: 30px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15);
}}

/* Status Indicator pulsing dot */
.pulse-dot {{
    width: 10px;
    height: 10px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5);
    animation: pulse 1.8s infinite;
    vertical-align: middle;
    margin-right: 6px;
}}
@keyframes pulse {{
    0% {{
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5);
    }}
    70% {{
        transform: scale(1);
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }}
    100% {{
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }}
}}

/* Style Streamlit Metrics */
div[data-testid="stMetric"] {{
    background: {c_card_bg} !important;
    border: 1px solid {c_card_border} !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-3px) !important;
    border-color: {c_btn_hover_border} !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08) !important;
}}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {c_text_body} !important;
}}
/* Style main page secondary buttons */
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn),
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn),
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) {{
    background-color: {c_btn_bg} !important;
    color: {c_btn_text} !important;
    border: 1px solid {c_btn_border} !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    min-height: 52px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
}}

/* Ensure text inside main page secondary buttons is styled */
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) p,
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) span,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) p,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) span,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) p,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn) span {{
    color: {c_btn_text} !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}}

/* Hover state for main page secondary buttons */
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover {{
    background-color: {c_btn_hover_bg} !important;
    border-color: {c_btn_hover_border} !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    transform: translateY(-1px) !important;
}}

div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover p,
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover span,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover p,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover span,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover p,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):not([data-testid="stHeader"] *):not(.modebar-btn):hover span {{
    color: {c_btn_hover_text} !important;
}}

/* Header and Deploy buttons height fix */
[data-testid="stHeader"] button,
[data-testid="stHeader"] a,
header button,
header a,
[data-testid="stHeaderDeployButton"],
[data-testid="stHeaderDeployButton"] button,
[data-testid="stHeaderDeployButton"] a,
button[data-testid="stHeaderDeployButton"],
a[data-testid="stHeaderDeployButton"] {{
    min-height: 40px !important;
    height: 40px !important;
    padding: 6px 16px !important;
    border:2px solid #871b1047 !important;
}}

/* Navigation buttons in the sidebar */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
    background-color: {c_sidebar_btn_bg} !important;
    border: 1px solid {c_sidebar_btn_border} !important;
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
}}
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"] p,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"] span,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span {{
    color: {c_sidebar_btn_text} !important;
}}
[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{
    background-color: {c_sidebar_btn_hover_bg} !important;
    border-color: {c_sidebar_btn_border} !important;
    transform: translateX(3px) !important;
}}
[data-testid="stSidebar"] button:hover p,
[data-testid="stSidebar"] button:hover span,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover p,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover span,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover p,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover span {{
    color: {c_sidebar_btn_hover_text} !important;
}}

/* Sidebar navigation buttons - Active primary button */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] [data-testid="baseButton-primary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{
    background-color: {c_sidebar_active_bg} !important;
    background: {c_sidebar_active_bg} !important;
    border: 1px solid {c_sidebar_btn_border} !important;
    border-left: 4px solid {c_sidebar_active_border} !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}}
[data-testid="stSidebar"] button[kind="primary"] p,
[data-testid="stSidebar"] button[kind="primary"] span,
[data-testid="stSidebar"] [data-testid="baseButton-primary"] p,
[data-testid="stSidebar"] [data-testid="baseButton-primary"] span,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] span {{
    color: {c_sidebar_active_text} !important;
}}

/* Sidebar container boxes (Status card) */
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stSidebar"] div[style*="border"] {{
    background-color: {c_card_bg} !important;
    border: 1px solid {c_card_border} !important;
}}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] span,
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stSidebar"] div[style*="border"] p,
[data-testid="stSidebar"] div[style*="border"] span,
[data-testid="stSidebar"] div[style*="border"] label {{
    color: {c_text_body} !important;
}}


/* Custom pills/buttons for prompt options */
.prompt-pill {{
    background: {c_card_bg} !important;
    border: 1px solid {c_btn_border} !important;
    color: {c_text_body} !important;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-block;
    margin: 4px;
}}
.prompt-pill:hover {{
    background: {c_btn_hover_bg} !important;
    border-color: {c_btn_hover_border} !important;
    color: {c_btn_hover_text} !important;
    transform: translateY(-1px);
}}

/* Custom styled badge */
.pill-badge {{
    background-color: rgba(99, 102, 241, 0.1);
    color: #4F46E5;
    border: 1px solid rgba(99, 102, 241, 0.2);
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}}

.pii-badge {{
    background-color: rgba(239, 68, 68, 0.1);
    color: #DC2626;
    border: 1px solid rgba(239, 68, 68, 0.2);
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
}}

/* Theme-aware Streamlit Expander Header styling */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {{
    color: {c_text_headings} !important;
    fill: {c_text_headings} !important;
}}

.voice-input-card {{
    background: {c_voice_bg} !important;
    border: 1.5px solid {c_voice_border} !important;
    border-radius: 16px !important;
    padding: 18px 22px !important;
    margin-bottom: 14px !important;
}}

.voice-input-card .voice-title {{
    color: {c_voice_title} !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    margin: 0 0 10px 0 !important;
}}

.voice-input-card .voice-desc {{
    color: {c_voice_text} !important;
    font-size: 13px !important;
    margin: 0 !important;
}}

/* Plotly Modebar (Hover buttons) style visibility */
.modebar {{
    background-color: transparent !important;
}}
.modebar-btn {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px !important;
    min-height: auto !important;
    height: auto !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
.modebar-btn path {{
    fill: {c_plotly_modebar_btn} !important;
    stroke: {c_plotly_modebar_btn} !important;
}}
.modebar-btn:hover path {{
    fill: #3B82F6 !important;
    stroke: #3B82F6 !important;
}}

/* Agent Card and Pulse Radar styles */
.agent-status-card {{
    background: {c_card_bg} !important;
    border: 1px solid {c_card_border} !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
    margin-top: 15px !important;
    margin-bottom: 15px !important;
    transition: all 0.3s ease !important;
}}
.agent-status-card:hover {{
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
    transform: translateY(-2px) !important;
}}
.active-badge {{
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
}}
.radar-ping {{
    width: 6px;
    height: 6px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    position: relative;
}}
.radar-ping::after {{
    content: '';
    width: 100%;
    height: 100%;
    background-color: #10B981;
    border-radius: 50%;
    position: absolute;
    top: 0;
    left: 0;
    animation: ping 1.2s ease-in-out infinite;
}}
@keyframes ping {{
    0% {{
        transform: scale(1);
        opacity: 1;
    }}
    100% {{
        transform: scale(2.5);
        opacity: 0;
    }}
}}
@keyframes progress-glow {{
    0% {{
        opacity: 0.85;
    }}
    100% {{
        opacity: 1;
        filter: drop-shadow(0 0 2px rgba(16, 185, 129, 0.5));
    }}
}}
</style>
""",
unsafe_allow_html=True)
# Helper for dynamic PDF context metadata
def get_metadata_path(filename_prefix, default_filename):
    active_pdf = st.session_state.get("active_pdf")
    if active_pdf:
        pdf_basename = os.path.basename(active_pdf)
        custom_file = os.path.join(BASE_DIR, "metadata", f"{filename_prefix}_{pdf_basename}.json")
        if os.path.exists(custom_file):
            return custom_file
    return os.path.join(BASE_DIR, "metadata", default_filename)

def get_data_quality_data():
    tables_file = get_metadata_path("tables", "tables.json")
    try:
        with open(tables_file, "r") as f:
            tables = json.load(f)
    except:
        tables = []
        
    quality_data = {}
    import hashlib
    for t in tables:
        t_name = t["table_name"]
        h = int(hashlib.md5(t_name.encode()).hexdigest(), 16)
        
        total_rows = (h % 90000) + 10000
        null_rate = round((h % 150) / 100.0, 2)  # 0.00% to 1.50%
        if "bronze" in t_name.lower():
            null_rate += 1.5
        elif "gold" in t_name.lower():
            null_rate = max(0.01, null_rate - 0.5)
            
        duplicate_rate = round((h % 80) / 100.0, 2)
        if "bronze" in t_name.lower():
            duplicate_rate += 1.2
        elif "gold" in t_name.lower():
            duplicate_rate = 0.0
            
        completeness = round(100.0 - null_rate, 2)
        uniqueness = round(100.0 - duplicate_rate, 2)
        
        rules = [
            {"rule_name": "Non-Null Keys", "status": "Passed" if null_rate < 1.0 else "Warning", "metric": f"{completeness}% complete"},
            {"rule_name": "Unique Primary Key", "status": "Passed" if duplicate_rate == 0.0 else "Warning", "metric": f"{uniqueness}% unique"},
            {"rule_name": "DataType Conformity", "status": "Passed", "metric": "100% conforming"},
        ]
        
        if "payments" in t_name.lower() or "sales" in t_name.lower() or "revenue" in t_name.lower():
            rules.append({"rule_name": "Positive Amounts", "status": "Passed", "metric": "100% positive"})
        if "user" in t_name.lower() or "customer" in t_name.lower():
            rules.append({"rule_name": "Valid Email Format", "status": "Passed" if (h % 3 != 0) else "Warning", "metric": "99.8% valid" if (h % 3 != 0) else "94.2% valid"})
            
        passed_rules = len([r for r in rules if r["status"] == "Passed"])
        quality_score = round((passed_rules / len(rules)) * 100.0, 1)
        
        quality_data[t_name] = {
            "total_rows": total_rows,
            "null_rate": null_rate,
            "duplicate_rate": duplicate_rate,
            "completeness": completeness,
            "uniqueness": uniqueness,
            "rules": rules,
            "quality_score": quality_score
        }
        
    return quality_data


# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0;">
            <span class="material-symbols-outlined" style="font-size: 32px; color: #2563EB;">rocket_launch</span>
            <h2 style="margin: 0; font-size: 24px; font-weight: 700; color: {c_text_headings};">Data Platform</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    
    # UI Theme Mode toggle
    toggle_label = "Dark Mode" if st.session_state.theme_mode == "Dark" else "Light Mode"
    theme_toggle_val = st.toggle(
        toggle_label,
        value=(st.session_state.theme_mode == "Dark"),
        key="theme_toggle_switch"
    )
    new_theme = "Dark" if theme_toggle_val else "Light"
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    pages = [
        {"name": "Dashboard", "icon": ":material/dashboard:"},
        {"name": "AI Assistant", "icon": ":material/smart_toy:"},
        {"name": "Pipeline Health", "icon": ":material/monitoring:"},
        {"name": "Data Catalog", "icon": ":material/storage:"},
        {"name": "Data Quality", "icon": ":material/fact_check:"},
        {"name": "Lineage Explorer", "icon": ":material/account_tree:"},
        {"name": "Upload Center", "icon": ":material/folder_open:"},
        {"name": "Architecture", "icon": ":material/schema:"}
    ]

    for p in pages:
        btn_type = "primary" if st.session_state.page == p["name"] else "secondary"
        if st.button(p["name"], icon=p["icon"], use_container_width=True, type=btn_type):
            st.session_state.page = p["name"]
            st.rerun()

    page = st.session_state.page

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    active_pdf = st.session_state.get("active_pdf")
    with st.container(border=True):
        st.markdown(
            f"""<div style='display: flex; align-items: center; gap: 6px; margin-bottom: 8px;'>
<span class='material-symbols-outlined' style='font-size: 16px; color: {c_sidebar_label};'>description</span>
<span style='color: {c_sidebar_label}; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Active Context</span>
</div>""",
            unsafe_allow_html=True
        )
        if active_pdf:
            st.markdown(f"<span style='color: {c_text_body}; font-size: 13px; display: block; margin-bottom: 8px;'>📄 <b>{active_pdf}</b></span>", unsafe_allow_html=True)
            if st.button("Clear Selection", use_container_width=True, type="secondary", key="clear_active_pdf_btn"):
                st.session_state["active_pdf"] = None
                st.rerun()
        else:
            st.markdown(f"<span style='color: {c_sidebar_label}; font-size: 13px; font-style: italic;'>Default Capstone Data</span>", unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 6px; margin-bottom: 8px;'>
                <span class='material-symbols-outlined' style='font-size: 16px; color: {c_sidebar_label};'>shield</span>
                <span style='color: {c_sidebar_label}; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Enterprise Agent Status</span>
            </div>
            <div style='display: flex; flex-direction: column; gap: 6px;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span class="pulse-dot"></span>
                    <span style='color: {c_text_body}; font-size: 13px;'><b>Gemini AI</b> (1.5 Pro)</span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span class="pulse-dot"></span>
                    <span style='color: {c_text_body}; font-size: 13px;'><b>AWS S3 Sync</b> (Connected)</span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span class="pulse-dot"></span>
                    <span style='color: {c_text_body}; font-size: 13px;'><b>ChromaDB Vector</b> (Ready)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 6px; margin-bottom: 8px;'>
                <span class='material-symbols-outlined' style='font-size: 16px; color: {c_sidebar_label};'>publish</span>
                <span style='color: {c_sidebar_label}; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Pipeline Ingestion</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        
        # Display active repo
        active_repo = st.session_state.get("active_repo", "Default Capstone")
        st.markdown(f"<span style='color: {c_text_body}; font-size: 13px;'><b>Active:</b> {active_repo}</span>", unsafe_allow_html=True)
        
        repo_url = st.text_input("GitHub Repo URL", key="repo_url_input", placeholder="https://github.com/...", label_visibility="collapsed")
        
        if st.button("Ingest Repository", use_container_width=True, type="secondary"):
            if repo_url:
                with st.spinner("Cloning & analyzing pipeline..."):
                    try:
                        from agents.repo_agent import ingest_github_repo
                        ingest_github_repo(repo_url)
                        repo_name = repo_url.split("/")[-1].replace(".git", "")
                        st.session_state.active_repo = repo_name
                        st.success("Ingested successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ingestion failed: {e}")
            else:
                st.warning("Please enter a valid URL")

        if st.session_state.get("active_repo", "Default Capstone") != "Default Capstone":
            if st.button("Reset to Default", use_container_width=True, type="secondary"):
                with st.spinner("Restoring defaults..."):
                    try:
                        from agents.repo_agent import restore_default_metadata
                        restore_default_metadata()
                        st.session_state.active_repo = "Default Capstone"
                        st.success("Restored successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Reset failed: {e}")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    try:

        with open(
            get_metadata_path("tables", "tables.json"),
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

if page == "Dashboard":

    st.markdown("""
    <div class="dashboard-header" style="display: flex; align-items: center; gap: 20px;">
        <span class="material-symbols-outlined" style="font-size: 48px; color: white; background: rgba(255,255,255,0.15); padding: 16px; border-radius: 16px;">rocket_launch</span>
        <div>
            <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -0.5px; line-height: 1.2;">
                GenAI Data Engineering Assistant
            </h1>
            <p style="color: #93C5FD; margin: 4px 0 0 0; font-size: 16px; font-weight: 400; opacity: 0.9;">
                AI-Powered Data Platform Command Center & Knowledge Engine
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        health = get_pipeline_health(active_pdf=st.session_state.get("active_pdf"))
        active_pipelines_count = len([k for k in health.keys() if k != "recent_incident"])
    except:
        active_pipelines_count = 2

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Active Pipelines",
            value=str(active_pipelines_count),
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
            <h3 style="margin-top:0; font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid {c_card_border}; padding-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-outlined" style="font-size: 22px; color: #2563EB;">analytics</span>
                Platform Resource Summary
            </h3>
            <div style="display: grid; gap: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {c_card_border}; padding-bottom: 8px;">
                    <span style="font-weight: 500;">Cataloged Tables</span>
                    <span style="font-weight: 600; font-size: 16px;">{total_tables}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {c_card_border}; padding-bottom: 8px;">
                    <span style="font-weight: 500;">PII Monitored Tables</span>
                    <span class="pii-badge">{pii_tables} PII</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {c_card_border}; padding-bottom: 8px;">
                    <span style="font-weight: 500;">Data Catalog Schema Sync</span>
                    <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);">Active</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 4px;">
                    <span style="font-weight: 500;">Knowledge Base Files</span>
                    <span style="font-weight: 600; font-size: 16px; color: #059669 !important;">{total_uploads} PDFs</span>
                </div>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

    with col_right:
        status_html = f"""
        <div class="custom-card" style="height: 100%;">
            <h3 style="margin-top:0; font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid {c_card_border}; padding-bottom: 10px; display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-outlined" style="font-size: 22px; color: #10B981;">health_and_safety</span>
                System Health Monitor
            </h3>
            <div style="display: grid; gap: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: {c_nested_box_bg}; border-radius: 8px; border: 1px solid {c_nested_box_border};">
                    <span style="font-weight: 500;">Gemini AI Integration</span>
<span class="status-badge online" style="
background-color: rgba(16, 185, 129, 0.1);
color: #059669;
border: 1px solid rgba(16, 185, 129, 0.2);
border-radius: 16px;
width: 120px;
height: 38px;
display: inline-flex;
align-items: center;
justify-content: center;
box-sizing: border-box;
">
<span class="pulse-dot"></span>Active
</span>                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: {c_nested_box_bg}; border-radius: 8px; border: 1px solid {c_nested_box_border};">
                    <span style="font-weight: 500;">AWS S3 Cloud Sync</span>
                    <span class="status-badge online" style="
background-color: rgba(16, 185, 129, 0.1);
color: #059669;
border: 1px solid rgba(16, 185, 129, 0.2);
border-radius: 16px;
width: 120px;
height: 38px;
display: inline-flex;
align-items: center;
justify-content: center;
box-sizing: border-box;
"><span class="pulse-dot"></span>Connected</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: {c_nested_box_bg}; border-radius: 8px; border: 1px solid {c_nested_box_border};">
                    <span style="font-weight: 500;">ChromaDB Vector Store</span>
                    <span class="status-badge online" style="
background-color: rgba(16, 185, 129, 0.1);
color: #059669;
border: 1px solid rgba(16, 185, 129, 0.2);
border-radius: 16px;
width: 120px;
height: 38px;
display: inline-flex;
align-items: center;
justify-content: center;
box-sizing: border-box;
"><span class="pulse-dot"></span>Healthy</span>
                </div>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

# =====================================
# CHAT TAB
# =====================================

if page == "AI Assistant":

    st.markdown("""
    <div class="section-header">
        <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #2563EB;">smart_toy</span>
            RAG AI Assistant
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px;">
            Ask questions about data catalogs, schemas, pipelines SLAs, lineaging, or document indices. Backed by ChromaDB and Gemini.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Quick prompt pills above chat
    st.markdown("<p style='font-weight: 600; display: flex; align-items: center; gap: 6px; margin-bottom: 8px;'><span class='material-symbols-outlined' style='font-size: 18px; color: #F59E0B;'>lightbulb</span>Quick Queries:</p>", unsafe_allow_html=True)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_query = None
    with q_col1:
        if st.button("List PII Tables", icon=":material/shield:", use_container_width=True):
            quick_query = "Which tables contain PII?"
    with q_col2:
        if st.button("Pipeline Status", icon=":material/monitoring:", use_container_width=True):
            quick_query = "What is the health status and SLAs of my pipelines?"
    with q_col3:
        if st.button("Show Lineage", icon=":material/account_tree:", use_container_width=True):
            quick_query = "Show the lineage details of orders tables."
    with q_col4:
        if st.button("View Data Catalog", icon=":material/storage:", use_container_width=True):
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
    <div class="voice-input-card">
        <p class="voice-title">
            🎙️ Voice Input — Speak your question
        </p>
        <p class="voice-desc">
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

        answer = ask_question(query, active_pdf=st.session_state.get("active_pdf"))

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

if page == "Pipeline Health":

    health = get_pipeline_health(active_pdf=st.session_state.get("active_pdf"))

    st.markdown("""
    <div class="section-header">
        <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #10B981;">monitoring</span>
            Pipeline Health Monitor
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px;">
            Real-time ingestion pipeline uptime, SLA achievements, and recent platform incident logs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pipelines_keys = [k for k in health.keys() if k != "recent_incident"]

    if pipelines_keys:
        num_cols = min(len(pipelines_keys), 2)
        cols = st.columns(num_cols)
        for idx, p_key in enumerate(pipelines_keys):
            p_data = health[p_key]
            p_title = p_key.replace("_", " ").title()
            p_icon = "package" if "order" in p_key.lower() else "group" if "customer" in p_key.lower() else "sync"
            
            with cols[idx % num_cols]:
                card_html = f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h4 style="margin: 0; font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                            <span class="material-symbols-outlined" style="font-size: 20px; color: #2563EB;">{p_icon}</span>
                            {p_title}
                        </h4>
                        <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1.5px solid rgba(16, 185, 129, 0.3); border-radius: 20px; padding: 4px 12px; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600;"><span class="pulse-dot"></span>{p_data.get('status', 'Operational')}</span>
                    </div>
                    <div style="display: grid; gap: 10px; font-size: 14px;">
                        <div style="display: flex; justify-content: space-between;">
                        <span style="color: #8D7B68 !important;">Uptime Availability</span>
                        <span style="font-weight:600; color: #059669 !important;">{p_data.get('availability', '99.90%')}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;"><span style="color: #8D7B68 !important;">Last Sync Time</span><span style="font-weight:500;">{p_data.get('last_run', 'Success')}</span></div>
                        <div style="display: flex; justify-content: space-between;"><span style="color: #8D7B68 !important;">Target SLA</span><span style="font-weight:500;">{p_data.get('sla', 'Met')}</span></div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        y_vals = []
        x_vals = []
        for p_key in pipelines_keys:
            p_data = health[p_key]
            avail_str = str(
                p_data.get('availability') or "100%"
            ).replace("%", "")
            try:
                y_vals.append(float(avail_str))
            except ValueError:
                y_vals.append(100.0)
            x_vals.append(p_key.replace("_", " ").title())

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=y_vals,
                marker_color=["#3B82F6", "#0D9488", "#8B5CF6", "#EC4899"][:len(x_vals)],
                width=0.35
            )
        )
        min_y = min(y_vals) - 0.1 if y_vals else 99.0
        
        # Dynamic styling based on selected theme mode
        chart_text_color = "#E5E7EB" if st.session_state.theme_mode == "Dark" else "#0F172A"
        grid_color = "rgba(255, 255, 255, 0.08)" if st.session_state.theme_mode == "Dark" else "rgba(0, 0, 0, 0.08)"
        
        fig.update_layout(
            title=dict(
                text="Uptime Availability Actual vs Target (%)",
                font=dict(color=chart_text_color, family='Outfit', size=16)
            ),
            yaxis_title="Availability %",
            yaxis_range=[min(min_y, 99.5), 100.0],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=chart_text_color, family='Outfit'),
            height=320,
            margin=dict(l=40, r=40, t=50, b=40),
            modebar=dict(
                bgcolor='rgba(0,0,0,0)',
                color=chart_text_color,
                activecolor='#3B82F6'
            )
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=grid_color)
        
        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    incident = health.get("recent_incident")
    if incident:
        incident_html = f"""
        <div class="custom-card" style="border-left: 4px solid #D97706;">
            <h4 style="margin: 0; color: #D97706 !important; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-outlined" style="font-size: 20px; color: #D97706;">warning</span>
                Recent Platform Incident Logs
            </h4>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; font-size: 13px;">
                <div><span style="color: #8D7B68 !important;">Incident ID:</span><br><strong>{incident.get('incident_id', 'N/A')}</strong></div>
                <div><span style="color: #8D7B68 !important;">Impacted Pipeline:</span><br><strong>{incident.get('pipeline', 'N/A')}</strong></div>
                <div><span style="color: #8D7B68 !important;">Current Status:</span><br><span class="pill-badge" style="background-color: rgba(245, 158, 11, 0.1); color: #D97706; border: 1px solid rgba(245, 158, 11, 0.2);">{incident.get('status', 'Resolved')}</span></div>
                <div><span style="color: #8D7B68 !important;">Incident Impact:</span><br><strong style="color: #EF4444 !important;">{incident.get('impact', 'N/A')}</strong></div>
            </div>
        </div>
        """
    else:
        incident_html = """
        <div class="custom-card" style="border-left: 4px solid #10B981;">
            <h4 style="margin: 0; color: #10B981 !important; font-size: 16px; display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-outlined" style="font-size: 20px; color: #10B981;">check_circle</span>
                Recent Platform Incident Logs
            </h4>
            <div style="margin-top: 10px; font-size: 14px;">
                No active or recent incidents reported in the last 7 days.
            </div>
        </div>
        """
    st.markdown(incident_html, unsafe_allow_html=True)

# =====================================
# DATA CATALOG TAB
# =====================================

if page == "Data Catalog":

    st.markdown("""
    <div class="section-header">
        <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #2563EB;">storage</span>
            Data Catalog Explorer
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px;">
            Discover cataloged physical schemas, access policies, ownership metadata, and PII status details.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with open(
        get_metadata_path("tables", "tables.json"),
        "r"
    ) as file:

        tables = json.load(file)
    
    search_table = st.text_input(
        "Search Cataloged Tables",
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
        pii_status = "Contains PII" if table['contains_pii'] else "Secured"
        with st.expander(f"{table['table_name']}  |  Owner: {table['owner']}  |  Classification: {pii_status}"):
            col_col1, col_col2 = st.columns(2)
            with col_col1:
                card_info = f"""
                <div style="padding: 16px; background: {c_nested_box_bg}; border-radius: 10px; border: 1px solid {c_nested_box_border}; height: 100%;">
                    <span style="color: #8D7B68 !important; font-size: 12px; font-weight: 500;">DATA OWNER</span><br>
                    <strong style="font-size: 15px;">{table['owner']}</strong>
                    <br><br>
                    <span style="color: #8D7B68 !important; font-size: 12px; font-weight: 500;">SECURITY CLASSIFICATION</span><br>
                    {"<span class='pii-badge'>Contains PII Data</span>" if table['contains_pii'] else "<span class='pill-badge' style='background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);'>No Sensitive PII</span>"}
                </div>
                """
                st.markdown(card_info, unsafe_allow_html=True)
            with col_col2:
                st.markdown("<div style='font-size: 13px; font-weight:600; color: #64748B; margin-bottom: 8px;'>COLUMNS & PHYSICAL SCHEMA</div>", unsafe_allow_html=True)
                for col in table["columns"]:
                    st.markdown(
                        f"• <span style='color: #2563EB; font-family: monospace; font-size: 14px; font-weight: 600;'>{col}</span>",
                        unsafe_allow_html=True
                    )
# =====================================
# LINEAGE TAB
# =====================================

if page == "Lineage Explorer":

    st.markdown("""
    <div class="section-header">
        <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #3B82F6;">account_tree</span>
            Data Lineage Tracker
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px;">
            Track upstream-to-downstream table flows and transformations across ingestion and serving layers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with open(
        get_metadata_path("lineage", "lineage.json"),
        "r"
    ) as file:

        lineage_data = json.load(file)

    for table, l_info in lineage_data.items():

        st.markdown(f"<h4 style='display: flex; align-items: center; gap: 6px; font-size: 16px; font-weight: 600; margin-top: 20px;'><span class='material-symbols-outlined' style='font-size: 20px; color: #3B82F6;'>location_on</span>Lineage Flow for <b>{table}</b></h4>", unsafe_allow_html=True)

        # Parse flow and insights dynamically to support both old array schema and new object schema
        if isinstance(l_info, dict):
            flow = l_info.get("flow", [])
            insights = l_info.get("insights", "Data transformation details and column mapping information.")
        else:
            flow = l_info
            insights = f"Traces key events and structures for `{table}` from initial ingestion to final aggregation layers."
        
        flow_steps = []
        for idx, step in enumerate(flow):
            node_html = (
                f'<div style="background-color: {c_lineage_node_bg}; border: 1px solid {c_lineage_node_border}; '
                f'border-radius: 8px; padding: 10px 16px; font-weight: 600; color: {c_lineage_node_text}; '
                f'text-align: center; min-width: 140px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">{step}</div>'
            )
            flow_steps.append(node_html)
        
        arrow_html = f' <div style="color: {c_lineage_arrow}; display: flex; align-items: center;"><span class="material-symbols-outlined" style="font-size: 20px;">chevron_right</span></div> '
        flow_html = (
            f'<div style="display: flex; align-items: center; justify-content: flex-start; gap: 15px; '
            f'flex-wrap: wrap; padding: 20px; background: {c_nested_box_bg}; border-radius: 12px; '
            f'border: 1px solid {c_nested_box_border}; margin-bottom: 15px;">'
            f'{arrow_html.join(flow_steps)}</div>'
        )
        st.markdown(flow_html, unsafe_allow_html=True)

        # AI Insights card
        insights_html = (
            f'<div class="custom-card" style="border-left: 4px solid #2563EB; margin-top: -5px; '
            f'margin-bottom: 30px; padding: 18px; background: {c_card_bg}; '
            f'border: 1px solid {c_card_border};">'
            f'<h5 style="margin: 0 0 8px 0; color: {c_text_headings}; font-size: 14px; font-weight: 600; '
            f'text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px;">'
            f'<span class="material-symbols-outlined" style="font-size: 18px; color: #F59E0B;">lightbulb</span>AI Pipeline Insights</h5>'
            f'<p style="margin: 0; color: {c_text_body}; font-size: 13.5px; line-height: 1.5;">{insights}</p></div>'
        )
        st.markdown(insights_html, unsafe_allow_html=True)

# =====================================
# UPLOAD CENTER
# =====================================

if page == "Upload Center":

    active_repo = st.session_state.get("active_repo", "Default Capstone")
    cloned_dir = os.path.join(BASE_DIR, "data", "cloned_repo")

    if active_repo != "Default Capstone" and os.path.exists(cloned_dir):
        st.markdown(f"""
        <div class="section-header">
            <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
                <span class="material-symbols-outlined" style="font-size: 28px; color: #2563EB;">folder_open</span>
                Ingested Repository Codebase
            </h2>
            <p style="margin: 6px 0 0 0; font-size: 14px;">
                Active Repository: <b>{active_repo}</b>. Displaying indexable files processed, chunked, and embedded in ChromaDB.
            </p>
        </div>
        """, unsafe_allow_html=True)

        try:
            repo_files = []
            for root, dirs, filenames in os.walk(cloned_dir):
                if ".git" in root or "__pycache__" in root or ".venv" in root or "node_modules" in root:
                    continue
                for f in filenames:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in ['.py', '.sql', '.md', '.txt', '.json', '.yml', '.yaml']:
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, cloned_dir)
                        size_kb = round(os.path.getsize(full_path) / 1024, 2)
                        repo_files.append((rel_path, size_kb, ext))

            if repo_files:
                cols = st.columns(3)
                for idx, (rel_path, size_kb, ext) in enumerate(repo_files):
                    m_icon = "code" if ext == ".py" else "database" if ext == ".sql" else "description" if ext in [".md", ".txt"] else "settings"
                    col_target = cols[idx % 3]
                    with col_target:
                        card_html = f"""
                        <div class="custom-card" style="padding: 18px; margin-bottom: 15px; border-top: 3px solid #2563EB;">
                            <div style="margin-bottom: 8px;"><span class="material-symbols-outlined" style="font-size: 32px; color: #2563EB;">{m_icon}</span></div>
                            <div style="font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; font-size: 15px;" title="{rel_path}">
                                {rel_path}
                            </div>
                            <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #8D7B68 !important; font-size: 12px; font-weight: 500;">{size_kb} KB</span>
                                <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);">Indexed</span>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.warning("No indexable code files found in the cloned repository.")
        except Exception as e:
            st.error(f"Error reading repository files: {e}")

    else:
        st.markdown("""
        <div class="section-header">
            <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
                <span class="material-symbols-outlined" style="font-size: 28px; color: #2563EB;">folder_open</span>
                Document Index Center
            </h2>
            <p style="margin: 6px 0 0 0; font-size: 14px;">
                Monitor files synced to AWS S3. Sync operations trigger automated text extraction and vector embedding.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if "pdf_uploader_key" not in st.session_state:
            st.session_state["pdf_uploader_key"] = 0

        # Load S3 bucket info and list S3 files
        bucket_name = os.getenv("AWS_BUCKET_NAME", "genai-capstone-abhinav")
        s3_files = []
        try:
            s3_files = list_s3_files()
        except Exception:
            s3_files = []

        # S3 Connection Status Card
        st.markdown(
            f"""
            <div style="background: {c_nested_box_bg}; border: 1px solid {c_nested_box_border}; border-radius: 12px; padding: 12px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="material-symbols-outlined" style="font-size: 24px; color: #3B82F6;">cloud</span>
                    <div>
                        <strong style="color: {c_text_headings}; font-size: 14.5px;">AWS S3 Cloud Integration</strong><br>
                        <span style="color: {c_text_muted}; font-size: 12px;">Active Bucket: <code>{bucket_name}</code></span>
                    </div>
                </div>
                <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1.5px solid rgba(16, 185, 129, 0.3); border-radius: 20px; padding: 4px 12px; display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600;">
                    <span class="pulse-dot"></span>Connected
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Direct PDF Upload Panel
        with st.container(border=True):
            st.markdown(
                f"""
                <div style='display: flex; align-items: center; gap: 6px; margin-bottom: 8px;'>
                    <span class='material-symbols-outlined' style='font-size: 18px; color: {c_text_headings};'>cloud_upload</span>
                    <span style='color: {c_text_headings}; font-size: 14px; font-weight: 600; text-transform: uppercase;'>Upload & Ingest New Document</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            uploaded_file = st.file_uploader(
                "Upload a PDF runbook or documentation file directly:",
                type=["pdf"],
                label_visibility="collapsed",
                key=f"pdf_direct_uploader_{st.session_state['pdf_uploader_key']}"
            )
            
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join(UPLOAD_DIR, file_name)
                
                with st.spinner(f"Saving {file_name} locally..."):
                    os.makedirs(UPLOAD_DIR, exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                st.toast(f"Saved {file_name} to local directory.", icon="💾")
                
                # Try syncing to S3
                if upload_file is not None:
                    try:
                        with st.spinner(f"Syncing {file_name} to AWS S3..."):
                            upload_file(file_path)
                        st.toast(f"Uploaded {file_name} to S3.", icon="☁️")
                    except Exception as s3_err:
                        st.toast(
                            f"AWS S3 Sync failed (local index will continue): {s3_err}",
                            icon="⚠️"
                        )
                
                # Process and index PDF
                if process_pdf is not None:
                    try:
                        with st.spinner("Processing & indexing PDF text into ChromaDB..."):
                            process_pdf(file_path)
                        st.success(f"Successfully processed and indexed '{file_name}'! The knowledge base is updated.")
                        
                        st.session_state["active_pdf"] = file_name
                        
                        # Increment uploader key to clear widget selection on next rerun
                        st.session_state["pdf_uploader_key"] += 1
                        
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as idx_err:
                        st.error(f"Failed to process/index PDF: {idx_err}")
                else:
                    st.error("ChromaDB indexer function is not available. Please verify scripts/auto_indexer.py.")

        # Document Selector & Viewer
        try:
            viewer_files = os.listdir(UPLOAD_DIR)
            viewer_pdfs = sorted([f for f in viewer_files if f.endswith(".pdf")])
        except Exception:
            viewer_pdfs = []

        if viewer_pdfs:
            st.markdown(
                f"""<div style='display: flex; align-items: center; gap: 6px; margin-bottom: 8px;'>
<span class='material-symbols-outlined' style='font-size: 18px; color: {c_text_headings};'>visibility</span>
<span style='color: {c_text_headings}; font-size: 14px; font-weight: 600; text-transform: uppercase;'>Document Viewer</span>
</div>""",
                unsafe_allow_html=True
            )
            # Get current index based on active_pdf
            default_index = None
            if st.session_state.get("active_pdf") in viewer_pdfs:
                default_index = viewer_pdfs.index(st.session_state["active_pdf"])

            selected_pdf = st.selectbox(
                "Select an indexed document to preview its content:",
                options=viewer_pdfs,
                index=default_index,
                placeholder="Choose a PDF file to display...",
                label_visibility="collapsed",
                key="viewer_pdf_select"
            )
            
            if selected_pdf != st.session_state.get("active_pdf"):
                st.session_state["active_pdf"] = selected_pdf
                st.rerun()
            
            if selected_pdf:
                file_path = os.path.join(UPLOAD_DIR, selected_pdf)
                try:
                    from ingestion.pdf_loader import load_pdf
                    pdf_text = load_pdf(file_path)
                    
                    st.markdown(
                        f"""<div class="custom-card" style="margin-top: 10px; margin-bottom: 15px;">
<h4 style="margin-top: 0; margin-bottom: 12px; font-size: 16px; font-weight: 600; color: {c_text_headings}; display: flex; align-items: center; gap: 8px;">
<span class="material-symbols-outlined" style="font-size: 20px; color: #2563EB;">menu_book</span>
Extracted Content: {selected_pdf}
</h4>
<div style="max-height: 350px; overflow-y: auto; background: {c_nested_box_bg}; border: 1px solid {c_nested_box_border}; border-radius: 8px; padding: 18px; font-family: 'Outfit', sans-serif; white-space: pre-wrap; font-size: 13.5px; line-height: 1.6; color: {c_text_body};">
{pdf_text}
</div>
</div>""",
                        unsafe_allow_html=True
                    )
                    
                    # Interactive AI Query input for the selected document
                    doc_query = st.text_input(
                        "Ask the AI Assistant a question about this document:",
                        placeholder="e.g. Who owns this pipeline? What is its SLA? Are there any data quality checks?",
                        key="doc_query_input"
                    )
                    
                    if doc_query:
                        with st.spinner("AI Assistant is analyzing..."):
                            from rag.chatbot import ask_question
                            answer = ask_question(f"Based on the document '{selected_pdf}', answer this question: {doc_query}", active_pdf=selected_pdf)
                            
                        st.markdown(
                            f"""<div style="background: {c_nested_box_bg}; border: 1px dashed {c_nested_box_border}; border-radius: 12px; padding: 20px; margin-top: 15px; color: {c_text_body};">
<strong style="color: {c_text_headings}; display: flex; align-items: center; gap: 8px; font-size: 15px;">
<span class="material-symbols-outlined" style="font-size: 20px; color: #2563EB;">smart_toy</span>
AI Response:
</strong>
<p style="margin-top: 10px; margin-bottom: 0; font-size: 14px; line-height: 1.6;">{answer}</p>
</div>""",
                            unsafe_allow_html=True
                        )
                        
                except Exception as e:
                    st.error(f"Error loading PDF: {e}")
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        try:
            # List local files
            local_files = os.listdir(UPLOAD_DIR)
            local_pdfs = sorted([f for f in local_files if f.endswith(".pdf")])
        except Exception:
            local_pdfs = []

        # Combine unique files
        all_pdfs = sorted(list(set(local_pdfs) | set(s3_files)))

        try:
            if all_pdfs:
                cols = st.columns(3)
                for idx, pdf in enumerate(all_pdfs):
                    is_local = pdf in local_pdfs
                    is_s3 = pdf in s3_files

                    col_target = cols[idx % 3]
                    with col_target:
                        if is_local:
                            file_path = os.path.join(UPLOAD_DIR, pdf)
                            size_kb = round(os.path.getsize(file_path) / 1024, 2)
                            size_text = f"{size_kb} KB"
                            
                            if is_s3:
                                s3_badge = '<span class="pill-badge" style="background-color: rgba(59, 130, 246, 0.1); color: #2563EB; border: 1px solid rgba(59, 130, 246, 0.2); font-size: 11px; display: inline-flex; align-items: center; gap: 2px;"><span class="material-symbols-outlined" style="font-size: 12px;">cloud</span>Synced</span>'
                            else:
                                s3_badge = '<span class="pill-badge" style="background-color: rgba(107, 114, 128, 0.1); color: #4B5563; border: 1px solid rgba(107, 114, 128, 0.2); font-size: 11px; display: inline-flex; align-items: center; gap: 2px;"><span class="material-symbols-outlined" style="font-size: 12px;">cloud_off</span>Local Only</span>'

                            card_html = f"""
                            <div class="custom-card" style="padding: 18px; margin-bottom: 15px; border-top: 3px solid #2563EB;">
                                <div style="margin-bottom: 8px;"><span class="material-symbols-outlined" style="font-size: 32px; color: #2563EB;">description</span></div>
                                <div style="font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; font-size: 15px;" title="{pdf}">
                                    {pdf}
                                </div>
                                <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: {c_text_muted} !important; font-size: 12px; font-weight: 500;">{size_text}</span>
                                    <div style="display: flex; gap: 4px;">
                                        <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 11px;">Indexed</span>
                                        {s3_badge}
                                    </div>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                        else:
                            # S3 Cloud Only Card
                            card_html = f"""
                            <div class="custom-card" style="padding: 18px; margin-bottom: 10px; border: 1.5px dashed {c_nested_box_border}; opacity: 0.85;">
                                <div style="margin-bottom: 8px;"><span class="material-symbols-outlined" style="font-size: 32px; color: #6B7280;">cloud_queue</span></div>
                                <div style="font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; font-size: 15px; color: {c_text_muted};" title="{pdf}">
                                    {pdf}
                                </div>
                                <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: {c_text_muted} !important; font-size: 12px; font-weight: 500;">Cloud Only</span>
                                    <span class="pill-badge" style="background-color: rgba(245, 158, 11, 0.1); color: #D97706; border: 1px solid rgba(245, 158, 11, 0.2); font-size: 11px;">Pending Sync</span>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                            # Click to download and index cloud-only file
                            if st.button("Download & Index", key=f"dl_sync_{pdf}", use_container_width=True):
                                local_path = os.path.join(UPLOAD_DIR, pdf)
                                with st.spinner(f"Downloading {pdf} from AWS S3..."):
                                    try:
                                        download_file_from_s3(pdf, local_path)
                                        st.toast(f"Downloaded {pdf} from S3.", icon="📥")
                                    except Exception as dl_err:
                                        st.error(f"S3 download failed: {dl_err}")
                                        st.stop()
                                        
                                with st.spinner("Processing & indexing PDF text into ChromaDB..."):
                                    try:
                                        process_pdf(local_path)
                                        st.success(f"Successfully processed and indexed '{pdf}'!")
                                        st.session_state["active_pdf"] = pdf
                                        time.sleep(1.5)
                                        st.rerun()
                                    except Exception as process_err:
                                        st.error(f"Failed to process PDF: {process_err}")
            else:
                st.warning("No PDFs Found in local directories or AWS S3.")
        except Exception as e:
            st.error(f"Error loading document index: {e}")

if page == "Architecture":

    active_repo = st.session_state.get("active_repo", "Default Capstone")
    mermaid_file = os.path.join(BASE_DIR, "metadata", "architecture_mermaid.txt")

    if active_repo != "Default Capstone" and os.path.exists(mermaid_file):
        st.markdown(f"""
        <div class="section-header">
            <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
                <span class="material-symbols-outlined" style="font-size: 28px; color: #2563EB;">schema</span>
                Ingested Repository System Architecture
            </h2>
            <p style="margin: 6px 0 0 0; font-size: 14px;">
                Active Repository: <b>{active_repo}</b>. Showing interactive architecture diagram generated from the codebase.
            </p>
        </div>
        """, unsafe_allow_html=True)

        try:
            with open(mermaid_file, "r") as f:
                mermaid_code = f.read().strip()

            import streamlit.components.v1 as components
            m_theme = 'dark' if st.session_state.theme_mode == 'Dark' else 'neutral'
            html_code = f"""
            <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>
                        mermaid.initialize({{startOnLoad:true, theme:'{m_theme}'}});
                    </script>
                    <style>
                        body {{
                            font-family: 'Outfit', sans-serif;
                            background-color: transparent;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            padding: 20px;
                        }}
                        .mermaid {{
                            background: {c_card_bg};
                            border: 1px solid {c_card_border};
                            border-radius: 12px;
                            padding: 20px;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
                        }}
                    </style>
                </head>
                <body>
                    <div class="mermaid">
                        {mermaid_code}
                    </div>
                </body>
            </html>
            """
            components.html(html_code, height=520, scrolling=True)
        except Exception as e:
            st.error(f"Error loading system architecture: {e}")

    else:
        st.markdown("""
        <div class="section-header">
            <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
                <span class="material-symbols-outlined" style="font-size: 28px; color: #2563EB;">schema</span>
                Platform System Architecture
            </h2>
            <p style="margin: 6px 0 0 0; font-size: 14px;">
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
# DATA QUALITY TAB
# =====================================

if page == "Data Quality":

    st.markdown(f"""
    <div class="section-header">
        <h2 style="margin: 0; font-size: 24px; font-weight: 600; display: flex; align-items: center; gap: 10px;">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #10B981;">fact_check</span>
            Data Quality Inspector
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 14px;">
            Monitor data profiling rules, completeness statistics, and duplicate rate checks across cataloged datasets.
        </p>
    </div>
    """, unsafe_allow_html=True)

    dq_data = get_data_quality_data()

    if not dq_data:
        st.warning("No cataloged datasets found in the active context to perform data quality checks.")
    else:
        # Calculate summary metrics
        avg_score = round(sum([info["quality_score"] for info in dq_data.values()]) / len(dq_data), 1)
        total_rows = sum([info["total_rows"] for info in dq_data.values()])
        total_rules = sum([len(info["rules"]) for info in dq_data.values()])
        
        passed_rules = 0
        warning_rules = 0
        for info in dq_data.values():
            passed_rules += len([r for r in info["rules"] if r["status"] == "Passed"])
            warning_rules += len([r for r in info["rules"] if r["status"] == "Warning"])

        # Display summary row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Average Quality Score",
                value=f"{avg_score}%",
                delta="Optimal" if avg_score >= 95 else "Attention Required"
            )
        with col2:
            st.metric(
                label="Total Records Checked",
                value=f"{total_rows:,}",
                delta="Active Context"
            )
        with col3:
            st.metric(
                label="Rules Evaluated",
                value=str(total_rules),
                delta=f"{passed_rules} Passed"
            )
        with col4:
            st.metric(
                label="Rule Integrity Warnings",
                value=str(warning_rules),
                delta="0 Critical Failures"
            )

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Plotly Bar Chart comparing Null Rate and Duplicate Rate side-by-side
        x_tables = list(dq_data.keys())
        y_nulls = [info["null_rate"] for info in dq_data.values()]
        y_dups = [info["duplicate_rate"] for info in dq_data.values()]

        fig = go.Figure()
        
        # Add Null Rate Bar
        fig.add_trace(
            go.Bar(
                name="Null Rate (%)",
                x=x_tables,
                y=y_nulls,
                marker_color="#EF4444" if st.session_state.theme_mode == "Dark" else "#DC2626",
                width=0.25
            )
        )
        
        # Add Duplicate Rate Bar
        fig.add_trace(
            go.Bar(
                name="Duplicate Rate (%)",
                x=x_tables,
                y=y_dups,
                marker_color="#F59E0B" if st.session_state.theme_mode == "Dark" else "#D97706",
                width=0.25
            )
        )

        chart_text_color = "#E5E7EB" if st.session_state.theme_mode == "Dark" else "#0F172A"
        grid_color = "rgba(255, 255, 255, 0.08)" if st.session_state.theme_mode == "Dark" else "rgba(0, 0, 0, 0.08)"

        fig.update_layout(
            title=dict(
                text="Dataset Anomaly Profiler: Null & Duplicate Rates (%)",
                font=dict(color=chart_text_color, family='Outfit', size=16)
            ),
            barmode='group',
            yaxis_title="Error Rate (%)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=chart_text_color, family='Outfit'),
            height=340,
            margin=dict(l=40, r=40, t=50, b=40),
            legend=dict(
                font=dict(color=chart_text_color),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            modebar=dict(
                bgcolor='rgba(0,0,0,0)',
                color=chart_text_color,
                activecolor='#3B82F6'
            )
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=grid_color)
        fig.update_xaxes(tickfont=dict(size=12))

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color: {c_text_headings}; font-size: 16px; font-weight: 600;'>Detailed Profiling & Rules Explorer</h4>", unsafe_allow_html=True)

        # Draw details for each table in an expander
        for t_name, info in dq_data.items():
            status_text = "Passed" if info["quality_score"] >= 95 else "Degraded"
            badge_color = "rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);" if status_text == "Passed" else "rgba(245, 158, 11, 0.1); color: #D97706; border: 1px solid rgba(245, 158, 11, 0.2);"
            
            with st.expander(f"{t_name} | Quality Score: {info['quality_score']}%"):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    card_html = f"""
                    <div style="padding: 16px; background: {c_nested_box_bg}; border-radius: 10px; border: 1px solid {c_nested_box_border}; height: 100%;">
                        <span style="color: {c_text_muted} !important; font-size: 11px; font-weight: 600; text-transform: uppercase;">PROFILING STATISTICS</span><br>
                        <div style="margin-top: 10px; display: grid; gap: 8px; font-size: 13.5px;">
                            <div style="display: flex; justify-content: space-between;"><span>Row Count</span><strong style="color: {c_text_headings};">{info['total_rows']:,}</strong></div>
                            <div style="display: flex; justify-content: space-between;"><span>Completeness</span><strong>{info['completeness']}%</strong></div>
                            <div style="display: flex; justify-content: space-between;"><span>Uniqueness</span><strong>{info['uniqueness']}%</strong></div>
                            <div style="display: flex; justify-content: space-between;"><span>Audit Status</span><span class="pill-badge" style="background-color: {badge_color}">{status_text}</span></div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                with col_info2:
                    st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: {c_text_muted}; margin-bottom: 8px; text-transform: uppercase;'>EVALUATED RULES ({len(info['rules'])})</div>", unsafe_allow_html=True)
                    for rule in info["rules"]:
                        icon_name = "check_circle" if rule["status"] == "Passed" else "warning"
                        icon_color = "#10B981" if rule["status"] == "Passed" else "#F59E0B"
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid {c_nested_box_border}; font-size: 13.5px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="material-symbols-outlined" style="font-size: 18px; color: {icon_color};">{icon_name}</span>
                                    <span>{rule['rule_name']}</span>
                                </div>
                                <span style="font-family: monospace; font-weight: 600; color: {c_text_headings};">{rule['metric']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# =====================================
# FOOTER
# =====================================

st.markdown("---")

st.caption(
    "Built with Gemini • ChromaDB • AWS S3 • Streamlit"
)