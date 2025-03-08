# storage/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import uuid
from .database import SessionLocal
from . import models, schemas, router, utils


router = APIRouter()

def get_db():  # probably needs to be moved to database.py
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------
# User Endpoints
# -----------------------
@router.post("/users", response_model=schemas.UserOut)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_pw = utils.get_password_hash(user_in.password)
    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ----------------------------
# Conversation Endpoints
# ----------------------------

@router.post("/conversations", response_model=schemas.ConversationOut)
def create_conversation(
    conversation_in: schemas.ConversationCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Validate the user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a unique thread_id
    thread_id = str(uuid.uuid4())  # Creates a UUID string

    # Create and save the conversation with the generated thread_id
    conversation = models.Conversation(
        user_id=user.id,
        title=conversation_in.title,
        thread_id=thread_id  # Assign the generated thread ID
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    # Query the database for the conversation
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    
    # If conversation is not found, return a 404 error
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conv  # FastAPI will automatically convert this to the response model


@router.get("/users/{user_id}/conversations", response_model=List[schemas.ConversationOut])
def list_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """
    Fetches all conversations for a specific user.
    """
    # Query conversations for the given user_id
    conversations = db.query(models.Conversation).filter(models.Conversation.user_id == user_id).all()

    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found for this user")

    return conversations


# -------------------------
# Message Endpoints
# -------------------------
@router.post("/conversations/{conversation_id}/messages", response_model=schemas.MessageOut)
def add_message(
    conversation_id: int,
    message_in: schemas.MessageCreate,
    db: Session = Depends(get_db)
):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    new_message = models.Message(
        conversation_id=conversation.id,
        sender=message_in.sender,
        content=message_in.content
    )
    db.add(new_message)
    # Update the conversation updated_at
    conversation.updated_at = new_message.timestamp
    db.commit()
    db.refresh(new_message)
    return new_message

@router.get("/conversations/{conversation_id}/messages", response_model=list[schemas.MessageOut])
def get_messages_for_conversation(conversation_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.timestamp.asc()).all()
    return messages
