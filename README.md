# 💸 FinAI – Your Personal Finance AI Agent

> **Personalized financial insights, planning tools, and real-time guidance.**

FinAI is an intelligent, agentic AI personal finance assistant built specifically for Indian users. Powered by **LangChain**, **Streamlit**, and multi-provider LLMs (OpenAI, Google Gemini), FinAI provides tool-driven financial calculations, investment compounding models, budget allocation strategies, and live financial market search.

---

## ⚙️ AI Tools & Capabilities Overview

FinAI uses a suite of 6 specialized tools to execute precise calculations and fetch real-time market data:

| Tool Name | Brief Description | Key Outputs |
| :--- | :--- | :--- |
| 💳 `calculate_emi` | **Loan EMI & Debt Analyzer**: Calculates monthly EMI, total interest, and total payable amount for any loan amount, interest rate, and tenure. | Monthly EMI, Total Interest, Total Payment, DTI Ratio (%), and DTI Status (*Excellent ≤36%*, *Manageable ≤43%*, *High Risk >43%*). |
| 📈 `calculate_sip` | **SIP Wealth Calculator**: Computes future portfolio valuation for Systematic Investment Plans using compounding formulas. | Total Invested Amount, Future Value (Rs.), Net Wealth Gained, and Gain Multiplier (x). |
| 💰 `calculate_budget` | **50-30-20 Budget Planner**: Allocates monthly income into Needs, Wants, and Savings according to personal finance best practices. | Needs (50%), Wants (30%), Savings (20%), Emergency Fund (40% of savings), Investment Split (60% of savings), and Savings Rate Status (*Strong*, *Moderate*, *Weak*). |
| 🎯 `calculate_goal_savings` | **Integrated Goal Planner**: Computes required monthly SIP for future goals considering tenure-based dynamic returns, inflation, and budget surplus. | Inflation-Adjusted Target, Required Monthly SIP, Budget Surplus Feasibility (*Achievable* / *Not Feasible*), and Recommended Asset Mix (Equity / Debt / Gold). |
| 🧮 `python_repl_tool` | **Python Math REPL**: Programmatically evaluates custom mathematical expressions and percentages to prevent LLM calculation errors. | Exact numerical calculation results to 4 decimal places. |
| 🌐 `search_tool` | **Live Web Search (DuckDuckGo)**: Fetches real-time financial market updates, RBI repo rate changes, stock trends, and CPI inflation figures. | Current market insights, inflation metrics, interest rates, and financial news summaries. |

---

## 🚀 Full Application Functionalities

- **Multi-Provider LLM Engine Selection**:
  - Toggle between **OpenAI** (`gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`), **Google Gemini** (`gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash`), and **Anthropic Claude** (`claude-3-5-sonnet`, `claude-3-haiku`) on the fly.
- **Dynamic API Key Configuration**:
  - Secure, masked password input in the left sidebar pane for entering API keys at runtime without modifying environment files.
- **Temperature & Memory Control**:
  - Custom temperature slider (`0.0` to `1.0`) to balance computational exactness with creative financial advice.
  - Maintains full multi-turn conversation memory across queries.
- **One-Click Conversation Reset**:
  - `🔄 Reset Conversation` button to instantly clear chat memory and start fresh.
- **Auto-Hiding Welcome & Empty State**:
  - Displays a welcome banner card and "How can I help you today?" prompt initially, which automatically hide as soon as conversation begins.
- **Animated Pulsing Glass Loading Indicator**:
  - Real-time animated loading bubble showing active calculation and tool execution status inside the chat feed.
- **Collapsible Sidebar with Floating Control**:
  - Floating chevron button (`>`) at top-left allows expanding and collapsing the sidebar for maximum screen real estate.
- **Floating Input Bar & Footer Disclaimer**:
  - Fixed glass capsule chat bar with instant send action and an AI disclaimer note (`🔒 AI-generated responses. Please verify important financial decisions.`).

---

## 🎨 Design System

- **Theme**: Ultra-Dark Midnight Glassmorphism (`#060813`) with ambient cyan (`#38bdf8`) & silver-grey (`#e2e8f0`) radial glow highlights.
- **Header**: Banner card displaying app title and 3 feature badges (*Smart Insights*, *Goal Planning*, *Secure & Private*).
- **Chat Feed**: Border-free native Streamlit auto-scrolling container with custom royal blue user pills and dark slate assistant cards.

---

## 🛠️ Tech Stack

- **UI Framework**: [Streamlit](https://streamlit.io/) with Custom CSS Glassmorphism
- **Agent Orchestration**: [LangChain](https://www.langchain.com/) (LangChain Community & Experimental)
- **AI Models**: OpenAI GPT-4o, Google Gemini 2.0 Flash, Anthropic Claude 3.5 Sonnet
- **Web Search**: DuckDuckGo Search API
- **Code Execution**: Python REPL Engine

---

## 🛡️ Privacy & Security

- **Local Execution**: All computations and agent invocations run locally.
- **Key Confidentiality**: API keys entered in the sidebar reside strictly in memory for the active session and are never logged or stored.

---
