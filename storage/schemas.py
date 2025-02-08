# storage/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    # Add other user fields here

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    #hashed_password: str  # Usually, you don't expose hashed passwords

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy models

class ConversationBase(BaseModel):
    pass #We could add extra fields here, like name

class ConversationCreate(ConversationBase):
    pass #We could add extra fields here

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CheckpointBase(BaseModel):
    data: Dict  # Checkpoint data is a dictionary

class CheckpointCreate(CheckpointBase):
    pass

class Checkpoint(CheckpointBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        orm_mode = True