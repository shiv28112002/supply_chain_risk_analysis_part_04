import os
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import analyze_risk_events

print("Task 7 - Multi-Turn Memory Test")
print("Tool loaded successfully")

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=os.getenv("PART4_GOOGLE_API_KEY"))

print("Gemini LLM loaded successfully")

# Use the existing risk-analysis tool

tools = [analyze_risk_events]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a supply-chain risk analysis agent. "
        "Use the available tool to analyze historical supply-chain risks. "
        "Use information from previous turns when answering follow-up questions. "
        "Do not invent data. "
        "Use the risk-analysis tool whenever factual risk information is required."
    )
)

print("Agent created successfully")

query1 = "How many Logistics risk events are there?"

result1 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": query1
        }
    ]
})

for message in result1["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print("\n--- TURN 1 TOOL CALL ---")
            print({"tool": tool_call["name"],"arguments": tool_call["args"]})

print("\n--- TURN 1 ---")

final_content = result1["messages"][-1].content

if isinstance(final_content, list):
    for item in final_content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))

else:
    print(final_content)


query2 = (
    "Now, for the same risk dataset, "
    "what is the current status distribution?"
)

result2 = agent.invoke({
    "messages": result1["messages"] + [
        {
            "role": "user",
            "content": query2
        }
    ]
})

for message in result2["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print("\n--- TURN 2 TOOL CALL ---")
            print({"tool": tool_call["name"],"arguments": tool_call["args"]})

print("\n--- TURN 2 ---")

final_content = result2["messages"][-1].content
if isinstance(final_content, list):
    for item in final_content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))

else:
    print(final_content)