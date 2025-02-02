from fastapi import APIRouter
from .schemas import OrchestratorRequest, OrchestratorResponse
from .chatbot_simple import handle_interview
from pydantic import BaseModel


class InterviewRequest(BaseModel):
    question: str

class InterviewResponse(BaseModel):
    answers: list[str]

router = APIRouter()

@router.post("/interview", response_model=InterviewResponse)
def run_interview_flow(payload: InterviewRequest):
    """
    Endpoint that accepts a user question and returns a list of messages
    from the orchestrated interview flow.
    """
    answers = handle_interview(payload.question)
    return InterviewResponse(answers=answers)
