from openai import OpenAI
from state import CareerBotState
from config import OPENAI_API_KEY
import json
import re

llm = OpenAI(api_key=OPENAI_API_KEY)

REQUIRED_FIELDS = ["current_role", "location", "years_experience", "current_salary"]
VALID_AGENTS = ["salary_agent", "planning_agent", "transition_agent", "upskill_agent", "simulator_agent"]

def interface(state: CareerBotState) -> CareerBotState:
    state.setdefault("chat_history", [])
    state.setdefault("user_data", {})
    state.setdefault("missing_fields", [])
    state.setdefault("agent_queue", [])
    state.setdefault("result", {})

    user_input = state.get("user_response") or state.get("query")
    if not user_input:
        state["result"] = {"error": "No input provided"}
        state["next"] = "done"
        return state

    # Log user input
    state["chat_history"].append({"role": "user", "content": user_input})

    # Build prompt
    system_prompt = """
You are the main assistant for a career advice chatbot. Your job is to:
1. Carry on a friendly, natural conversation.
2. Extract the following fields from the user's message if they exist:
   - current_role
   - location
   - years_experience (as an integer)
   - current_salary (as an integer)
3. Ask about missing fields conversationally (e.g., "Thanks! May I know where you're based?")
4. Once all required fields are collected, return which agent(s) to call based on the user's intent:
   - salary_agent
   - planning_agent
   - transition_agent
   - upskill_agent
   - simulator_agent

You must respond in valid JSON **only** like this:
{
  "assistant_message": "...your friendly reply to the user...",
  "updated_user_data": { ... },         // Only fields found in this input
  "missing_fields": [ ... ],            // Only if still missing
  "agent_queue": [ ... ]                // Only when ready to proceed
}
"""

    # Prepare the message history
    messages = [{"role": "system", "content": system_prompt}]
    for turn in state["chat_history"][-6:]:  # limit to last few turns
        messages.append({"role": turn["role"], "content": turn["content"]})

    # Call LLM
    response = llm.chat.completions.create(
        model="gpt-4",
        temperature=0.3,
        messages=messages
    )

    raw = response.choices[0].message.content.strip()
    json_str = re.sub(r"```json|```", "", raw).strip()

    try:
        parsed = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        print("Raw LLM output:", parsed)
        state["result"] = {"error": "LLM output not parseable"}
        state["next"] = "done"
        return state

    # Update state with LLM output
    reply = parsed.get("assistant_message", "Okay.")
    updated_data = parsed.get("updated_user_data", {})
    state["user_data"].update(updated_data)
    state["missing_fields"] = parsed.get("missing_fields", [])
    state["agent_queue"] = parsed.get("agent_queue", [])

    # Add assistant reply to chat history
    state["chat_history"].append({"role": "assistant", "content": reply})

    # Route or keep chatting
    if state["agent_queue"]:
        state["next"] = state["agent_queue"].pop(0)
    else:
        state["next"] = "interface"  # stay in chat

    return state
