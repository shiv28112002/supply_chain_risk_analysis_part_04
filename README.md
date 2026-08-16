# Part 4 - Agentic AI System: Supply-Chain Risk Intelligence

## 1. Introduction

This is Part 4 of my capstone project. In this part, I built an Agentic AI system for my supply-chain risk analysis project using LangChain and Google Gemini.

The main idea of this part is different from normal data analysis. Instead of directly calling a Python function for every question, I wanted the LLM to understand the question and decide which tool should be used.

My project mainly works with supply-chain risk events, shipment information and weather information.

The agent can:

- analyze historical supply-chain risk events
- analyze shipment information
- get current weather information for a shipment
- decide which tool is needed for a question
- continue a conversation using previous messages
- use a separate conditional workflow for risk-level routing

I selected **Option A - LangChain Single Autonomous Agent**.

---

# 2. Why I Selected LangChain

I selected LangChain because it was suitable for connecting my Gemini model with the Python tools that I created for the supply-chain project.

The basic idea of my system is:

```text
User Question
      ↓
Gemini
      ↓
LangChain Agent
      ↓
Select Tool
      ↓
Run Tool
      ↓
Get Result
      ↓
Final Answer
```

This makes the project more agentic instead of being only a normal Python data-analysis program.

---

# 3. Technologies Used

- Python
- LangChain
- Google Gemini
- `langchain-google-genai`
- Pandas
- CSV datasets
- Live weather API
- VS Code

---

# 4. Project Files

```text
part_04/
│
├── agent.py
├── tools.py
├── task6.py
├── task7.py
├── task8_workflow.py
├── test_tool.py
├── README.md
│
├── data/
│   ├── risk_events.csv
│   └── shipment.csv
│
└── outputs/
```

### Main files

**`tools.py`**

Contains the tools used by the agent. I kept this file unchanged while working on the later tasks.

**`agent.py`**

Contains my main Part 4 agent and the main demonstrations, including risk analysis, shipment analysis and weather interaction.

**`task6.py`**

Used to separately test the LangChain tool-calling agent.

**`task7.py`**

Used to demonstrate two-turn conversation memory.

**`task8_workflow.py`**

Contains the separate conditional workflow.

---

# 5. Tools Used in My Project

I created tools for different supply-chain tasks.

## Tool Contract Table

| Tool | What it does | Parameter | Type |
|---|---|---|---|
| `analyze_risk_events` | Analyzes historical supply-chain risk events | `analysis_type` | Read |
| `analyze_shipments` | Analyzes shipment information | Tool-defined parameter | Read |
| `get_weather` | Gets current weather information for a shipment | Shipment ID | Read |

All of my tools are read-only. They do not change or delete the original data.

---

# 6. Risk Analysis Tool

The `analyze_risk_events` tool is one of the main tools in my project.

It can perform different types of analysis:

```text
category
type
severity
loss
impact_area
root_cause
status
```

For example, when the agent decides to use:

```python
analyze_risk_events("category")
```

the tool checks the risk dataset and returns the number of risk events in each category.

It can also analyze severity, estimated loss, impact area, root cause and status.

---

# 7. Shipment Analysis Tool

The shipment tool is used for questions related to shipment performance.

For example, it can be used when the user asks about shipment delays or shipment-related information.

This tool reads the shipment data and returns the requested analysis.

---

# 8. Weather Tool

The weather tool is different from the local analysis tools because it uses a live external weather service.

I used it to make the project more realistic because supply-chain risks can be affected by current weather conditions.

For weather questions, I made the agent ask for a Shipment ID if it has not been provided.

Example:

```text
User:
What is the current weather condition for a shipment?

Agent:
Please provide the Shipment ID.

User:
The Shipment ID is <shipment_id>.

Agent:
Weather condition of Shipment ID is <shipment_id>
Weather: <condition>
Temperature: <temperature>°C
```

Weather data by Open-Meteo.com (CC BY 4.0).

---

# 9. Tool Safety

I kept the tools as read-only tools.

They do not:

- modify the CSV files
- delete records
- update records
- change the original dataset

The tools also check their inputs and return an error message when an invalid analysis type or required value is missing.

This helps prevent a tool error from directly stopping the whole agent.

---

