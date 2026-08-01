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
    page_title="FinAI – Your Wealth Assistant",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM STYLING — VISIBLE SIDEBAR COLLAPSE / EXPAND TOGGLE
# ---------------------------------------------------------
st.markdown("""
<style>
    :root {
        --border-color: transparent !important;
    }

    /* Lock Page Body strictly to 100vh with Dark Midnight & Bright Silver-Grey Glow */
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
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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

    [data-testid="collapsedControl"] *,
    button[data-testid="stBaseButton-header"] *,
    button[aria-label="Expand sidebar"] *,
    button[aria-label="Collapse sidebar"] * {
        color: #38bdf8 !important;
        fill: #38bdf8 !important;
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
    
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }

    /* Sidebar Header Branding Box */
    .sidebar-brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.2rem;
    }
    .sidebar-brand-icon {
        background: linear-gradient(135deg, #2563eb, #64748b);
        color: white;
        font-size: 1.4rem;
        padding: 8px 12px;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.45);
    }
    .sidebar-brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc !important;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-sub {
        font-size: 0.82rem;
        color: #64748b !important;
        line-height: 1.35;
        margin-bottom: 1.2rem;
    }

    .sidebar-section-title {
        font-size: 0.78rem;
        font-weight: 800;
        color: #3b82f6 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    /* Sidebar Input Overrides */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] input {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }

    /* Sidebar Reset Button */
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #2563eb, #475569) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4) !important;
        padding: 10px 16px !important;
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
        border-radius: 18px !important;
        padding: 16px 24px !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.8rem !important;
        width: 100% !important;
        box-shadow: 0 10px 36px 0 rgba(0, 0, 0, 0.5), 0 0 25px rgba(37, 99, 235, 0.15) !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .main-header-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .glowing-sparkle-badge {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.4), rgba(203, 213, 225, 0.35));
        border: 2px solid rgba(56, 189, 248, 0.6);
        border-radius: 50%;
        width: 56px;
        height: 56px;
        font-size: 1.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    .main-header-title {
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.02em !important;
    }
    .main-header-title span {
        background: linear-gradient(135deg, #38bdf8, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header-sub {
        font-size: 0.88rem !important;
        color: #94a3b8 !important;
        margin-top: 0.2rem !important;
    }

    /* Right Side Feature Badges */
    .header-features-group {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .feature-item {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .feature-icon {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .feature-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .feature-sub {
        font-size: 0.7rem;
        color: #64748b;
    }

    /* Welcome Banner Card (Inside Chat Box) */
    .welcome-banner-card {
        background: rgba(10, 15, 30, 0.65) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(59, 130, 246, 0.25) !important;
        border-radius: 16px !important;
        padding: 14px 22px !important;
        margin-bottom: 1rem !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    .welcome-banner-left {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.92rem;
        color: #cbd5e1;
        line-height: 1.4;
    }
    .welcome-banner-left b {
        color: #38bdf8;
    }
    .welcome-chart-icon {
        font-size: 1.9rem;
        background: linear-gradient(135deg, #38bdf8, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Empty State Container */
    .empty-state-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2.2rem 1rem;
        text-align: center;
    }
    .empty-state-icon {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(226, 232, 240, 0.2));
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 18px;
        width: 68px;
        height: 68px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.3);
    }
    .empty-state-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.4rem;
    }
    .empty-state-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        max-width: 480px;
        line-height: 1.45;
    }

    /* User Chat Bubble — Dark Royal Blue Gradient Pill */
    .user-bubble-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        margin: 0.9rem 0;
    }
    .user-bubble {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.8), rgba(30, 64, 175, 0.9)) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(147, 197, 253, 0.4) !important;
        color: #f8fafc !important;
        padding: 12px 20px !important;
        border-radius: 22px 22px 4px 22px !important;
        max-width: 78% !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }
    .user-avatar {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }

    /* Assistant Chat Bubble — Deep Obsidian Slate Card */
    .ai-bubble-container {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 0.9rem 0;
    }
    .ai-avatar {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
    }
    .ai-bubble {
        background: rgba(14, 18, 28, 0.78) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        color: #f8fafc !important;
        padding: 16px 22px !important;
        border-radius: 4px 22px 22px 22px !important;
        max-width: 86% !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
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
        font-size: 0.92rem;
        font-weight: 600;
        color: #38bdf8;
    }

    /* Floating Glass Input Bar */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: calc(50% + 140px) !important;
        transform: translateX(-50%) !important;
        width: calc(100% - 360px) !important;
        max-width: 1100px !important;
        z-index: 999999 !important;
        background: rgba(10, 15, 30, 0.88) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border-radius: 36px !important;
        padding: 4px 12px !important;
        border: 1px solid rgba(59, 130, 246, 0.35) !important;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.75), 0 0 25px rgba(56, 189, 248, 0.2) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        background-color: transparent !important;
        font-size: 1.02rem !important;
        line-height: 1.5 !important;
        font-weight: 500 !important;
    }

    /* Glass Action Send Button */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
        border-radius: 50% !important;
        color: white !important;
        border: none !important;
        width: 40px !important;
        height: 40px !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.6) !important;
    }

    /* Bottom Security Note Below Input */
    .input-disclaimer-note {
        position: fixed;
        bottom: 8px;
        left: calc(50% + 140px);
        transform: translateX(-50%);
        font-size: 0.75rem;
        color: #64748b;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 6px;
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
        <div class="sidebar-brand-icon">✨</div>
        <div>
            <div class="sidebar-brand-title">FinAI</div>
            <div class="sidebar-brand-sub">Your Wealth Assistant</div>
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
        index=0,
        help="Choose your preferred AI infrastructure provider."
    )

    # 2. Text Input Field: Enter API Key (masked)
    if provider == "OpenAI":
        default_key = os.getenv("OPENAI_API_KEY", "")
        api_key = st.text_input(
            "API Key",
            type="password",
            value=default_key,
            placeholder="sk-...",
            help="Enter your OpenAI API key."
        )
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]

    elif provider == "Google Gemini":
        default_key = os.getenv("GOOGLE_API_KEY", "")
        api_key = st.text_input(
            "API Key",
            type="password",
            value=default_key,
            placeholder="AIzaSy...",
            help="Enter your Google Gemini API key."
        )
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        model_options = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

    elif provider == "Anthropic":
        default_key = os.getenv("ANTHROPIC_API_KEY", "")
        api_key = st.text_input(
            "API Key",
            type="password",
            value=default_key,
            placeholder="sk-ant-...",
            help="Enter your Anthropic Claude API key."
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        model_options = ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]

    st.caption("🛡️ Your API key is stored securely.")

    # 3. Dropdown: Select Model
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=0,
        help="Model engine version"
    )

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

    # 4. Button: Reset Conversation
    if st.button("🔄 Reset Conversation", width="stretch"):
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
# MAIN PAGE HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="main-header-banner">
    <div class="main-header-left">
        <div class="glowing-sparkle-badge">✨</div>
        <div>
            <h1 class="main-header-title">FinAI – <span>Your Wealth Assistant</span></h1>
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
        <div class="feature-item">
            <div class="feature-icon">🛡️</div>
            <div>
                <div class="feature-title">Secure & Private</div>
                <div class="feature-sub">Your data is safe and encrypted</div>
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
    # Render Welcome Banner & Empty State ONLY before conversation starts
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-banner-card">
            <div class="welcome-banner-left">
                <span style="font-size:1.4rem;">👋</span>
                <div><b>Welcome to FinAI.</b> Ask a question about loan EMIs, SIP growth, monthly budget splits, financial goals, or market news.</div>
            </div>
            <div class="welcome-chart-icon">📊</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="empty-state-box">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-title">How can I help you today?</div>
            <div class="empty-state-sub">Ask anything related to your finances and I'll help you with insights, calculations, and recommendations.</div>
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
