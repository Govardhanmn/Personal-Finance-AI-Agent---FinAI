import os
import re
import time
from datetime import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun

# Optional Anthropic import
try:
    from langchain_anthropic import ChatAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Safe import for PythonREPLTool with fallback to custom calculator tool
try:
    from langchain_experimental.tools import PythonREPLTool
    python_repl_tool = PythonREPLTool()
except ImportError:
    try:
        from langchain_experimental.tools.python.tool import PythonREPLTool
        python_repl_tool = PythonREPLTool()
    except ImportError:
        @tool
        def python_repl_tool(expression: str) -> str:
            """Perform general mathematical and arithmetic calculations."""
            try:
                result = eval(expression, {"__builtins__": {}}, {})
                return f"Calculation: {expression} = {result:,.4f}"
            except Exception as e:
                return f"Error: {e}"

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FinAI – Your Personal Finance AI Agent",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM STYLING — POPPINS TYPOGRAPHY & GRADIENT BRANDING
# ---------------------------------------------------------
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    :root {
        --border-color: transparent !important;
    }

    /* Lock Page Body strictly to 100vh with Poppins Font Family */
    html, body, .stApp {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        background-color: #060813 !important;
        background-image: 
            radial-gradient(circle at 10% 15%, rgba(37, 99, 235, 0.15), transparent 45%),
            radial-gradient(circle at 90% 85%, rgba(203, 213, 225, 0.12), transparent 45%),
            radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.05), transparent 50%) !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Transparent Header Bar & Hide Footer */
    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 999999 !important;
    }
    
    footer {
        display: none !important;
        height: 0 !important;
    }

    /* ALWAYS SHOW & STYLE SIDEBAR EXPAND/COLLAPSE CONTROL BUTTON */
    [data-testid="collapsedControl"],
    button[data-testid="stBaseButton-header"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Collapse sidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 9999999 !important;
        background: rgba(10, 15, 30, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-radius: 12px !important;
        color: #38bdf8 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
    }

    /* ERADICATE ALL RAW ICON TEXT LEAKS ACROSS STREAMLIT SIDEBAR HEADER BUTTONS */
    [data-testid="stSidebarHeader"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"],
    [data-testid="stSidebar"] button[aria-label="Expand sidebar"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"] {
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebarHeader"] button *,
    [data-testid="stSidebarCollapseButton"] button *,
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"] *,
    [data-testid="stSidebar"] button[aria-label="Expand sidebar"] *,
    button[aria-label="Collapse sidebar"] *,
    button[aria-label="Expand sidebar"] * {
        display: none !important;
        font-size: 0 !important;
        color: transparent !important;
    }

    [data-testid="stSidebarHeader"] button::before,
    [data-testid="stSidebarCollapseButton"] button::before,
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"]::before,
    button[aria-label="Collapse sidebar"]::before {
        content: "‹" !important;
        font-size: 1.4rem !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        display: block !important;
    }

    [data-testid="stSidebar"] button[aria-label="Expand sidebar"]::before,
    button[aria-label="Expand sidebar"]::before {
        content: "›" !important;
        font-size: 1.4rem !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        display: block !important;
    }

    /* FIX PASSWORD EYE BUTTON TEXT LEAK ON STREAMLIT CLOUD */
    button[aria-label="Show password"],
    button[aria-label="Hide password"],
    [data-baseweb="input"] button {
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
        overflow: hidden !important;
    }

    button[aria-label="Show password"] *,
    button[aria-label="Hide password"] *,
    [data-baseweb="input"] button * {
        display: none !important;
        font-size: 0 !important;
        color: transparent !important;
    }

    button[aria-label="Show password"]::before,
    button[aria-label="Hide password"]::before,
    [data-baseweb="input"] button::before {
        content: "👁" !important;
        font-size: 1.1rem !important;
        color: #38bdf8 !important;
        opacity: 0.85 !important;
        display: block !important;
        line-height: 1 !important;
    }

    /* PRESERVE STREAMLIT MATERIAL SYMBOLS & ICON FONTS FROM OVERRIDES */
    .material-symbols-outlined,
    .material-symbols-rounded,
    .material-icons,
    [data-testid="stIcon"],
    [data-testid="stIcon"] * {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        text-transform: none !important;
        word-wrap: normal !important;
        white-space: nowrap !important;
        direction: ltr !important;
    }

    /* FORCED TRANSPARENCY ON STREAMLIT CONTAINER WRAPPERS */
    [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] *,
    [data-testid="stBottom"],
    [data-testid="stBottom"] *,
    div[data-testid="stContainer"],
    div[data-testid="stContainer"] * {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-style: none !important;
        border-width: 0px !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Sidebar Styling — Deep Dark Glass Pane */
    [data-testid="stSidebar"] {
        background: rgba(8, 11, 22, 0.92) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border-right: 1px solid rgba(59, 130, 246, 0.15) !important;
        padding-top: 1rem !important;
        height: 100vh !important;
    }
    
    [data-testid="stSidebar"] *:not(.material-symbols-outlined):not(.material-symbols-rounded):not(.material-icons):not([data-testid="stIcon"]) {
        color: #cbd5e1 !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Sidebar Header Branding Box */
    .sidebar-brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.2rem;
    }
    .sidebar-brand-icon {
        background: linear-gradient(135deg, #2563eb, #38bdf8);
        color: white;
        font-size: 1.25rem;
        padding: 6px 10px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.45);
    }
    .sidebar-brand-title {
        font-size: 1.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
        letter-spacing: -0.02em;
        font-family: 'Poppins', sans-serif !important;
    }
    .sidebar-brand-sub {
        font-size: 0.74rem;
        color: #94a3b8 !important;
        font-weight: 400;
        line-height: 1.35;
        margin-bottom: 1rem;
    }

    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #3b82f6 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
    }

    /* Sidebar Input Overrides */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="input"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebar"] input {
        background: transparent !important;
        border: none !important;
        color: #f8fafc !important;
    }

    /* Reset Icon Buttons inside Inputs (Tooltip ?, Dropdown arrow, Eye icon) */
    [data-testid="stSidebar"] [data-testid="stTooltipIcon"] button,
    [data-testid="stSidebar"] div[data-baseweb="select"] button,
    [data-testid="stSidebar"] div[data-baseweb="input"] button,
    [data-testid="stSidebar"] button[aria-label="Show password"],
    [data-testid="stSidebar"] button[aria-label="Hide password"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 8px !important;
        margin: 0 !important;
        border-radius: 0 !important;
        width: auto !important;
        height: auto !important;
    }

    /* Sidebar Reset Action Button Only */
    [data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4) !important;
        padding: 9px 14px !important;
        width: 100% !important;
        font-size: 0.88rem !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Main Block Container */
    .main,
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0.4rem !important;
        margin-top: 0rem !important;
        padding-bottom: 95px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
        width: 100% !important;
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Top Glass Banner Card */
    .main-header-banner {
        background: rgba(10, 15, 30, 0.75) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border: 1px solid rgba(59, 130, 246, 0.25) !important;
        border-radius: 16px !important;
        padding: 14px 22px !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.7rem !important;
        width: 100% !important;
        box-shadow: 0 10px 36px 0 rgba(0, 0, 0, 0.5), 0 0 25px rgba(37, 99, 235, 0.15) !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .main-header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .glowing-sparkle-badge {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.4), rgba(203, 213, 225, 0.35));
        border: 2px solid rgba(56, 189, 248, 0.6);
        border-radius: 50%;
        width: 46px;
        height: 46px;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.4);
    }
    
    /* ABSOLUTE GAPLESS HEADER TYPOGRAPHY USING DIV */
    .main-header-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 1.55rem !important;
        margin: 0 !important;
        padding: 0 !important;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        line-height: 1.15 !important;
        letter-spacing: -0.02em !important;
        display: block !important;
    }
    .fin-brand-bold {
        font-weight: 700 !important;
        font-size: 1.55rem !important;
        background: linear-gradient(135deg, #38bdf8, #2563eb) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block !important;
    }
    .fin-sub-regular {
        font-weight: 400 !important;
        font-size: 1.25rem !important;
        color: #cbd5e1 !important;
        -webkit-text-fill-color: #cbd5e1 !important;
        display: inline-block !important;
    }
    .main-header-sub {
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.76rem !important;
        color: #94a3b8 !important;
        margin: 0 !important;
        margin-top: 2px !important;
        padding: 0 !important;
        line-height: 1.25 !important;
        display: block !important;
    }

    /* Right Side Feature Badges */
    .header-features-group {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .feature-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .feature-icon {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 10px;
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    .feature-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #f8fafc;
        font-family: 'Poppins', sans-serif !important;
    }
    .feature-sub {
        font-size: 0.65rem;
        color: #64748b;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Combined Hero Empty State Container */
    .empty-state-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 1.5rem;
        text-align: center;
    }
    .empty-state-icon {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.25), rgba(56, 189, 248, 0.25));
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 20px;
        width: 64px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 28px rgba(56, 189, 248, 0.35);
    }
    .empty-state-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.4rem;
        font-family: 'Poppins', sans-serif !important;
    }
    .empty-state-sub {
        font-size: 0.88rem;
        color: #94a3b8;
        max-width: 520px;
        line-height: 1.5;
        font-family: 'Poppins', sans-serif !important;
    }

    /* User Chat Bubble — Dark Royal Blue Gradient Pill */
    .user-bubble-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        margin: 0.8rem 0;
    }
    .user-bubble {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.8), rgba(30, 64, 175, 0.9)) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(147, 197, 253, 0.4) !important;
        color: #f8fafc !important;
        padding: 10px 18px !important;
        border-radius: 20px 20px 4px 20px !important;
        max-width: 78% !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        font-weight: 400 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .user-avatar {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.88rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }

    /* Assistant Chat Bubble — Deep Obsidian Slate Card */
    .ai-bubble-container {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin: 0.8rem 0;
    }
    .ai-avatar {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
    }
    .ai-bubble {
        background: rgba(14, 18, 28, 0.78) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        color: #f8fafc !important;
        padding: 14px 20px !important;
        border-radius: 4px 20px 20px 20px !important;
        max-width: 86% !important;
        font-size: 0.9rem !important;
        line-height: 1.55 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Animated Glass Loading Bubble */
    .loading-bubble {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.25) !important;
        animation: pulse-glow 1.5s infinite alternate;
    }
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 12px rgba(56, 189, 248, 0.2); }
        100% { box-shadow: 0 0 28px rgba(56, 189, 248, 0.5); }
    }
    .loading-text {
        font-size: 0.88rem;
        font-weight: 500;
        color: #38bdf8;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Floating Glass Input Bar */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 28px !important;
        left: calc(50% + 140px) !important;
        transform: translateX(-50%) !important;
        width: calc(100% - 360px) !important;
        max-width: 1100px !important;
        z-index: 999999 !important;
        background: rgba(10, 15, 30, 0.88) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border-radius: 32px !important;
        padding: 3px 10px !important;
        border: 1px solid rgba(59, 130, 246, 0.35) !important;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.75), 0 0 25px rgba(56, 189, 248, 0.2) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        background-color: transparent !important;
        font-size: 0.93rem !important;
        line-height: 1.45 !important;
        font-weight: 400 !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Glass Action Send Button */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
        border-radius: 50% !important;
        color: white !important;
        border: none !important;
        width: 36px !important;
        height: 36px !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.6) !important;
    }

    /* Bottom Security Note Below Input */
    .input-disclaimer-note {
        position: fixed;
        bottom: 6px;
        left: calc(50% + 140px);
        transform: translateX(-50%);
        font-size: 0.72rem;
        color: #64748b;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Poppins', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# SIDEBAR (LEFT PANE) — BRANDING + MODEL CONFIGURATION
# ---------------------------------------------------------
with st.sidebar:
    # Top Branding Header
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-icon">🧠</div>
        <div>
            <div class="sidebar-brand-title">FinAI</div>
            <div class="sidebar-brand-sub">Next-Generation Financial Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">AI MODEL CONFIGURATION</div>', unsafe_allow_html=True)

    # 1. Dropdown: Select LLM Provider
    provider_options = ["OpenAI", "Google Gemini"]
    if HAS_ANTHROPIC:
        provider_options.append("Anthropic")

    provider = st.selectbox(
        "LLM Provider",
        provider_options,
        index=0
    )

    # 2. Text Input Field: Enter API Key (masked)
    # Managed volatile in-memory API key state (starts empty on app open)
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {
            "OpenAI": "",
            "Google Gemini": "",
            "Anthropic": ""
        }

    env_var_map = {
        "OpenAI": "OPENAI_API_KEY",
        "Google Gemini": "GOOGLE_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY"
    }

    placeholder_map = {
        "OpenAI": "sk-...",
        "Google Gemini": "AIzaSy...",
        "Anthropic": "sk-ant-..."
    }

    model_options_map = {
        "OpenAI": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        "Google Gemini": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "Anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    }

    current_env_var = env_var_map[provider]
    model_options = model_options_map.get(provider, ["gpt-4o-mini"])

    # Callback function executed BEFORE widget rendering to prevent Streamlit crash
    def clear_api_key_callback(target_provider, env_var):
        st.session_state.api_keys[target_provider] = ""
        widget_key = f"widget_key_{target_provider}"
        if widget_key in st.session_state:
            st.session_state[widget_key] = ""
        os.environ.pop(env_var, None)

    widget_key_name = f"widget_key_{provider}"
    if widget_key_name not in st.session_state:
        st.session_state[widget_key_name] = st.session_state.api_keys.get(provider, "")

    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder=placeholder_map.get(provider, "Enter API Key..."),
        key=widget_key_name
    )

    # Sync state and process environment cleanly
    if api_key_input:
        st.session_state.api_keys[provider] = api_key_input
        os.environ[current_env_var] = api_key_input
    else:
        st.session_state.api_keys[provider] = ""
        os.environ.pop(current_env_var, None)

    # Clear Button: Safely wipes key using on_click callback without triggering Streamlit widget mutation error
    if api_key_input or st.session_state.api_keys.get(provider, ""):
        st.button(
            "🗑️ Clear API Key",
            key=f"clear_key_{provider}",
            on_click=clear_api_key_callback,
            args=(provider, current_env_var)
        )


    # 3. Dropdown: Select Model
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=0
    )

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

    # 4. Button: Reset Conversation
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.caption("This will clear all messages and conversation history.")


