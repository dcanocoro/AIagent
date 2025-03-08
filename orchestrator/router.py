from fastapi import APIRouter
from .chatbot_simple import handle_interview
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session
from storage import models
from fastapi import HTTPException
from storage.router import get_db
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class InterviewRequest(BaseModel): # needs to be moved to schemas.py
    question: str
    conversation_id: int

router = APIRouter()

@router.post("/interview", response_model=list[str])
def run_interview_flow(payload: InterviewRequest, db: Session = Depends(get_db)):
    """
    Endpoint that accepts a user question and conversation_id, retrieves thread_id,
    and returns the LLM response.
    """
    # Fetch the conversation to get the correct thread_id
    logger.info("🔵 Endpoint was hit!")
    logger.info(f"Payload received: {payload.dict()}")

    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == payload.conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    thread_id = {"configurable": {"thread_id": conversation.thread_id}}
    # Extract thread_id

    logger.info(f"Transformed thread_id: {thread_id}")

    # Call handle_interview with thread_id
    response = handle_interview(payload.question, thread=thread_id)
    return response  # Return response as a string