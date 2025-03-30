# from agents.graph_builder import career_bot
# from state import CareerBotState

# # ✅ Start fresh conversation
# state = CareerBotState()

# print("💬 CareerBot is online! Type 'exit' to quit.\n")

# # while True:
# #     user_input = input("You: ")

# #     if user_input.strip().lower() in ["exit", "quit"]:
# #         print("👋 Goodbye!")
# #         break

# #     # Update state with new user input
# #     state["user_response"] = user_input

# #     try:
# #         # 🔁 Run through LangGraph
# #         state = career_bot.invoke(state)

# #         # 💬 Show assistant's latest reply
# #         reply = state.get("chat_history", [])[-1]["content"]
# #         print(f"🤖 CareerBot: {reply}\n")

# #     except Exception as e:
# #         print(f"❌ Error: {e}")
# #         break


# while True:
#     chat_history = []
#     user_input = input("You: ")
#     chat_history.append({'USER: ': user_input})
#     if user_input.strip().lower() in ["exit", "quit"]:
#         print("👋 Goodbye!")
#         break
#     if not user_input:
#         continue
#     # Update state with new user input *using the expected key*
#     state["query"] = user_input
#     user_input = ""

#     try:
#         state = career_bot.invoke(state)
#         # reply = state.get("chat_history", [])[-1]["content"]
#         print(state)
#         reply = state.get("chat_history", [])
#         chat_history.append({'BOT: ': reply})
#         print(f"🤖 CareerBot: {reply}\n")
#     except Exception as e:
#         # print(state)
#         print(f"❌ Error: {e}")
#         break


import asyncio
from agents.graph_builder import career_bot
from state import CareerBotState

# ✅ Start fresh conversation
state = CareerBotState()

async def chat(state):
    print("💬 CareerBot is online! Type 'exit' to quit.\n")

    while True:
        # Wait for user input asynchronously
        user_input = await asyncio.to_thread(input, "You: ")

        if user_input.strip().lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        if not user_input:
            continue

        # Update state with new user input *using the expected key*
        state["query"] = user_input

        try:
            # 🔁 Run through LangGraph (this may be async as well depending on your bot logic)
            state = await asyncio.to_thread(career_bot.invoke, state)
            
            # Show assistant's latest reply
            reply = state.get("chat_history", [])
            print(f"🤖 CareerBot: {reply[-1]['content']}\n")

        except Exception as e:
            print(f"❌ Error: {e}")
            break

# Run the asynchronous chat function
asyncio.run(chat(state))