# ---------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------
@tool
def calculate_emi(loan_amount: float, annual_interest_rate: float, tenure_years: float, monthly_income: float = 0.0) -> str:
    """Calculate loan EMI, total interest, total payment and Debt-to-Income (DTI) ratio."""
    P = loan_amount
    r_annual = annual_interest_rate
    t_years = tenure_years
    income = monthly_income

    r = (r_annual / 12) / 100
    n = int(t_years * 12)

    emi = P * r * ((1 + r) ** n) / (((1 + r) ** n) - 1) if r != 0 else P / n
    total_payment = emi * n
    total_interest = total_payment - P
    dti = (emi / income * 100) if income > 0 else 0.0
    dti_status = "Excellent" if dti <= 36 else ("Manageable" if dti <= 43 else "High Risk")

    return (
        f"EMI Calculation Results\n"
        f"{'='*40}\n"
        f"Loan Amount     : Rs. {P:,.2f}\n"
        f"Interest Rate   : {r_annual}% per annum\n"
        f"Tenure          : {t_years} years ({n} months)\n"
        f"{'='*40}\n"
        f"Monthly EMI     : Rs. {emi:,.2f}\n"
        f"Total Interest  : Rs. {total_interest:,.2f}\n"
        f"Total Payment   : Rs. {total_payment:,.2f}\n"
        f"{'='*40}\n"
        f"Monthly Income  : Rs. {income:,.2f}\n"
        f"DTI Ratio       : {dti:.2f}%\n"
        f"DTI Status      : {dti_status}\n"
    )

