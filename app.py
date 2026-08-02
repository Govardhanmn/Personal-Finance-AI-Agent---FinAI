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
    page_title="FinAI – Your Smart Financial Companion",
    page_icon="💳",
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

    /* PRESERVE STREAMLIT MATERIAL SYMBOLS & ICON FONTS FROM OVERRIDES */
    .material-symbols-outlined,
    .material-symbols-rounded,
    .material-icons,
    [data-testid="stIcon"],
    [data-testid="stIcon"] *,
    button[aria-label="Show password"] *,
    button[aria-label="Hide password"] * {
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
   
