# Pydantic models for orchestrator requests/responses:

from pydantic import BaseModel

class OrchestratorRequest(BaseModel):
    user_input: str

class OrchestratorResponse(BaseModel):
    reply: str