# 10. Task 6 - LangChain Tool-Calling Agent

## What I had to do

For Task 6, the main requirement was to show that the agent can use tools instead of only generating a normal text response.

The agent should understand the user's question and select the correct tool.

## Why I changed the implementation

At the beginning, I already had Python functions for my supply-chain analysis.

But just having functions is not enough to show an Agentic AI system.

I needed to connect those tools with the LLM so that the model could decide which tool to use.

So the change was made in the **agent part**, not in `tools.py`.

I did not change the existing risk-analysis tool just to make Task 6 work.

The flow became:

```text
User Question
      ↓
Gemini understands the question
      ↓
Agent selects the required tool
      ↓
Tool is called
      ↓
Tool analyzes the data
      ↓
Agent gives the final answer
```

My installed LangChain version is `1.3.15`, so the working Task 6 implementation uses the `create_agent` API available in my environment.

The study material also explains the tool-calling agent approach and the use of a bounded execution limit to avoid an agent running indefinitely.

## Task 6 Query

I tested the following question:

> Which supply-chain risk category has the most events?

The agent automatically selected the risk-analysis tool.

## Tool Call Captured

The actual output was:

```text
--- TASK 6 TOOL CALL ---
{
    'tool': 'analyze_risk_events',
    'arguments': {
        'analysis_type': 'category'
    }
}
```

This is important because I did not manually write:

```python
analyze_risk_events("category")
```

for this particular question in the test.

The agent decided that category analysis was required.

## Result

The tool returned:

```text
Logistics          1470
Inventory          1039
Supplier            780
Warehouse           749
Product Quality     464
Weather             248
Transportation      151
Financial            99
```

The final agent answer was:

```text
Based on historical supply-chain risk data, the risk category
with the most events is Logistics, with a total of 1,470 events.
```

## What I demonstrated in Task 6

Task 6 shows that:

- the Gemini model is connected to LangChain
- the tools can be given to the agent
- the agent can choose a tool
- the tool arguments are structured
- the selected tool actually runs
- the final answer is based on the dataset

---

# 11. How I Captured the Tool Call

For the tool-call evidence, I used LangChain's native `tool_calls` information.

I printed the tool name and arguments like this:

```python
print({
    "tool": tool_call["name"],
    "arguments": tool_call["args"]
})
```

This gives an output such as:

```text
{
    "tool": "analyze_risk_events",
    "arguments": {
        "analysis_type": "category"
    }
}
```

I used the framework's native representation instead of writing a separate JSON parser for the LLM's response.

---

# 12. Task 7 - Multi-Turn Memory

## What I had to demonstrate

For Task 7, I needed to show that the agent can continue a conversation and use information from an earlier turn.

A new LLM call does not automatically know what happened in a previous call. Therefore, I passed the previous messages into the next agent invocation.

The basic flow is:

```text
Turn 1
  ↓
Agent + Tool
  ↓
Conversation History
  ↓
Turn 2
  ↓
Agent + Tool
```

## Turn 1

### Question

```text
How many Logistics risk events are there?
```

### Tool Call

```text
{
    "tool": "analyze_risk_events",
    "arguments": {
        "analysis_type": "category"
    }
}
```

### Answer

```text
There are 1,470 Logistics risk events in the dataset.
```

## Turn 2

### Question

```text
Now, for the same risk dataset, what is the current status distribution?
```

I passed the messages from Turn 1 into Turn 2.

The run produced these tool calls:

```text
{
    "tool": "analyze_risk_events",
    "arguments": {
        "analysis_type": "category"
    }
}
```

and:

```text
{
    "tool": "analyze_risk_events",
    "arguments": {
        "analysis_type": "status"
    }
}
```

### Final Answer

```text
The current status distribution across the risk dataset is as follows:

Resolved: 2,974
Mitigated: 1,043
Investigating: 741
Open: 242
```

## Why this is useful

The second question says **"the same risk dataset"** instead of repeating all the information from the first question.

The previous messages are passed to the second invocation, so the agent can continue from the earlier conversation.

No changes were made to `tools.py` for this task.

---

# 13. Task 8 - Conditional Workflow

## What I had to demonstrate

Task 8 was separate from the main agent.

The requirement was to create a small workflow that:

