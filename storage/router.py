# storage/router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, models # models added, it was failing
from .database import get_db
from typing import List

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user=user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    return db_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
@router.get("/users/name/{username}", response_model=schemas.User)
def read_user_by_name(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/users/{user_id}/conversations/", response_model=schemas.Conversation)
def create_conversation_for_user(user_id: int, db: Session = Depends(get_db)):
    return crud.create_conversation(db=db, user_id=user_id)

@router.get("/conversations/{conversation_id}", response_model=schemas.Conversation)
def read_conversation(conversation_id: int, db: Session = Depends(get_db)):
    db_conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation

@router.get("/users/{user_id}/conversations/", response_model=List[schemas.Conversation])
def read_conversations_for_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_conversations_for_user(db=db, user_id=user_id, skip=skip, limit=limit)

@router.post("/conversations/{conversation_id}/checkpoints/", response_model=schemas.Checkpoint)
def create_checkpoint_for_conversation(conversation_id: int, checkpoint: schemas.CheckpointCreate, db: Session = Depends(get_db)):
    return crud.create_checkpoint(db=db, conversation_id=conversation_id, data=checkpoint.data)

@router.get("/conversations/{conversation_id}/checkpoints/latest", response_model=schemas.Checkpoint)
def read_latest_checkpoint(conversation_id: int, db: Session = Depends(get_db)):
    db_checkpoint = crud.get_latest_checkpoint(db, conversation_id=conversation_id)
    if db_checkpoint is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return db_checkpoint

@router.get("/conversations/{conversation_id}/checkpoints/", response_model=List[schemas.Checkpoint])
def read_checkpoints(conversation_id: int, db: Session = Depends(get_db)):
    db_checkpoint = crud.get_all_checkpoints(db, conversation_id=conversation_id)
    if db_checkpoint is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return db_checkpoint