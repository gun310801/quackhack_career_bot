from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from tools.salary_tools import (
    compare_to_market,
    get_salary_summary,
    get_company_salary_data,
    get_state_salary,
    compare_state_industries
)
from config import OPENAI_API_KEY

# 🔐 LLM setup
llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=OPENAI_API_KEY)

# 📦 LangGraph-compatible ToolNode (no initialize_agent anymore!)
salary_node = ToolNode(
    name="salary_agent",
    tools=[
        compare_to_market,
        get_salary_summary,
        get_company_salary_data,
        get_state_salary,
        compare_state_industries
    ]
)
