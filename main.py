from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from graph_flow import get_career_response, handle_career_simulation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (set specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

class QueryRequest(BaseModel):
    question: str

class ChatRequest(BaseModel):
    messages: list  # List of chat messages with role and content fields

class SimulationRequest(BaseModel):
    profile: dict  # User career profile

@app.post("/career-query/")
async def career_query(request: QueryRequest):
    """API endpoint to process career queries without tracking sessions."""
    response = await get_career_response(request.question, chat_history=[])

    if "Error" in response:
        raise HTTPException(status_code=500, detail=response)

    return {"response": response}

@app.post("/career-chat/")
async def career_chat(request: ChatRequest):
    """API endpoint to process career chat with history."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
        
    # Extract the last user message
    user_messages = [msg for msg in request.messages if msg.get("role") == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user messages found")
        
    latest_user_message = user_messages[-1].get("content", "")
    
    # Process with chat history
    response = await get_career_response(latest_user_message, chat_history=request.messages[:-1])

    if "Error" in response:
        raise HTTPException(status_code=500, detail=response)

    return {"response": response}

@app.post("/career-simulation/")
async def career_simulation(request: SimulationRequest):
    """API endpoint to run the career simulator with user profile data."""
    try:
        result = await handle_career_simulation(request.profile)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
