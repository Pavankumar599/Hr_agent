"""
agent/tool_definitions.py

Defines the 5 tools Claude can call.
These are sent in every API request so Claude knows what's available.
"""

TOOL_DEFINITIONS = [
    {
        "name": "search_hr_policy",
        "description": (
            "Search the HR policy document for information about company policies. "
            "Use this for questions about leave rules, WFH policy, compensation, "
            "reimbursements, onboarding, code of conduct, IT security, and benefits. "
            "Always call this first for policy-related questions before answering from memory."
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
            "Check the remaining leave balance (casual, sick, earned) for an employee. "
            "Call this when an employee asks how many leaves they have left, "
            "or before applying for leave to verify availability."
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
            "Submit a leave application for an employee. "
            "Use this when an employee explicitly asks to apply for or book leave. "
            "Always check leave balance first. Require all fields before calling."
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
            "Retrieve the payslip summary for an employee for a given month. "
            "Use when an employee asks about their salary, net pay, TDS, or payslip."
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
            "Send an escalation email to the HR team when the query cannot be resolved "
            "by policy search or available tools. Use for complex, sensitive, or "
            "out-of-policy situations that need human HR attention."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID raising the issue."},
                "subject":     {"type": "string", "description": "Brief subject of the issue."},
                "message":     {"type": "string", "description": "Detailed description of the issue."}
            },
            "required": ["employee_id", "subject", "message"]
        }
    }
]
