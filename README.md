---
title: Hr Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: ui/app.py
pinned: false
---

# HR Agent — Agentic AI with Tool Use

An end-to-end **HR AI Agent** built with Groq and LLaMA 3.1:8B model using tool use API.
Unlike a simple RAG bot, this agent *decides* which tools to call,
executes them, and loops until it has a complete answer.

---

## Project Structure

```
hr_agent/
│
├── data/
│   ├── HR_Header_Chunking_Policies.docx   ← your policy document
│   └── mock_db.py                         ← mock HRMS database (employees, leaves, payslips)
│
├── tools/
│   ├── chunker.py          ← header-based DOCX chunker
│   ├── policy_search.py    ← TF-IDF search over policy chunks
│   └── tool_executor.py    ← implements all 5 agent tools
│
├── agent/
│   ├── tool_definitions.py ← tool schemas sent to Groq API
│   └── hr_agent.py         ← the agentic loop (the core)
│
├── ui/
│   └── app.py              ← Streamlit chat UI with tool activity panel
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.9+
- A free **Groq API key** from [console.groq.com](https://console.groq.com)
- No local model or GPU required — Groq runs in the cloud for free

---

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/Pavankumar599/Hr_agent.git
cd hr_agent

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# 5. Run the app
streamlit run ui/app.py
```

---

## Architecture — How the Agent Works

```
Employee question
        │
        ▼
  LLaMA 3.1:8B (via Groq) reads question
  + system prompt
  + 5 tool definitions
        │
        ▼
  "I need to call search_hr_policy first"
        │
        ▼
  tool_executor.py runs the function
  → returns real result
        │
        ▼
  LLaMA 3.1:8B reads result
  "Now I need check_leave_balance too"
        │
        ▼
  tool_executor.py runs again
        │
        ▼
  Model has enough context → writes final answer
        │
        ▼
  Answer shown in chat UI
```

The loop repeats until the model stops calling tools and gives a text answer.
This is the **ReAct pattern** (Reason + Act).

---

## The 5 Tools

| Tool | What it does |
|---|---|
| `search_hr_policy` | TF-IDF search over header-chunked policy DOCX |
| `check_leave_balance` | Returns casual/sick/earned days remaining |
| `apply_for_leave` | Validates and books a leave request |
| `get_payslip` | Returns gross/deductions/net pay for a month |
| `escalate_to_hr` | Sends an escalation email to the HR team |

---

## Demo Employees

| ID | Name | Department |
|---|---|---|
| E001 | Aisha Sharma | Engineering |
| E002 | Rohan Patel | Marketing |
| E003 | Sneha Iyer | HR |

---

## Environment Variables

Create a `.env` file in the root of your project:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at [console.groq.com](https://console.groq.com) — no credit card required.

---

## Deployment on Streamlit Cloud

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file path to `ui/app.py`
5. Under **Advanced Settings → Secrets**, add:
```
GROQ_API_KEY = "your_groq_api_key_here"
```
6. Click **Deploy** — your app will be live in 2-3 minutes

---

## Sample Conversations

**Policy question:**
> "What is the WFH eligibility policy?"
→ Agent calls `search_hr_policy`, returns grounded answer with section citation.

**Leave balance:**
> "How many leaves does E001 have?"
→ Agent calls `check_leave_balance(E001)`.

**Apply leave (multi-tool):**
> "Apply casual leave for E002 from 2025-07-10 to 2025-07-11 for personal work"
→ Agent calls `check_leave_balance` first, then `apply_for_leave`.

**Payslip:**
> "Show me the payslip for E001 for May 2025"
→ Agent calls `get_payslip(E001, May 2025)`.

**Out of scope:**
> "Write me a Python script"
→ Agent politely declines and stays in HR scope.

---

## RAG vs Agent — Key Difference

| | RAG Bot | HR Agent (this) |
|---|---|---|
| Flow | Fixed: retrieve → answer | Dynamic: model decides |
| Tools | Only policy search | 5 tools + can chain them |
| Actions | Read-only | Can apply leave, escalate |
| Memory | Per-question | Multi-turn conversation |
| Reasoning | None | Decides what to do next |
| Model | N/A | LLaMA 3.1:8B via Groq (free) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.1:8B via Groq API |
| Agent Framework | Custom ReAct loop |
| Frontend | Streamlit |
| Policy Search | TF-IDF (scikit-learn) |
| Deployment | Streamlit Cloud |

---

## Troubleshooting

**Groq API key error:**
```
AuthenticationError: Invalid API key
```
→ Check your `.env` file has the correct `GROQ_API_KEY` value.

**Module not found:**
```
ModuleNotFoundError: No module named 'groq'
```
→ Run `pip install -r requirements.txt` inside your virtual environment.

**Streamlit Cloud deployment failing:**
→ Make sure `GROQ_API_KEY` is added in Streamlit Cloud secrets, not just `.env`.

**Tool execution failing:**
→ Check `tool_executor.py` logs and ensure all dependencies are installed.