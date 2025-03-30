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
import os
import sys

# Add the demo directory to the Python path to import the agent
sys.path.append(os.path.join(os.path.dirname(__file__), "demo"))
from agents.career_simulator.career_simulator_agent import CareerSimulatorAgent

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

# Initialize CareerSimulatorAgent once to reuse
def get_career_simulator_agent():
    """Initialize and return the career simulator agent with the correct data files."""
    # Get the absolute path to the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Try both possible locations for the data file
    possible_paths = [
        os.path.join(project_root, "demo/agents/career_simulator/data/Level_compensation_by_company.csv"),
        os.path.join(project_root, "data/Level_compensation_by_company.csv")
    ]
    
    # Find which path exists
    salary_data_path = None
    for path in possible_paths:
        if os.path.exists(path):
            salary_data_path = path
            break
    
    if not salary_data_path:
        raise FileNotFoundError("Could not find required salary compensation data files")
    
    # Initialize agent
    return CareerSimulatorAgent(salary_data_dir=salary_data_path, use_llm=True)

# Global instance of the agent that can be reused
try:
    career_agent = get_career_simulator_agent()
except Exception as e:
    print(f"⚠️ Warning: Could not initialize career simulator agent: {e}")
    career_agent = None

async def run_career_simulation(user_profile):
    """
    Run the career simulator with the provided user profile.
    
    Args:
        user_profile (dict): User profile data with fields like:
            - current_role: Current job role
            - target_role: Target job role
            - current_level: Experience level (Entry, Mid, Senior)
            - years_experience: Years of experience
            - current_skills: List of skills
            - location: Geographic location
            - current_salary: Current salary
            - current_company: Current employer
            - target_companies: List of target companies
    
    Returns:
        dict: Career simulation results
    """
    if career_agent is None:
        return {"error": "Career simulator agent not initialized"}
    
    # Ensure minimum required fields are present
    if not user_profile.get("current_role") or not user_profile.get("target_role"):
        return {"error": "Missing required fields: current_role and target_role"}
    
    # Set default values for missing fields
    defaults = {
        "current_level": "Entry",
        "years_experience": 0,
        "current_skills": [],
        "location": "Unknown",
        "current_salary": 0,
        "current_company": None,
        "target_companies": [],
        "n_steps": 48,
        "n_simulations": 1000
    }
    
    # Apply defaults for missing fields
    for key, value in defaults.items():
        if key not in user_profile:
            user_profile[key] = value
            
    try:
        # Run the simulation (this can take some time)
        result = career_agent.process(user_profile)
        return result
    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"}

async def extract_career_data(chat_history):
    """
    Extract career-related information from chat history using LLM.
    
    Args:
        chat_history (list): List of chat message dictionaries
    
    Returns:
        dict: Extracted career data
    """
    if not chat_history:
        return {}
    
    extract_prompt = """
    Based on the conversation, extract the following career information about the user.
    Return the information in a valid JSON format with these fields:
    {
        "current_role": str or null,
        "target_role": str or null,
        "current_level": str or null, 
        "years_experience": int or null,
        "current_skills": list of str or empty list,
        "location": str or null,
        "current_salary": int or null,
        "current_company": str or null,
        "target_companies": list of str or empty list,
        "goals": str or null,
        "timeline": str or null
    }
    
    Only include fields where you have information. Use null for unknown values.
    """
    
    messages = [
        {"role": "system", "content": extract_prompt}
    ]
    
    # Add conversation history
    for message in chat_history:
        messages.append({"role": message["role"], "content": message["content"]})
    
    try:
        response = await llm.ainvoke(messages)
        extracted_text = response.content
        
        # Extract JSON from response text
        try:
            # Find JSON content (it might be enclosed in ```json and ```)
            if "```json" in extracted_text:
                json_start = extracted_text.find("```json") + 7
                json_end = extracted_text.find("```", json_start)
                extracted_text = extracted_text[json_start:json_end].strip()
            elif "```" in extracted_text:
                json_start = extracted_text.find("```") + 3
                json_end = extracted_text.find("```", json_start)
                extracted_text = extracted_text[json_start:json_end].strip()
                
            return json.loads(extracted_text)
        except json.JSONDecodeError:
            # If not valid JSON, return empty dict
            return {}
    except Exception as e:
        print(f"Error extracting career data: {e}")
        return {}

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

async def run_career_simulation_from_chat(chat_history):
    """
    Extract career info from chat and run a simulation.
    
    Args:
        chat_history (list): Chat history
        
    Returns:
        dict: Simulation results or error
    """
    # Extract career data from conversation
    user_profile = await extract_career_data(chat_history)
    
    # Check if we have enough information to run a simulation
    if not user_profile.get("current_role") or not user_profile.get("target_role"):
        return {
            "error": "Not enough information to run a career simulation. Please provide at least your current role and target role."
        }
    
    # Run simulation
    return await run_career_simulation(user_profile)

# API endpoint function for frontend integration
async def handle_career_simulation(user_profile_data):
    """
    Handle a career simulation request from the frontend.
    
    Args:
        user_profile_data (dict): User profile data
        
    Returns:
        dict: Simulation results
    """
    try:
        # Validate and parse input data
        if isinstance(user_profile_data, str):
            try:
                user_profile = json.loads(user_profile_data)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON data"}
        else:
            user_profile = user_profile_data
            
        # Run simulation
        result = await run_career_simulation(user_profile)
        return result
    except Exception as e:
        return {"error": f"Error processing request: {str(e)}"}
