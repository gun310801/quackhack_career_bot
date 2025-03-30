from dotenv import load_dotenv
import os
from typing import Dict, TypedDict, List, Annotated, Sequence
import operator
from langgraph.graph import Graph, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPEN_AI_API_KEY")
)

# Define the state type
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    current_step: str
    job_data: Dict
    salary_data: Dict
    user_profile: Dict
    simulation_results: Dict

@dataclass
class UserProfile:
    current_job: str
    current_salary: float
    location: str
    years_experience: int
    skills: List[str]
    target_job: Optional[str] = None
    target_location: Optional[str] = None

# Tool 1: Chatbot Server
@tool
def chat_interface(user_input: str, state: AgentState) -> Dict:
    """
    Main chatbot interface that handles user interactions and coordinates with other agents.
    """
    # Process user input
    messages = state["messages"]
    messages.append(HumanMessage(content=user_input))
    
    # Generate response using LLM
    response = llm.invoke(messages)
    messages.append(response)
    
    # Extract relevant information for user profile
    # This is a simplified version - in practice, you'd want to implement proper information extraction
    user_info = {
        "query_type": "identify_intent",
        "extracted_info": response.content
    }
    
    return {
        "messages": messages,
        "user_info": user_info
    }

# Tool 2: Salary Analysis
@tool
def salary_analyzer(
    job_title: str,
    location: str,
    experience: int = 0
) -> Dict:
    """
    Performs comparative salary analysis using multiple data sources.
    """
    # Load data
    job_df = pd.read_csv('job_postings.csv')
    salary_df = pd.read_csv('salary_trends.csv')
    
    # Perform analysis
    current_market_data = {
        "median_salary": 0,  # Replace with actual calculation
        "salary_range": (0, 0),  # Replace with actual calculation
        "market_demand": "high",  # Replace with actual calculation
        "growth_trend": 0.0  # Replace with actual calculation
    }
    
    comparative_analysis = {
        "industry_percentile": 0,  # Replace with actual calculation
        "location_adjustment": 0,  # Replace with actual calculation
        "experience_impact": 0  # Replace with actual calculation
    }
    
    return {
        "market_data": current_market_data,
        "comparative_analysis": comparative_analysis
    }

# Tool 3: Career Transition Simulator
@tool
def career_simulator(
    current_profile: UserProfile,
    target_job: str,
    target_location: str
) -> Dict:
    """
    Simulates career transition scenarios using Markov models and market data.
    """
    # Load data
    job_df = pd.read_csv('job_postings.csv')
    salary_df = pd.read_csv('salary_trends.csv')
    
    # Create transition probability matrix
    def create_transition_matrix(data):
        # Placeholder for transition matrix creation
        return np.array([[0.7, 0.3], [0.4, 0.6]])
    
    # Calculate transition probabilities
    transition_matrix = create_transition_matrix(job_df)
    
    # Run simulation
    num_simulations = 1000
    success_probability = 0.0  # Replace with actual calculation
    expected_timeline = 0  # Replace with actual calculation
    risk_factors = []  # Replace with actual calculation
    
    # Market condition analysis
    market_conditions = {
        "market_health": 0.0,
        "competition_level": "medium",
        "growth_potential": 0.0
    }
    
    return {
        "success_probability": success_probability,
        "expected_timeline": expected_timeline,
        "risk_factors": risk_factors,
        "market_conditions": market_conditions
    }

# Define agent nodes with updated logic
def chatbot_agent(state: AgentState) -> AgentState:
    """Handles user interactions and coordinates with other agents."""
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    if last_message:
        chat_result = chat_interface(last_message.content, state)
        state["messages"] = chat_result["messages"]
        state["current_step"] = "salary_analyst" if "salary" in last_message.content.lower() else "simulator"
    
    return state

def salary_analyst_agent(state: AgentState) -> AgentState:
    """Processes salary analysis requests."""
    user_profile = state.get("user_profile", {})
    if user_profile:
        analysis = salary_analyzer(
            user_profile.get("current_job", ""),
            user_profile.get("location", ""),
            user_profile.get("years_experience", 0)
        )
        state["salary_data"] = analysis
    
    return state

def simulator_agent(state: AgentState) -> AgentState:
    """Runs career transition simulations."""
    user_profile = state.get("user_profile", {})
    if user_profile:
        profile = UserProfile(
            current_job=user_profile.get("current_job", ""),
            current_salary=user_profile.get("current_salary", 0),
            location=user_profile.get("location", ""),
            years_experience=user_profile.get("years_experience", 0),
            skills=user_profile.get("skills", []),
            target_job=user_profile.get("target_job"),
            target_location=user_profile.get("target_location")
        )
        
        simulation = career_simulator(
            profile,
            profile.target_job or "",
            profile.target_location or ""
        )
        state["simulation_results"] = simulation
    
    return state

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("chatbot", chatbot_agent)
workflow.add_node("salary_analyst", salary_analyst_agent)
workflow.add_node("simulator", simulator_agent)

# Add edges
workflow.add_edge("chatbot", "salary_analyst")
workflow.add_edge("chatbot", "simulator")
workflow.add_edge("salary_analyst", "chatbot")
workflow.add_edge("simulator", "chatbot")

# Set entry point
workflow.set_entry_point("chatbot")

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    # Initialize state
    initial_state = {
        "messages": [],
        "current_step": "chatbot",
        "job_data": {},
        "salary_data": {},
        "user_profile": {},
        "simulation_results": {}
    }
    
    # Example usage
    result = app.invoke(initial_state)
    print(result) 