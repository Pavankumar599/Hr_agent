import os
import json
from typing import List, Dict, Any, Generator
from dotenv import load_dotenv
from logger import logger

from agent.tool_definitions import TOOL_DEFINITIONS
from tools.tool_executor import execute_tool

load_dotenv()

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an HR Assistant. Use only these 5 tools — never answer from memory.

TOOL SELECTION:
- check_leave_balance → leave balance, leaves left, remaining leaves
- apply_for_leave → apply/book/request leave
- get_payslip → payslip, salary, net pay, take home, deductions
- search_hr_policy → policy, WFH, notice period, maternity, reimbursement, office hours
- escalate_to_hr → complaint, grievance, harassment, unfair, not happy, problem

STRICT RULES:
1. Extract employee_id (e.g. E001, E002) from every message and pass it to the tool.
2. Call the tool → read the result → give Final Answer. Do this in ONE cycle. Stop.
3. Never call the same tool twice with the same inputs. You already have that result.
4. Never use brave_search, web_search, or any unlisted tool.
5. Never say "contact HR" or "check the portal" — you are the HR system.
6. For yes/no questions answer in one sentence. For policy questions summarize briefly.
"""


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

MAX_ITERATIONS = 5


def run_agent(user_message: str, history: List[Dict]) -> Generator[Dict, None, None]:
    logger.info(f"USER_QUERY | message = {user_message} | history = {history}")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    iteration = 0
    seen_calls = set()  # track duplicate tool calls

    while iteration < MAX_ITERATIONS:
        iteration += 1

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1024,
            )
        except Exception as e:
            logger.error(f"GROQ_API_ERROR | error={str(e)}")
            yield {"type": "error", "text": str(e)}
            return

        msg = response.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)

        if not tool_calls:
            yield {"type": "final", "text": msg.content}
            return

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in tool_calls]
        })

        for tc in tool_calls:
            args = json.loads(tc.function.arguments)

            # DUPLICATE CALL GUARD — skip if already called with same args
            call_key = f"{tc.function.name}:{json.dumps(args, sort_keys=True)}"
            if call_key in seen_calls:
                logger.warning(f"DUPLICATE_CALL_SKIPPED | {call_key}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": "You already called this tool and got the result. Stop calling it again. Give the user a Final Answer now."
                })
                continue

            seen_calls.add(call_key)
            logger.info(f"TOOL_CALL | tool={tc.function.name} | inputs={args}")
            yield {"type": "tool_call", "tool": tc.function.name, "inputs": args}

            result = execute_tool(tc.function.name, args)
            logger.info(f"TOOL_RESULT | tool={tc.function.name} | result={result}")
            yield {"type": "tool_result", "tool": tc.function.name, "result": result}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

    # Exited loop without a final answer — force one
    logger.warning("MAX_ITERATIONS_REACHED | forcing final answer")
    yield {"type": "final", "text": "I've gathered the information needed. Please ask again if something is missing."}


def run_agent_sync(user_message: str, history: List[Dict]) -> Dict[str, Any]:
    events = list(run_agent(user_message, history))
    tool_calls = [e for e in events if e["type"] == "tool_call"]
    final = next((e["text"] for e in events if e["type"] == "final"), "No answer.")
    error = next((e["text"] for e in events if e["type"] == "error"), None)

    logger.info(f"SYNC_SUMMARY | tools_used={[t['tool'] for t in tool_calls]} | error={error}")

    return {"answer": final, "tool_calls": tool_calls, "error": error}