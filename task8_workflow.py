from langchain_core.runnables import RunnablePassthrough, RunnableBranch

print("Task 8 workflow file is running")

# Step 1: Add risk level to the workflow state
initial_state = RunnablePassthrough.assign(
    risk_level=lambda x: x["risk_level"]
)

# Step 2: Add priority based on the risk level
workflow_state = initial_state.assign(
    priority=lambda x: (
        "URGENT"
        if x["risk_level"] in ["High", "Critical"]
        else "NORMAL"
    )
)

# Test the accumulated state
result = workflow_state.invoke({"risk_level": "Critical"})

print("\n--- ACCUMULATED STATE ---")
print(result)

# Step 3: Define the two possible downstream routes

urgent_chain = (lambda x: f"URGENT ROUTE: Immediate attention required for {x['risk_level']} risk.")

normal_chain = (lambda x: f"NORMAL ROUTE: Continue routine monitoring for {x['risk_level']} risk.")


# Step 4: Route based on the accumulated priority state
conditional_workflow = workflow_state | RunnableBranch(
    (
        lambda x: x["priority"] == "URGENT",
        urgent_chain
    ),
    normal_chain
)

# Step 5: Run the conditional workflow twice
# Run 1: Critical risk → URGENT route

print("\n--- WORKFLOW RUN 1 ---")

result1 = conditional_workflow.invoke({"risk_level": "Critical"})

print(result1)


# Run 2: Low risk → NORMAL route

print("\n--- WORKFLOW RUN 2 ---")

result2 = conditional_workflow.invoke({"risk_level": "Low"})

print(result2)