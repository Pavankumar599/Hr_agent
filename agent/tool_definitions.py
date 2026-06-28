"""
agent/tool_definitions.py

Defines the 5 tools Claude can call.
These are sent in every API request so Claude knows what's available.
"""

TOOL_DEFINITIONS = [
    {
        "name": "search_hr_policy",
        "description": (
            "ALWAYS call this tool when an employee asks about company policies, rules, "
            "or guidelines. "
            "Trigger keywords: policy, rules, WFH, work from home, office hours, "
            "maternity, paternity, notice period, reimbursement, onboarding, "
            "code of conduct, IT security, benefits, compensation, dress code. "
            "Do NOT answer policy questions from memory — always call this tool. "
            "Use for questions about leave rules, WFH policy, compensation, "
            "reimbursements, onboarding, code of conduct, IT security, and benefits."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query describing the policy topic to look up."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_leave_balance",
        "description": (
            "ALWAYS call this tool when an employee asks about their leave balance "
            "or how many leaves they have remaining. "
            "Trigger keywords: leaves left, leave balance, how many leaves, "
            "remaining leaves, casual leaves, sick leaves, earned leaves, "
            "annual leaves, how many days off, leave count. "
            "Do NOT tell the employee to check the portal — call this tool immediately. "
            "Extract employee_id from their message (e.g. E001, E002). "
            "Also call this before applying leave to verify availability."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The employee ID, e.g. E001, E002, E003."
                }
            },
            "required": ["employee_id"]
        }
    },
    {
        "name": "apply_for_leave",
        "description": (
            "ALWAYS call this tool when an employee wants to apply, book, or request leave. "
            "Trigger keywords: apply leave, book leave, take a day off, request leave, "
            "need leave, want to take leave, submit leave. "
            "Always call check_leave_balance first to verify balance is available. "
            "Ask employee for missing details (leave_type, start_date, end_date, reason) "
            "before calling if not provided. "
            "Require all fields before submitting."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID."},
                "leave_type":  {"type": "string", "description": "One of: casual, sick, earned."},
                "start_date":  {"type": "string", "description": "Start date in YYYY-MM-DD format."},
                "end_date":    {"type": "string", "description": "End date in YYYY-MM-DD format."},
                "reason":      {"type": "string", "description": "Reason for leave."}
            },
            "required": ["employee_id", "leave_type", "start_date", "end_date", "reason"]
        }
    },
    {
        "name": "get_payslip",
        "description": (
            "ALWAYS call this tool when an employee asks about their salary, "
            "payslip, net pay, take home, or deductions. "
            "Trigger keywords: payslip, salary, pay slip, take home, net pay, "
            "how much paid, salary slip, TDS, deductions, PF, provident fund. "
            "Do NOT answer salary questions from memory — always call this tool. "
            "Extract employee_id and month from their message. "
            "If month is not mentioned, use the current month."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID."},
                "month":       {"type": "string", "description": "Month and year, e.g. 'May 2025'."}
            },
            "required": ["employee_id", "month"]
        }
    },
    {
        "name": "escalate_to_hr",
        "description": (
            "ALWAYS call this tool when an employee wants to raise a complaint, "
            "report an issue, express a grievance, mention harassment, unfair treatment, "
            "salary problems, or any negative experience. "
            "Trigger keywords: complaint, complain, issue, problem, report, grievance, "
            "not happy, harassment, unfair, concern, raise, escalate, angry, frustrated. "
            "Do NOT answer these with general advice — always call this tool immediately. "
            "Extract the employee_id from their message if they provide it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID raising the issue."},
                "subject":     {"type": "string", "description": "Brief subject of the issue."},
                "message":     {"type": "string", "description": "Detailed description of the issue."}
            },
            "required": ["employee_id", "message"]
        }
    }
]