@tool
def calculate_sip(monthly_investment: float, annual_return_rate: float, tenure_years: float) -> str:
    """Calculate future value of a Systematic Investment Plan (SIP) and total wealth gained."""
    P = monthly_investment
    r_annual = annual_return_rate
    t_years = tenure_years

    r = (r_annual / 12) / 100
    n = int(t_years * 12)

    fv = P * (((1 + r) ** n - 1) / r) if r != 0 else P * n
    total_invested = P * n
    wealth_gained = fv - total_invested
    gain_multiplier = fv / total_invested if total_invested > 0 else 1

    return (
        f"SIP Investment Results\n"
        f"{'='*40}\n"
        f"Monthly Investment : Rs. {P:,.2f}\n"
        f"Expected Return    : {r_annual}% per annum\n"
        f"Investment Period  : {t_years} years ({n} months)\n"
        f"{'='*40}\n"
        f"Total Invested     : Rs. {total_invested:,.2f}\n"
        f"Future Value       : Rs. {fv:,.2f}\n"
        f"Wealth Gained      : Rs. {wealth_gained:,.2f}\n"
        f"Gain Multiplier    : {gain_multiplier:.2f}x\n"
    )

@tool
def calculate_budget(monthly_income: float, monthly_expenses: float = 0.0, loan_emi: float = 0.0) -> str:
    """Create a monthly budget plan using the 50-30-20 rule."""
    income = monthly_income
    expenses = monthly_expenses
    emi = loan_emi

    total_expenses = expenses + emi
    surplus = income - total_expenses
    savings_rate = (surplus / income) if income > 0 else 0

    needs = income * 0.50
    wants = income * 0.30
    savings = income * 0.20

    if surplus < savings:
        savings = max(0, surplus)
        wants = max(0, income - (needs + savings))

    emergency_fund = savings * 0.40
    investments = savings * 0.60

    status = "Strong" if savings_rate >= 0.2 else ("Moderate" if savings_rate >= 0.1 else "Weak")

    return (
        f"Budget Allocation Results (50-30-20 Rule)\n"
        f"{'='*45}\n"
        f"Monthly Income    : Rs. {income:,.2f}\n"
        f"Total Expenses    : Rs. {total_expenses:,.2f}\n"
        f"Monthly Surplus   : Rs. {surplus:,.2f}\n"
        f"{'='*45}\n"
        f"Needs (50%)       : Rs. {needs:,.2f}\n"
        f"Wants (30%)       : Rs. {wants:,.2f}\n"
        f"Savings (20%)     : Rs. {savings:,.2f}\n"
        f"  Emergency Fund  : Rs. {emergency_fund:,.2f}\n"
        f"  Investments     : Rs. {investments:,.2f}\n"
        f"{'='*45}\n"
        f"Savings Rate      : {savings_rate*100:.1f}%\n"
        f"Savings Status    : {status}\n"
    )

