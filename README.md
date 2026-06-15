# HR Agent — Agentic AI with Tool Use

An end-to-end **HR AI Agent** built on Claude's tool use API.
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
│   ├── tool_definitions.py ← tool schemas sent to Claude API
│   └── hr_agent.py         ← the agentic loop (the core)
│
├── ui/
│   └── app.py              ← Streamlit chat UI with tool activity panel
│
├── requirements.txt
└── README.md
```

---

## Architecture — How the Agent Works

```
Employee question
        │
        ▼
  mistral reads question
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
  mistral reads result
  "Now I need check_leave_balance too"
        │
        ▼
  tool_executor.py runs again
        │
        ▼
  Claude has enough → writes final answer
        │
        ▼
  Answer shown in chat UI
```

The loop repeats until Claude stops calling tools and gives a text answer.
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

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt


# 3. Launch the chatbot
streamlit run ui/app.py
```

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

| | RAG Bot (previous) | HR Agent (this) |
|---|---|---|
| Flow | Fixed: retrieve → answer | Dynamic: Claude decides |
| Tools | Only policy search | 5 tools + can chain them |
| Actions | Read-only | Can apply leave, escalate |
| Memory | Per-question | Multi-turn conversation |
| Reasoning | None | Decides what to do next |
