"""
tools/tool_executor.py

Implements every tool the HR agent can call.
Each function mirrors the tool definition sent to Claude.
"""

import json
from datetime import date, datetime
from data.mock_db import EMPLOYEES, LEAVE_BALANCES, LEAVE_REQUESTS, PAYSLIPS, HR_EMAIL
from tools.policy_search import search_policy


# ── Tool 1: search_hr_policy ────────────────────────────────────────────────

def tool_search_hr_policy(query: str) -> str:
    results = search_policy(query, top_k=3)
    if not results:
        return "No relevant policy found for this query."
    parts = []
    for chunk, score in results:
        heading = f"{chunk.section} > {chunk.subsection}" if chunk.subsection else chunk.section
        parts.append(f"[{heading}]\n{chunk.content}")
    return "\n\n---\n\n".join(parts)


# ── Tool 2: check_leave_balance ─────────────────────────────────────────────

def tool_check_leave_balance(employee_id: str) -> str:
    emp = EMPLOYEES.get(employee_id)
    if not emp:
        return f"Employee ID '{employee_id}' not found."
    bal = LEAVE_BALANCES.get(employee_id, {})
    return (
        f"Leave balance for {emp['name']} ({employee_id}):\n"
        f"  Casual leave  : {bal.get('casual', 0)} days remaining\n"
        f"  Sick leave    : {bal.get('sick',   0)} days remaining\n"
        f"  Earned leave  : {bal.get('earned', 0)} days remaining"
    )


# ── Tool 3: apply_for_leave ─────────────────────────────────────────────────

def tool_apply_for_leave(employee_id: str, leave_type: str,
                         start_date: str, end_date: str, reason: str) -> str:
    """
    IMPORTANT:

    Before calling this tool you MUST call
    check_leave_balance.

    Never apply leave without verifying
    sufficient balance.
    """
    emp = EMPLOYEES.get(employee_id)
    if not emp:
        return f"Employee ID '{employee_id}' not found."

    lt = leave_type.lower().replace(" leave", "").strip()
    bal = LEAVE_BALANCES.get(employee_id, {})

    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date,   "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

    days = (ed - sd).days + 1
    if days <= 0:
        return "End date must be after start date."

    if lt not in bal:
        return f"Unknown leave type '{leave_type}'. Choose from: casual, sick, earned."
    if bal[lt] < days:
        return (f"Insufficient {leave_type} balance. "
                f"Requested: {days} days, Available: {bal[lt]} days.")

    # Deduct and record
    bal[lt] -= days
    req_id = f"REQ{len(LEAVE_REQUESTS)+1001}"
    LEAVE_REQUESTS.append({
        "id": req_id, "employee_id": employee_id,
        "name": emp["name"], "leave_type": leave_type,
        "start": start_date, "end": end_date,
        "days": days, "reason": reason, "status": "Pending manager approval"
    })

    return (
        f"Leave request submitted successfully!\n"
        f"  Request ID  : {req_id}\n"
        f"  Employee    : {emp['name']}\n"
        f"  Type        : {leave_type}\n"
        f"  Dates       : {start_date} to {end_date} ({days} day(s))\n"
        f"  Status      : Pending manager approval ({emp['manager']})\n"
        f"  Remaining {leave_type}: {bal[lt]} days"
    )


# ── Tool 4: get_payslip ─────────────────────────────────────────────────────

def tool_get_payslip(employee_id: str, month: str) -> str:
    emp = EMPLOYEES.get(employee_id)
    if not emp:
        return f"Employee ID '{employee_id}' not found."
    slips = PAYSLIPS.get(employee_id, {})
    slip  = slips.get(month)
    if not slip:
        available = list(slips.keys()) or ["No payslips available"]
        return f"Payslip not found for {month}. Available months: {', '.join(available)}"
    return (
        f"Payslip — {emp['name']} ({month}):\n"
        f"  Gross salary  : ₹{slip['gross']:,}\n"
        f"  Total deductions: ₹{slip['deductions']:,}\n"
        f"  TDS           : ₹{slip['tds']:,}\n"
        f"  Net salary    : ₹{slip['net']:,}\n"
        f"  Credited on   : Last working day of {month}"
    )


# ── Tool 5: escalate_to_hr ──────────────────────────────────────────────────

def tool_escalate_to_hr(employee_id: str, subject: str, message: str) -> str:
    emp = EMPLOYEES.get(employee_id, {})
    name  = emp.get("name", employee_id)
    email = emp.get("email", "unknown")
    # Simulated — just log it
    HR_EMAIL = 'hr@ANSR.com'
    print(f"\n[ESCALATION EMAIL]\nTo: {HR_EMAIL}\nFrom: {email}\n"
          f"Subject: {subject}\nMessage: {message}\n")
    return (
        f"Escalation sent to HR team at {HR_EMAIL}.\n"
        f"  From    : {name} ({email})\n"
        f"  Subject : {subject}\n"
        f"Your query has been logged. HR will respond within 1–2 business days."
    )


# ── Dispatch table ──────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    if name == "search_hr_policy":
        return tool_search_hr_policy(**inputs)
    if name == "check_leave_balance":
        return tool_check_leave_balance(**inputs)
    if name == "apply_for_leave":
        return tool_apply_for_leave(**inputs)
    if name == "get_payslip":
        return tool_get_payslip(**inputs)
    if name == "escalate_to_hr":
        return tool_escalate_to_hr(**inputs)
    return f"Unknown tool: {name}"