@tool
def calculate_goal_savings(
    target_amount: float,
    years_to_goal: float,
    monthly_income: float = 0.0,
    monthly_expenses: float = 0.0,
    loan_emi: float = 0.0,
    fetched_inflation_rate: float = 6.0,
    risk_appetite: str = "Moderate",
    expected_annual_return: float = 0.0
) -> str:
    """Calculate required monthly SIP for a financial goal by integrating budget surplus, dynamic returns, and web inflation."""
    total_expenses = monthly_expenses + loan_emi
    monthly_surplus = max(0.0, monthly_income - total_expenses) if monthly_income > 0 else 0.0

    if expected_annual_return > 0:
        exp_return = expected_annual_return
    elif years_to_goal < 3:
        exp_return = 7.0 if risk_appetite == "Low" else 8.0
    elif years_to_goal <= 7:
        exp_return = 9.0 if risk_appetite == "Low" else (10.5 if risk_appetite == "Moderate" else 12.0)
    else:
        exp_return = 10.0 if risk_appetite == "Low" else (12.0 if risk_appetite == "Moderate" else 14.0)

    inflation = fetched_inflation_rate
    inflated_target = target_amount * ((1 + inflation / 100) ** years_to_goal)

    r = exp_return / 1200
    n = int(years_to_goal * 12)

    if r > 0:
        required_monthly = inflated_target * r / (((1 + r) ** n - 1) * (1 + r))
    else:
        required_monthly = inflated_target / n if n else 0.0

    feasibility = "Achievable" if (monthly_surplus >= required_monthly and monthly_surplus > 0) else ("Not Feasible" if monthly_surplus > 0 else "N/A")

    eq_pct = 70 if years_to_goal >= 7 else (40 if years_to_goal >= 3 else 10)
    debt_pct = 20 if years_to_goal >= 7 else (50 if years_to_goal >= 3 else 80)
    gold_pct = 10

    return (
        f"Integrated Goal & Budget Planner Results\n"
        f"{'='*50}\n"
        f"Target Amount (Today)  : Rs. {target_amount:,.2f}\n"
        f"Time Horizon           : {years_to_goal} years ({n} months)\n"
        f"Web Inflation Rate     : {inflation}% per annum\n"
        f"Inflation-Adj. Target  : Rs. {inflated_target:,.2f}\n"
        f"Dynamic Expected Return: {exp_return}% p.a.\n"
        f"{'='*50}\n"
        f"Required Monthly SIP   : Rs. {required_monthly:,.2f}\n"
        f"Monthly Budget Surplus : Rs. {monthly_surplus:,.2f}\n"
        f"Goal Feasibility       : {feasibility}\n"
        f"{'='*50}\n"
        f"Recommended Asset Mix  : Equity {eq_pct}% | Debt {debt_pct}% | Gold {gold_pct}%\n"
    )

