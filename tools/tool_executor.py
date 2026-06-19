"""
tools/tool_executor.py

Implements every tool the HR agent can call.
Each function mirrors the tool definition sent to Claude.
"""

import json
from datetime import date, datetime
from data.mock_db import EMPLOYEES, LEAVE_BALANCES, LEAVE_REQUESTS, PAYSLIPS, HR_EMAIL
from tools.policy_search import search_policy
from logger import logger

# ── Tool 1: search_hr_policy ────────────────────────────────────────────────

def tool_search_hr_policy(query: str) -> str:

    # Logg
    logger.info(f"POLICY_SEARCH | query = {query}")

    results = search_policy(query, top_k=3)

    if not results:
        logger.warning(f"POLICY_SEARCH_NO_RESULTS | no results found for query = {query}")
        return "No relevant policy found for this query."
    
    parts = []
    for chunk, score in results:
        heading = f"{chunk.section} > {chunk.subsection}" if chunk.subsection else chunk.section
        parts.append(f"[{heading}]\n{chunk.content}")
    
    logger.info(f"POLICY_SEARCH_RESULTS | found {len(results)} chunks for query = {query}")
    return "\n\n---\n\n".join(parts)


# ── Tool 2: check_leave_balance ─────────────────────────────────────────────

def tool_check_leave_balance(employee_id: str) -> str:
    #Log
    logger.info(f"CHECK_LEAVE_BALANCE | employee_id = {employee_id}")
    emp = EMPLOYEES.get(employee_id)
    if not emp:
        return f"Employee ID '{employee_id}' not found."
    bal = LEAVE_BALANCES.get(employee_id, {})

    logger.info(f"CHECK_LEAVE_BALANCE_RESULT | employee_id = {employee_id} | balance = {bal}")
    return (
        f"Leave balance for {emp['name']} ({employee_id}):\n"
        f"  Casual leave  : {bal.get('casual', 0)} days remaining\n"
        f"  Sick leave    : {bal.get('sick',   0)} days remaining\n"
        f"  Earned leave  : {bal.get('earned', 0)} days remaining"
    )


# ── Tool 3: apply_for_leave ─────────────────────────────────────────────────

def tool_apply_for_leave(employee_id: str, leave_type: str,
                         start_date: str, end_date: str, reason: str) -> str:
    
    logger.info(f"APPLY_FOR_LEAVE | employee_id = {employee_id} | leave_type = {leave_type} | ")
    """
    IMPORTANT:

    Before calling this tool you MUST call
    check_leave_balance.

    Never apply leave without verifying
    sufficient balance.
    """
    emp = EMPLOYEES.get(employee_id)
    if not emp:
        logger.info(f"APPLY_FOR_LEAVE_FAILED | employee_id = {employee_id} not found")
        return f"Employee ID '{employee_id}' not found."

    lt = leave_type.lower().replace(" leave", "").strip()
    bal = LEAVE_BALANCES.get(employee_id, {})

    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date,   "%Y-%m-%d").date()
    except ValueError:

        logger.warning(f"APPLY_LEAVE | invalid date format | start={start_date} end={end_date}")
        return "Invalid date format. Use YYYY-MM-DD."

    days = (ed - sd).days + 1
    if days <= 0:
        logger.warning(f"APPLY_LEAVE | invalid date range | days={days}")  # ✅ LOG
        return "End date must be after start date."

    if lt not in bal:
        logger.warning(f"APPLY_LEAVE | unknown leave type={leave_type}")
        return f"Unknown leave type '{leave_type}'. Choose from: casual, sick, earned."
    if bal[lt] < days:
        logger.warning(f"APPLY_LEAVE | insufficient balance | requested={days} available={bal[lt]}") 
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

    logger.info(f"APPLY_LEAVE | SUCCESS | req_id={req_id} | employee={emp['name']} | days={days} | remaining={bal[lt]}") 
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

    logger.info(f"GET_PAYSLIP | employee_id={employee_id} | month={month}")  # ✅ LOG

    emp = EMPLOYEES.get(employee_id)
    if not emp:
        logger.warning(f"GET_PAYSLIP | employee not found | id={employee_id}")  # ✅ LOG
        return f"Employee ID '{employee_id}' not found."
    slips = PAYSLIPS.get(employee_id, {})
    slip  = slips.get(month)
    if not slip:
        available = list(slips.keys()) or ["No payslips available"]

        logger.warning(f"GET_PAYSLIP | month not found | month={month} | available={available}")  # ✅ LOG
        return f"Payslip not found for {month}. Available months: {', '.join(available)}"
    
    logger.info(f"GET_PAYSLIP | SUCCESS | employee={emp['name']} | month={month} | net=₹{slip['net']}")  # ✅ LOG
    
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
    logger.info(f"ESCALATE | employee_id={employee_id} | subject={subject}")  # ✅ LOG

    emp = EMPLOYEES.get(employee_id, {})
    name  = emp.get("name", employee_id)
    email = emp.get("email", "unknown")
    # Simulated — just log it
    HR_EMAIL = 'hr@ANSR.com'
    print(f"\n[ESCALATION EMAIL]\nTo: {HR_EMAIL}\nFrom: {email}\n"
          f"Subject: {subject}\nMessage: {message}\n")
    
    logger.info(f"ESCALATE | SUCCESS | from={email} | to={HR_EMAIL} | subject={subject}")  # ✅ LOG
    
    return (
        f"Escalation sent to HR team at {HR_EMAIL}.\n"
        f"  From    : {name} ({email})\n"
        f"  Subject : {subject}\n"
        f"Your query has been logged. HR will respond within 1–2 business days."
    )


# ── Dispatch table ──────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    logger.info(f"EXECUTE_TOOL | name={name} | inputs={inputs}")  # ✅ LOG
    try:
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
        
        logger.warning(f"EXECUTE_TOOL | unknown tool={name}")  # ✅ LOG
        return f"Unknown tool: {name}"
    
    except Exception as e:
        logger.error(f"EXECUTE_TOOL | CRASHED | tool={name} | error={str(e)}")  # ✅ LOG
        return f"Tool '{name}' failed with error: {str(e)}"
