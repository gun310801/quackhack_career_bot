from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agents.manager_agent import interface  # 🧠 Your interface agent
from agents.salary_agent import salary_node  # 🛠 Salary ToolNode
from state import CareerBotState  # 🗂️ Shared state object

# Create the LangGraph
graph = StateGraph(CareerBotState)

# Add nodes
graph.add_node("interface", interface)           # interface = normal def function
graph.add_node("salary_agent", salary_node)      # salary_agent = ToolNode

# Define edges
graph.set_entry_point("interface")
graph.add_edge("interface", "interface")   
graph.add_edge("interface", END)          
graph.add_edge("interface", "salary_agent")
graph.add_edge("salary_agent", "interface")  # Return if missing_fields present

  # If next = done

# Compile the graph
career_bot = graph.compile()
