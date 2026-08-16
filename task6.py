import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from tools import analyze_risk_events


print("Task 6 - LangChain Tool-Calling Agent")
print("Tool loaded successfully")


llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=os.getenv("PART4_GOOGLE_API_KEY"))

print("Gemini LLM loaded successfully")

tools = [analyze_risk_events]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a supply-chain risk analysis agent. "
        "Use the available risk-analysis tool whenever "
        "the user asks for factual information about "
        "historical supply-chain risks. "
        "Choose the appropriate analysis type based on "
        "the user's question. "
        "Do not invent data."
    )
)

print("Agent created successfully")

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Which supply-chain risk category has the most events?"
        }
    ]
})

for message in result["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print("\n--- TASK 6 TOOL CALL ---")
            print({"tool": tool_call["name"],"arguments": tool_call["args"]})

print("\n--- TASK 6 FINAL ANSWER ---")

final_content = result["messages"][-1].content

if isinstance(final_content, list):

    for item in final_content:

        if isinstance(item, dict) and item.get("type") == "text":

            print(item.get("text", ""))

else:

    print(final_content)