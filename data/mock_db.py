"""
data/mock_db.py  —  In-memory mock HR database.
Simulates what a real HRMS (like Darwinbox / BambooHR) would expose via API.
"""

from datetime import date

EMPLOYEES = {
    "E001": {
        "name": "Aisha Sharma",
        "email": "aisha.sharma@company.com",
        "department": "Engineering",
        "manager": "Ravi Menon",
        "join_date": "2022-06-01",
        "designation": "Software Engineer",
    },
    "E002": {
        "name": "Rohan Patel",
        "email": "rohan.patel@company.com",
        "department": "Marketing",
        "manager": "Priya Nair",
        "join_date": "2021-03-15",
        "designation": "Marketing Analyst",
    },
    "E003": {
        "name": "Sneha Iyer",
        "email": "sneha.iyer@company.com",
        "department": "HR",
        "manager": "Divya Rao",
        "join_date": "2023-01-10",
        "designation": "HR Executive",
    },
}

LEAVE_BALANCES = {
    "E001": {"casual": 8,  "sick": 7,  "earned": 12},
    "E002": {"casual": 5,  "sick": 10, "earned": 6},
    "E003": {"casual": 12, "sick": 3,  "earned": 15},
}

LEAVE_REQUESTS = []   # filled at runtime by apply_leave tool

PAYSLIPS = {
    "E001": {
        "May 2025":  {"gross": 85000, "deductions": 12000, "net": 73000, "tds": 8500},
        "April 2025":{"gross": 85000, "deductions": 12000, "net": 73000, "tds": 8500},
    },
    "E002": {
        "May 2025":  {"gross": 62000, "deductions": 9000,  "net": 53000, "tds": 5200},
        "April 2025":{"gross": 62000, "deductions": 9000,  "net": 53000, "tds": 5200},
    },
    "E003": {
        "May 2025":  {"gross": 55000, "deductions": 7500,  "net": 47500, "tds": 4000},
        "April 2025":{"gross": 55000, "deductions": 7500,  "net": 47500, "tds": 4000},
    },
}

HR_EMAIL = "hr@company.com"
