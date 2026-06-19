import os
import json
from typing import List, Dict, Any, Generator
from dotenv import load_dotenv
from logger import logger

from agent.tool_definitions import TOOL_DEFINITIONS
from tools.tool_executor import execute_tool
from langchain_groq import ChatGroq

load_dotenv()

from langchain_groq import ChatGroq
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an intelligent HR Assistant for employees at a company.

Rules:
- Answer directly.
- Use bullet points only when necessary.
- For yes/no questions, answer in one sentence.
- For policy questions, summarize the key points.
- NEVER say "contact HR" or "check the portal" — you ARE the HR system.
- Always extract the employee_id from the message (e.g. E001, E002) 
  and pass it to every tool call.

CRITICAL TOOL RULES — always follow these, no exceptions:

1. LEAVE BALANCE — keywords: leaves left, leave balance, how many leaves,
   remaining leaves, casual/sick/annual leaves
   → MUST call check_leave_balance(employee_id) immediately

2. APPLY LEAVE — keywords: apply leave, book leave, take a day off,
   request leave, need leave
   → MUST call apply_for_leave(employee_id, ...) immediately

3. COMPLAINT / ESCALATION — keywords: complaint, complain, issue, problem,
   harassment, grievance, unfair, not happy, raise a concern, report
   → MUST call escalate_to_hr(employee_id, ...) immediately

4. PAYSLIP / SALARY — keywords: payslip, salary, pay slip, take home,
   how much paid, salary slip
   → MUST call get_payslip(employee_id) immediately

5. POLICY QUESTIONS — keywords: policy, rules, WFH, work from home,
   office hours, maternity, notice period
   → MUST call search_hr_policy(query) immediately

NEVER answer any of the above from your own knowledge.
ALWAYS call the correct tool. That is your only job.
"""

# Convert Anthropic-style tools to OpenAI-style for Ollama
def convert_tools_for_openai(tools):
    converted = []
    for tool in tools:
        converted.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
        })
    return converted

OPENAI_TOOLS = convert_tools_for_openai(TOOL_DEFINITIONS)


def run_agent(user_message: str, history: List[Dict]) -> Generator[Dict, None, None]:
    # log1 capture everything incoming question
    logger.info(f"USER_QUERY | message = {user_message} | history = {history}")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    while True:
        try:
            response = client.chat.completions.create(
               model="llama-3.1-8b-instant",
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            # LOG Capture API errors
            logger.error(f"GROQ_API_ERROR | error={str(e)}")

            yield {"type": "error", "text": str(e)}
            return

        msg = response.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)

        if not tool_calls:
            # LOG4 Capture the final answer
            yield {"type": "final", "text": msg.content}
            return

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in tool_calls]
        })

        for tc in tool_calls:
            args = json.loads(tc.function.arguments)
            # LOG2 which tool was called and with what inputs
            logger.info(f"TOOL_CALL | tool={tc.function.name} | inputs={args}")
            yield {"type": "tool_call", "tool": tc.function.name, "inputs": args}

            result = execute_tool(tc.function.name, args)

            # LOG3 - what the tool returned
            logger.info(f"TOOL_RESULT | tool={tc.function.name} | result={result}")
            yield {"type": "tool_result", "tool": tc.function.name, "result": result}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })


def run_agent_sync(user_message: str, history: List[Dict]) -> Dict[str, Any]:
    events = list(run_agent(user_message, history))
    tool_calls = [e for e in events if e["type"] == "tool_call"]
    final = next((e["text"] for e in events if e["type"] == "final"), "No answer.")
    error = next((e["text"] for e in events if e["type"] == "error"), None)
    
    # LOG - sync wrapper summary
    logger.info(f"SYNC_SUMMARY | tools_used= {[t['tool'] for t in tool_calls]} | error={error}")
    
    return {"answer": final, "tool_calls": tool_calls, "error": error}