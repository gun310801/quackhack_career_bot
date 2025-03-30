from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from graph_flow import get_career_response
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

@app.post("/career-query/")
async def career_query(request: QueryRequest):
    """API endpoint to process career queries without tracking sessions."""
    response = await get_career_response(request.question, chat_history=[])

    if "Error" in response:
        raise HTTPException(status_code=500, detail=response)

    return {"response": response}