1. accumulates state;
2. calculates something from that state;
3. checks a condition;
4. sends the input to one of two different routes.

I used:

```python
RunnablePassthrough.assign
```

and:

```python
RunnableBranch
```

## Step 1 - Add Risk Level

The workflow starts with the risk level.

For example:

```text
Critical
```

The first step keeps the risk level in the workflow state.

## Step 2 - Calculate Priority

The workflow then checks the risk level.

I used:

```text
High / Critical → URGENT
Other levels → NORMAL
```

So:

```text
Critical
   ↓
URGENT
```

and:

```text
Low
   ↓
NORMAL
```

---

# 14. Task 8 - Conditional Routes

I created two downstream routes.

## URGENT Route

The urgent route returns:

```text
URGENT ROUTE: Immediate attention required for Critical risk.
```

## NORMAL Route

The normal route returns:

```text
NORMAL ROUTE: Continue routine monitoring for Low risk.
```

---

# 15. Task 8 - Testing Both Routes

I ran the workflow twice.

### Run 1

Input:

```text
Critical
```

Output:

```text
URGENT ROUTE: Immediate attention required for Critical risk.
```

### Run 2

Input:

```text
Low
```

Output:

```text
NORMAL ROUTE: Continue routine monitoring for Low risk.
```

This shows that both branches of the workflow work.

---

# 16. Agent vs Workflow

One thing I wanted to show in this project is the difference between an agent and a workflow.

### Agent

The LLM decides which tool is needed.

```text
User Question
      ↓
LLM Decision
      ↓
Selected Tool
```

### Workflow

The condition is defined by the developer.

```text
Risk Level
      ↓
Priority
      ↓
Condition
      ↓
URGENT / NORMAL
```

So the agent is more dynamic, while the workflow follows the condition that I defined.

---

# 17. Demonstration Summary

| Task | Input | Tool / Method | Result |
|---|---|---|---|
| Task 6 | Which risk category has the most events? | `analyze_risk_events(category)` | Logistics - 1,470 |
| Task 7 Turn 1 | How many Logistics risk events are there? | `analyze_risk_events(category)` | 1,470 |
| Task 7 Turn 2 | What is the current status distribution? | `analyze_risk_events(status)` | Resolved 2,974; Mitigated 1,043; Investigating 741; Open 242 |
| Weather | Current weather for a shipment | `get_weather` | Live weather result |
| Task 8 Run 1 | Critical | `RunnableBranch` | URGENT route |
| Task 8 Run 2 | Low | `RunnableBranch` | NORMAL route |

---

# 18. API Key

I did not put my Gemini API key inside the Python files or GitHub repository.

The code uses this environment variable:

```text
PART4_GOOGLE_API_KEY
```

For example, in PowerShell:

```powershell
$env:PART4_GOOGLE_API_KEY="YOUR_API_KEY"
```

The real API key should never be uploaded to GitHub.

---

# 19. Installation

The main packages used in this project are:

```bash
pip install langchain
pip install langchain-google-genai
pip install langchain-core
```

---

# 20. How to Run

From the `part_04` folder:

### Main agent

```bash
python agent.py
```

### Task 6

```bash
python task6.py
```

### Task 7

```bash
python task7.py
```

### Task 8

```bash
python task8_workflow.py
```

---

# 21. What I Learned From Part 4

Through this part of the project, I learned how an LLM can be connected to actual Python tools instead of only generating text.

The main things I worked with were:

- creating tools with `@tool`;
- connecting tools to Gemini;
- allowing the agent to select tools;
- checking the native tool-call output;
- passing conversation history between turns;
- creating a conditional workflow;
- using `RunnablePassthrough.assign`;
- using `RunnableBranch`;
- keeping API keys outside the repository.

The most important part for my project is that the agent can now use my supply-chain data and external weather information instead of only giving a general LLM answer.

---

# 22. Final Outcome

Part 4 converts my supply-chain analytics project into an Agentic AI system.

The final flow is:

```text
Supply-Chain Question
        ↓
Gemini + LangChain
        ↓
Agent decides what is needed
        ↓
Risk / Shipment / Weather Tool
        ↓
Actual Data or Live API
        ↓
Final Answer
```

This makes the project more practical because the user can ask questions in normal language while the agent handles the tool selection and analysis.
