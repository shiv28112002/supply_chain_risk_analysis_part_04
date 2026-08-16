import os
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import (analyze_risk_events,analyze_shipments, get_weather)

print("Agent and tools loaded successfully")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("PART4_GOOGLE_API_KEY")
)
print("Gemini LLM loaded successfully")

# Available tools
tools = [analyze_risk_events, analyze_shipments, get_weather]

# Create the agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a supply-chain risk analysis agent. "
        "Use the available tools to analyze supply-chain risks and shipment performance. "
        "Use the weather tool when current weather information is relevant to the user's question. "
        "For weather questions, the user must provide a Shipment ID. "
        "If the Shipment ID is missing, ask the user to provide it instead of guessing or using another tool. "
        "For weather results, use exactly this format: "
        "Weather condition of Shipment ID is <shipment_id>\n"
        "Weather: <condition>\n"
        "Temperature: <temperature>°C"
        )
)
print("Agent created successfully")

# Run the agent

# QUERY 1

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What are the major supply-chain risk categories?"
        }
    ]
})

# Inspect LangChain's native tool-call representation
for message in result["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print("\n--- QUERY 1 TOOL CALL ---")
            print({"tool": tool_call["name"], "arguments": tool_call["args"]})

# Print final answer
print("\n--- QUERY 1 FINAL ANSWER ---")
final_content = result["messages"][-1].content

if isinstance(final_content, list):
    for item in final_content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))
else:
    print(final_content)
    
# QUERY 2

result2 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What are the most common shipment delay reasons?"
        }
    ]
})

for message in result2["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print("\n--- QUERY 2 TOOL CALL ---")
            print({
                "tool": tool_call["name"],
                "arguments": tool_call["args"]
            })

print("\n--- QUERY 2 FINAL ANSWER ---")

final_content = result2["messages"][-1].content

if isinstance(final_content, list):
    for item in final_content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))
else:
    print(final_content)

# QUERY 3 - INTERACTIVE WEATHER QUERY

result3 = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is the current weather condition for a shipment?"
        }
    ]
})

print("\n--- QUERY 3 AGENT RESPONSE ---")

final_content = result3["messages"][-1].content

if isinstance(final_content, list):
    for item in final_content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))
else:
    print(final_content)


# Ask the user for the Shipment ID
shipment_id = input("\nEnter Shipment ID: ").strip()


# Continue the same conversation
result3_followup = agent.invoke({
    "messages": result3["messages"] + [
        {
            "role": "user",
            "content": f"The Shipment ID is {shipment_id}."
        }
    ]
})


# Show the weather tool call
for message in result3_followup["messages"]:
    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            print("\n--- QUERY 3 TOOL CALL ---")
            print({
                "tool": tool_call["name"],
                "arguments": tool_call["args"]
            })


# Show final weather answer
print("\n--- QUERY 3 FINAL ANSWER ---")

final_content = result3_followup["messages"][-1].content

if isinstance(final_content, list):
    for item in final_content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))
else:
    print(final_content)