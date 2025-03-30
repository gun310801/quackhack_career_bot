from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from agents.manager_agent import interface  # 🧠 Interface agent function
from agents.salary_agent import salary_node  # 🛠 ToolNode for salary
from state import CareerBotState  # 🗂️ Shared state definition

# 🔧 Build the LangGraph
graph = StateGraph(CareerBotState)

# 🧩 Add nodes
graph.add_node("interface", interface)
graph.add_node("salary_agent", salary_node)

# 🚪 Set entry point
graph.set_entry_point("interface")
graph.add_edge("interface", END)
# 🔀 Smart conditional routing from interface to agent
graph.add_conditional_edges(
    "interface",
    tools_condition,
    {
        "salary": "salary_agent"
    }
)

# 🔁 Go back to interface if salary agent needs more input
graph.add_edge("salary_agent", "interface")

# ✅ End condition
graph.add_edge("interface", END)

# 🧠 Compile the graph
career_bot = graph.compile()