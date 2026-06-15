
import os
from typing import List, Dict, Any, Generator
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from agent.tool_definitions import TOOL_DEFINITIONS
from tools.tool_executor import execute_tool

load_dotenv()


from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


SYSTEM_PROMPT = """
You are an intelligent HR Assistant for employees at a company.
Rules:
- Answer directly.
- Keep answers under 100 to 500 words unless the user asks for details.
- Use bullet points only when necessary.
- Do not provide lengthy explanations.
- For yes/no questions, answer in one sentence.
- For policy questions, summarize the key points.
"""

def run_agent(user_message: str, history: List[Dict]) -> Generator[Dict, None, None]:
    messages = [{"role":"system","content":SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role":"user","content":user_message})

    while True:
        try:
            response = client.chat.completions.create(
    model="qwen3:8b",
    messages=messages,
)
        except Exception as e:
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
            import json
            args = json.loads(tc.function.arguments)

            yield {"type":"tool_call","tool":tc.function.name,"inputs":args}

            result = execute_tool(tc.function.name, args)

            yield {"type":"tool_result","tool":tc.function.name,"result":result}

            messages.append({
                "role":"tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

def run_agent_sync(user_message: str, history: List[Dict]) -> Dict[str, Any]:
    events = list(run_agent(user_message, history))
    tool_calls = [e for e in events if e["type"] == "tool_call"]
    final = next((e["text"] for e in events if e["type"] == "final"), "No answer.")
    error = next((e["text"] for e in events if e["type"] == "error"), None)
    return {"answer": final, "tool_calls": tool_calls, "error": error}