search_tool = DuckDuckGoSearchRun()

finance_tools = [
    calculate_emi,
    calculate_sip,
    calculate_budget,
    calculate_goal_savings,
    python_repl_tool,
    search_tool
]

# ---------------------------------------------------------
# Agent Creation Helper
# ---------------------------------------------------------
def get_agent():
    if provider == "Google Gemini":
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            return None
        llm = ChatGoogleGenerativeAI(model=selected_model, temperature=temperature)
    elif provider == "OpenAI":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return None
        llm = ChatOpenAI(model=selected_model, temperature=temperature)
    elif provider == "Anthropic" and HAS_ANTHROPIC:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return None
        llm = ChatAnthropic(model=selected_model, temperature=temperature)
    else:
        return None

    agent_prompt = """
    You are a Personal Finance AI Assistant designed specifically for Indian users.

   Your primary capabilities include:
    - Loan EMI calculations and DTI analysis
    - SIP investment projections and wealth planning
    - Monthly budget planning (50-30-20 rule)
    - Integrated Financial Goal Planning (with budget surplus, dynamic tenure returns, and live inflation rate)
    - General arithmetic and percentage calculations
    - Live financial news, stock market updates, RBI rates,
      mutual fund data and inflation trends from the web

    Operational Workflow:
    1. Invoke the appropriate tool to generate accurate numerical outputs.
       All calculations must be tool-driven, manual or estimated calculations are not permitted.
       - For Loan EMI       : use calculate_emi
       - For SIP returns    : use calculate_sip
       - For Budget split   : use calculate_budget
       - For arithmetic     : use Python_REPL
       - For news/rates     : use duckduckgo_search
       - For Goal Planning  : first search web for current inflation rate using 'duckduckgo_search' if not provided,
                              then call 'calculate_goal_savings' passing income, expenses, EMI, and fetched inflation rate.

    2. Based on the tool result, provide a complete response:
       - For EMI    : evaluate the DTI ratio and assess the sustainability of the user’s debt obligations
       - For SIP    : explain the power of compounding and interpret long-term wealth accumulation
       - For Budget : Assess the user’s savings rate, classify financial health (Strong / Moderate / Weak), and provide targeted optimization recommendations
       - For Goal   : explain inflation impact, dynamic return choice based on tenure, feasibility against budget surplus, quantify any shortfall, and suggest actionable corrective measures
       - For search : summarize the news/data clearly, extract key numbers, give financial context
       - End every response with one clear, actionable next step

    Constraints and Guidelines:
    - Always use the appropriate tool first. Never guess numbers.
    - Ensure all insights are derived strictly from computed outputs
    - All monetary values must be expressed in Indian Rupees (Rs.)
    - Provide practical, context-aware recommendations rather than generic advice
    - Maintain a balance between analytical precision and user-friendly explanation
    - You have memory of the full conversation — refer back to earlier
      questions or numbers the user has already shared when relevant.
    """

    return create_agent(model=llm, tools=finance_tools, system_prompt=agent_prompt)


