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

1. AI Model Configuration Panel (Left Sidebar)
•	LLM Provider Selection: Allows users to choose the underlying language model (e.g., Gemini).
•	API Key Input: Securely stores and uses the user’s API credentials for model access.
•	Model Selection: Lets users pick specific model variants for performance vs speed trade-offs.
•	Temperature Control: Adjusts response creativity vs accuracy (lower = more deterministic financial outputs).
•	Reset Conversation: Clears chat history and resets the session state for a fresh interaction.
2. Central Interaction Panel
•	Dynamic Chat Interface: Users can input natural language queries (e.g., “Calculate my EMI” or “Plan my SIP”).
•	Context-Aware Responses: The agent uses conversation memory to refine and personalize responses over time.
3. Intelligent Query Processing
•	Converts user input into structured financial intent
•	Automatically selects the correct backend tool (EMI, SIP, Budget, etc.)
•	Ensures accurate, tool-driven computation rather than guesswork
4. Financial Insight Generation
•	Transforms raw calculations into:
•	Actionable recommendations
•	Savings health analysis
•	Debt sustainability insights
•	Investment projections
5. Real-Time Capabilities
•	Fetches live financial data such as inflation, market trends, and news
•	Integrates external data into planning (especially for goal-based calculations)
6. Stateful Conversation Management
•	Maintains chat history and financial context
•	Enables follow-up queries without re-entering data
•	Supports multi-step financial planning workflows

---

## 🛡️ Privacy & Security

- **Local Execution**: All computations and agent invocations run locally.
- **Key Confidentiality**: API keys entered in the sidebar reside strictly in memory for the active session and are never logged or stored.

---
