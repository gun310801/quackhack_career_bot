# from openai import OpenAI
# from state import CareerBotState
# from config import OPENAI_API_KEY
# import json
# import re

# llm = OpenAI(api_key=OPENAI_API_KEY)

# REQUIRED_FIELDS = ["current_role", "location", "years_experience", "current_salary"]
# VALID_AGENTS = ["salary_agent", "planning_agent", "transition_agent", "upskill_agent", "simulator_agent"]

# def interface(state: CareerBotState) -> CareerBotState:
#     state.setdefault("chat_history", [])
#     state.setdefault("user_data", {})
#     state.setdefault("missing_fields", [])
#     state.setdefault("agent_queue", [])
#     state.setdefault("result", {})

#     user_input = state.get("user_response") or state.get("query")
#     if not user_input:
#         state["result"] = {"error": "No input provided"}
#         state["next"] = "done"
#         return state

#     # Log user input
#     state["chat_history"].append({"role": "user", "content": user_input})

#     # Build prompt
#     system_prompt = """
# You are the main assistant for a career advice chatbot. Your job is to:
# 1. Carry on a friendly, natural conversation.
# 2. Extract the following fields from the user's message if they exist:
#    - current_role
#    - location
#    - years_experience (as an integer)
#    - current_salary (as an integer)
# 3. Ask about missing fields conversationally (e.g., "Thanks! May I know where you're based?")
# 4. Once all required fields are collected, return which agent(s) to call based on the user's intent:
#    - salary_agent
#    - planning_agent
#    - transition_agent
#    - upskill_agent
#    - simulator_agent

# You must respond in valid JSON **only** like this:
# {
#   "assistant_message": "...your friendly reply to the user...",
#   "updated_user_data": { ... },         // Only fields found in this input
#   "missing_fields": [ ... ],            // Only if still missing
#   "agent_queue": [ ... ]                // Only when ready to proceed
# }
# """

#     # Prepare the message history
#     messages = [{"role": "system", "content": system_prompt}]
#     for turn in state["chat_history"][-6:]:  # limit to last few turns
#         messages.append({"role": turn["role"], "content": turn["content"]})

#     # Call LLM
#     response = llm.chat.completions.create(
#         model="gpt-4",
#         temperature=0.3,
#         messages=messages
#     )

#     raw = response.choices[0].message.content.strip()
#     json_str = re.sub(r"```json|```", "", raw).strip()

#     try:
#         parsed = json.loads(json_str)
#     except Exception as e:
#         print("❌ Failed to parse JSON:", e)
#         print("Raw LLM output:", parsed)
#         state["result"] = {"error": "LLM output not parseable"}
#         state["next"] = "done"
#         return state

#     # Update state with LLM output
#     reply = parsed.get("assistant_message", "Okay.")
#     updated_data = parsed.get("updated_user_data", {})
#     state["user_data"].update(updated_data)
#     state["missing_fields"] = parsed.get("missing_fields", [])
#     state["agent_queue"] = parsed.get("agent_queue", [])

#     # Add assistant reply to chat history
#     state["chat_history"].append({"role": "assistant", "content": reply})

#     # Route or keep chatting
#     if state["agent_queue"]:
#         state["next"] = state["agent_queue"].pop(0)
#     else:
#         state["next"] = "interface"  # stay in chat

#     return state

from openai import OpenAI
from state import CareerBotState
from config import OPENAI_API_KEY
import json
import re

# 🔐 Set up OpenAI client
llm = OpenAI(api_key=OPENAI_API_KEY)

# 📋 Required fields for each downstream agent
AGENT_REQUIRED_FIELDS = {
    "salary_agent": ["current_role", "location", "current_salary", "years_experience"],
    "transition_agent": ["current_role", "target_role", "education_level"],
    "planning_agent": ["current_role", "goal", "timeline_months"],
}

# 🧠 Interface agent node — this runs on each user message
def interface(state: CareerBotState) -> CareerBotState:
    # Initialize defaults
    state.setdefault("chat_history", [])
    state.setdefault("user_data", {})
    state.setdefault("missing_fields", [])
    state.setdefault("agent_queue", [])
    state.setdefault("result", {})

    # Grab user input
    user_input = state.get("user_response") or state.get("query")
    if not user_input:
        state["result"] = {"error": "No input provided"}
        state["next"] = "done"
        return state

    # Add user message to chat history
    state["chat_history"].append({"role": "user", "content": user_input})

    # LLM system prompt
    system_prompt = """
You are the main assistant for a career advice chatbot. Your job is to:
1. Carry on a friendly, natural conversation.
2. Extract the following fields from the user's message if they exist:
   - current_role
   - location
   - years_experience (as an integer)
   - current_salary (as an integer)
   - target_role
   - education_level
   - goal
   - timeline_months
3. Ask about missing fields conversationally.
4. Once enough info is collected, return which agent(s) to call:
   - salary_agent
   - planning_agent
   - transition_agent
   - upskill_agent
   - simulator_agent

You must respond in valid JSON ONLY like this:
```json
{
  "assistant_message": "Your friendly reply to the user",
  "updated_user_data": {
    "current_role": "AI Engineer",
    "location": "NYC"
  },
  "missing_fields": ["current_salary", "years_experience"],
  "agent_queue": ["salary_agent"]
}
"""
        # Add system + conversation history
    messages = [{"role": "system", "content": system_prompt}]
    for turn in state["chat_history"][-6:]:  # Limit context for cost/speed
        messages.append({"role": turn["role"], "content": turn["content"]})

    # Send to LLM
    response = llm.chat.completions.create(
        model="gpt-4",
        temperature=0.3,
        messages=messages
    )

    # Parse response
    raw_output = response.choices[0].message.content.strip()
    json_str = re.sub(r"```json|```", "", raw_output).strip()

    try:
        parsed = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        print("Raw LLM output:", raw_output)
        state["result"] = {"error": "LLM output not parseable"}
        state["next"] = "done"
        return state

    # Update state with parsed data
    reply = parsed.get("assistant_message", "Okay.")
    updated_data = parsed.get("updated_user_data", {})
    agent_queue = parsed.get("agent_queue", [])

    state["user_data"].update(updated_data)
    state["chat_history"].append({"role": "assistant", "content": reply})
    state["agent_queue"] = agent_queue

    # Check if we need more info for next agent
    if agent_queue:
        next_agent = agent_queue[0]
        required_fields = AGENT_REQUIRED_FIELDS.get(next_agent, [])
        missing = [f for f in required_fields if f not in state["user_data"]]

        if missing:
            # Ask for missing info
            state["missing_fields"] = missing
            prompt = f"To help with {next_agent}, could you tell me your {missing[0]}?"
            state["chat_history"].append({"role": "assistant", "content": prompt})
            state["next"] = "interface"
            return state

        # All good — route to agent
        state["next"] = agent_queue.pop(0)
        return state

    # No routing yet — stay in convo
    state["next"] = "interface"
    return state
