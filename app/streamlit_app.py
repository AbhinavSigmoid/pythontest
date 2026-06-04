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

# Initialize Theme Mode in session state
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

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
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *),
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *),
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *) {{
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
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *) p,
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *) span,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *) p,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *) span,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *) p,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *) span {{
    color: {c_btn_text} !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}}

/* Hover state for main page secondary buttons */
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):hover,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):hover,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):hover {{
    background-color: {c_btn_hover_bg} !important;
    border-color: {c_btn_hover_border} !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    transform: translateY(-1px) !important;
}}

div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):hover p,
div[data-testid="stAppViewContainer"] button:not([data-testid="stSidebar"] *):hover span,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):hover p,
div[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:not([data-testid="stSidebar"] *):hover span,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):hover p,
div[data-testid="stAppViewContainer"] [data-testid="stBaseButton-secondary"]:not([data-testid="stSidebar"] *):hover span {{
    color: {c_btn_hover_text} !important;
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
    theme_toggle_val = st.toggle(
        "Dark Mode",
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
        health = get_pipeline_health()
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
                    <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Active</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: {c_nested_box_bg}; border-radius: 8px; border: 1px solid {c_nested_box_border};">
                    <span style="font-weight: 500;">AWS S3 Cloud Sync</span>
                    <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Connected</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: {c_nested_box_bg}; border-radius: 8px; border: 1px solid {c_nested_box_border};">
                    <span style="font-weight: 500;">ChromaDB Vector Store</span>
                    <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>Healthy</span>
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

if page == "Pipeline Health":

    health = get_pipeline_health()

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
                        <span class="status-badge online" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);"><span class="pulse-dot"></span>{p_data.get('status', 'Operational')}</span>
                    </div>
                    <div style="display: grid; gap: 10px; font-size: 14px;">
                        <div style="display: flex; justify-content: space-between;"><span style="color: #8D7B68 !important;">Uptime Availability</span><span style="font-weight:600; color: #059669 !important;">{p_data.get('availability', '99.90%')}</span></div>
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
            avail_str = p_data.get('availability', '100%').replace("%", "")
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
        fig.update_layout(
            title="Uptime Availability Actual vs Target (%)",
            yaxis_title="Availability %",
            yaxis_range=[min(min_y, 99.5), 100.0],
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
        "metadata/tables.json",
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
                    st.markdown(f"- `<code style='color: #2563EB; background: transparent; padding: 0;'>{col}</code>`", unsafe_allow_html=True)

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
        "metadata/lineage.json",
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
                        <div class="custom-card" style="padding: 18px; margin-bottom: 15px; border-top: 3px solid #2563EB;">
                            <div style="margin-bottom: 8px;"><span class="material-symbols-outlined" style="font-size: 32px; color: #2563EB;">description</span></div>
                            <div style="font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; font-size: 15px;" title="{pdf}">
                                {pdf}
                            </div>
                            <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #8D7B68 !important; font-size: 12px; font-weight: 500;">{size_kb} KB</span>
                                <span class="pill-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2);">Indexed</span>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.warning(
                    "No PDFs Found"
                )
        except Exception as e:
            st.error(f"Uploads folder not found: {e}")

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
# FOOTER
# =====================================

st.markdown("---")

st.caption(
    "Built with Gemini • ChromaDB • AWS S3 • Streamlit"
)