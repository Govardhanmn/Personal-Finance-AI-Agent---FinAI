# 💸 FinAI – Your Personal Finance AI Agent

> **Personalized financial insights, planning tools, and real-time guidance.**

This AI Agent lays a robust foundation for a next-generation financial advisory ecosystem by integrating the reasoning power of Large Language Models with the precision of deterministic financial computations. It enables users to interact through natural language while delivering accurate, personalized, and context-aware insights across loans, investments, budgeting, and overall financial planning.

By enforcing tool-driven Python execution, the system effectively eliminates numerical inconsistencies, ensuring reliable outputs for EMI calculations, SIP projections, budget allocation, and goal planning. Built on a LangChain ReAct-based architecture, the agent dynamically selects and executes the most relevant tools, incorporates real-time financial indicators such as inflation and market trends, and leverages session-based memory to maintain continuity across multi-step interactions.

Beyond basic assistance, the system provides advanced financial diagnostics by analyzing key metrics such as Debt-to-Income ratios, savings rates, and inflation-adjusted forecasts, enabling users to gain a deeper understanding of their financial health. With support for multiple LLM providers, including OpenAI and Google Gemini, the platform offers flexibility in balancing performance, cost, and response speed.

Paired with an intuitive Streamlit interface featuring configurable AI settings and real-time conversational capabilities, this solution presents a scalable, efficient, and modern alternative to traditional financial advisory services—empowering users to make well-informed decisions on borrowing, saving, investing, and long-term wealth creation.

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

## 1. AI Model Configuration Panel (Left Sidebar)

- **LLM Provider Selection**: Choose the underlying language model (e.g., Gemini)  
- **API Key Input**: Securely enter API credentials  
- **Model Selection**: Select model variants (performance vs speed)  
- **Temperature Control**: Adjust creativity vs accuracy  
- **Reset Conversation**: Clear chat history and restart session  

---

## 2. Central Interaction Panel

- **Dynamic Chat Interface**: Ask queries like “Calculate EMI” or “Plan SIP”  
- **Context-Aware Responses**: Uses memory to personalize replies  

---

## 3. Intelligent Query Processing

- Converts user input into structured financial intent  
- Automatically selects the correct tool (EMI, SIP, Budget, etc.)  
- Ensures accurate, tool-driven computations  

---

## 4. Financial Insight Generation

- Converts calculations into:
  - Actionable recommendations  
  - Savings health analysis  
  - Debt insights  
  - Investment projections  

---

## 5. Real-Time Capabilities

- Fetches live data (inflation, market trends, news)  
- Integrates real-time insights into financial planning  

---

## 6. Stateful Conversation Management

- Maintains chat history and context  
- Supports follow-up queries without re-entry  
- Enables multi-step financial planning  

---

## 🛡️ Privacy & Security

- **Local Execution**: All computations and agent invocations run locally.
- **Key Confidentiality**: API keys entered in the sidebar reside strictly in memory for the active session and are never logged or stored.

---
