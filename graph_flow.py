# import asyncio
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from state import CareerBotState
# import json
# from config import OPENAI_API_KEY

# # Create a simple chat interface without using langgraph
# async def chat():
#     # Create a fresh conversation state
#     state = CareerBotState()
#     state["chat_history"] = []
#     state["user_data"] = {}
    
#     print("💬 CareerBot is online! Type 'exit' to quit.\n")
    
#     # Set up OpenAI client
#     llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=OPENAI_API_KEY)
    
#     # Create a system prompt
#     system_prompt = """
#     You are a helpful career advisor bot. Your job is to:
    
#     1. Carry on a friendly, natural conversation.
#     2. Extract useful career information from user messages, such as:
#        - current_role
#        - location
#        - years_experience
#        - current_salary
#        - target_role
#        - education_level
#        - goals
#        - timeline
#     3. Provide helpful career advice based on the information provided.
    
#     Your responses should be conversational and helpful.
#     """
    
#     while True:
#         # Get user input
#         user_input = await asyncio.to_thread(input, "You: ")
        
#         if user_input.strip().lower() in ["exit", "quit"]:
#             print("👋 Goodbye!")
#             break
            
#         if not user_input:
#             continue
        
#         # Add user message to chat history
#         state["chat_history"].append({"role": "user", "content": user_input})
        
#         # Create message list for LLM
#         messages = [
#             {"role": "system", "content": system_prompt}
#         ]
        
#         # Add up to last 10 messages from chat history
#         for message in state["chat_history"][-10:]:
#             messages.append({"role": message["role"], "content": message["content"]})
        
#         # Get response from LLM
#         try:
#             response = await llm.ainvoke(messages)
            
#             # Add assistant response to chat history
#             assistant_message = response.content
#             state["chat_history"].append({"role": "assistant", "content": assistant_message})
            
#             # Print response
#             print(f"🤖 CareerBot: {assistant_message}\n")
            
#         except Exception as e:
#             print(f"❌ Error: {e}")
#             break

# # Run the asynchronous chat function
# asyncio.run(chat())
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import CareerBotState
import json
from config import OPENAI_API_KEY

# Set up OpenAI client
llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=OPENAI_API_KEY)

# Define system prompt
SYSTEM_PROMPT = """
You are a helpful career advisor bot. Your job is to:

1. Carry on a friendly, natural conversation.
2. Extract useful career information from user messages, such as:
   - current_role
   - location
   - years_experience
   - current_salary
   - target_role
   - education_level
   - goals
   - timeline
3. Provide helpful career advice based on the information provided.

Your responses should be conversational and helpful.
"""

async def get_career_response(user_input, chat_history):
    """Processes a user query and returns a response from the AI assistant."""
    if not user_input.strip():
        return "Please enter a valid question."

    # Append user message to chat history
    chat_history.append({"role": "user", "content": user_input})

    # Construct messages for LLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += chat_history[-10:]  # Keep last 10 messages for context

    # Get response from LLM
    try:
        response = await llm.ainvoke(messages)
        ai_message = response.content
        chat_history.append({"role": "assistant", "content": ai_message})
        return ai_message
    except Exception as e:
        return f"Error: {e}"
