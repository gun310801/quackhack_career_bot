# state.py
from typing import TypedDict, List, Optional, Dict, Any

class CareerBotState(TypedDict):
    query: str
    user_data: Dict[str, Any]           # e.g., role, location, current_salary
    chat_history: List[Dict[str, str]]  # running list of turns
    agent_queue: List[str]              # agents to call
    missing_fields: List[str]           # missing values
    user_response: Optional[str]        # latest reply from user
    result: Dict[str, Any]
    next: Optional[str]