# ---------------------------------------------------------
# MAIN PAGE HEADER (DIV-BASED TYPOGRAPHY FOR ZERO DEPLOYMENT GAP)
# ---------------------------------------------------------
st.markdown("""
<div class="main-header-banner">
    <div class="main-header-left">
        <div class="glowing-sparkle-badge">🤖</div>
        <div>
            <div class="main-header-title">
                <span class="fin-brand-bold">FinAI</span> <span class="fin-sub-regular">– Your Personal Finance AI-Agent</span>
            </div>
            <div class="main-header-sub">Personalized financial insights, planning tools, and real-time guidance.</div>
        </div>
    </div>
    <div class="header-features-group">
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div>
                <div class="feature-title">Smart Insights</div>
                <div class="feature-sub">Get data-driven financial insights</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div>
                <div class="feature-title">Goal Planning</div>
                <div class="feature-sub">Plan and track your financial goals</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CHAT INTERFACE — EXPANDED HEIGHT CONTAINER (HEIGHT=480)
# ---------------------------------------------------------
chat_container = st.container(height=480)

with chat_container:
    # Single Combined Hero Empty State Card BEFORE conversation starts
    if not st.session_state.messages:
        st.markdown("""
        <div class="empty-state-box">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-title">How can I help you today?</div>
            <div class="empty-state-sub">
                Welcome to <b>FinAI</b>! Ask anything about loan EMIs, SIP growth, monthly budget splits, financial goals, or market news and I'll assist you with calculations and insights.
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(f"""
            <div class="user-bubble-container">
                <div class="user-bubble">
                    {content}
                </div>
                <div class="user-avatar">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-bubble-container">
                <div class="ai-avatar">🤖</div>
                <div class="ai-bubble">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Floating Bottom Glass Chat Input
user_input = st.chat_input("Ask FinAI anything (e.g. Loan EMI, SIP growth, Budget plan)...")

# Bottom Disclaimer Security Note
st.markdown("""
<div class="input-disclaimer-note">
    🔒 AI-generated responses. Please verify important financial decisions.
</div>
""", unsafe_allow_html=True)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    agent = get_agent()

    if agent:
        # Show animated loading status pill inside chat feed
        with chat_container:
            st.markdown("""
            <div class="ai-bubble-container">
                <div class="ai-avatar">🤖</div>
                <div class="ai-bubble loading-bubble">
                    <span class="loading-text">✨ FinAI Agent is generating response & performing calculations...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        try:
            langchain_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            response = agent.invoke({"messages": langchain_msgs})
            
            response_messages = response.get("messages", [])
            reply_content = response_messages[-1].content if response_messages else "Analysis complete."

            st.session_state.messages.append({"role": "assistant", "content": reply_content})
            st.rerun()
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ **Execution Error**: {e}"})
            st.rerun()
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"⚠️ **API Key Required**: Please enter your **{provider} API Key** in the left sidebar configuration pane to continue."
        })
        st.rerun()
