# test_interface_llm.py

from agents.Manager_agent import interface
from state import CareerBotState

# Initial empty state
state: CareerBotState = {
    "query": "",
    "user_data": {},
    "chat_history": [],
    "agent_queue": [],
    "missing_fields": [],
    "user_response": None,
    "result": {},
    "next": None
}

print("💬 CareerBot LLM Test (type 'exit' to quit)")
first_turn = True

while True:
    if first_turn:
        user_input = input("You: ")
        if user_input.lower() == "exit": break
        state["query"] = user_input
        first_turn = False
    else:
        user_input = input("You: ")
        if user_input.lower() == "exit": break
        state["user_response"] = user_input

    state = interface(state)

    # Show assistant response (last in chat history)
    if "chat_history" in state and state["chat_history"]:
        response = state["chat_history"][-1]["content"]
        print(f"\n🤖 CareerBot: {response}")

    # Exit if we're ready to call another agent
    if state.get("next") and state["next"] != "interface":
        print(f"\n✅ Routing to: {state['next']}")
        break
