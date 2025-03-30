# state.py
from typing import TypedDict, List,Literal, Optional, Dict, Any

class UserData(TypedDict, total=False):
    current_role: str
    location: str
    current_salary: int
    years_experience: int


class ChatTurn(TypedDict):
    role: Literal["user", "assistant"]
    content: str

class CareerBotState(TypedDict):
    query: str
    user_data: Dict[str, Any]           # e.g., role, location, current_salary
    chat_history: List[Dict[str, str]]  # running list of turns
    agent_queue: List[str]              # agents to call
    missing_fields: List[str]           # missing values
    user_response: Optional[str]        # latest reply from user
    result: Dict[str, Any]
    next: Optional[str]
