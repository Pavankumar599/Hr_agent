from agent.hr_agent import run_agent_sync

result = run_agent_sync(
    "I am E001-Aisha Sharma I want to know how many leaves I have left",
    history=[]
)

print("=== TOOL CALLS ===")
for tc in result["tool_calls"]:
    print(tc)

print("\n=== FINAL ANSWER ===")
print(result["answer"])

print("\n=== ERROR ===")
print(result["error"])