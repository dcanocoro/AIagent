# storage/crud.py

from sqlalchemy.orm import Session
from . import models, schemas  # We'll define schemas in the next step
from sqlalchemy.exc import IntegrityError  # For handling unique constraint violations

def create_user(db: Session, user: schemas.UserCreate):
    # Placeholder for password hashing (replace with actual hashing)
    hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None # Or raise a custom exception


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_conversation(db: Session, user_id: int):
    db_conversation = models.Conversation(user_id=user_id)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def get_conversations_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Conversation).filter(models.Conversation.user_id == user_id).offset(skip).limit(limit).all()

def create_checkpoint(db: Session, conversation_id: int, data: dict):
    db_checkpoint = models.Checkpoint(conversation_id=conversation_id, data=data)
    db.add(db_checkpoint)
    db.commit()
    db.refresh(db_checkpoint)
    return db_checkpoint

def get_latest_checkpoint(db: Session, conversation_id: int):
    return db.query(models.Checkpoint).filter(models.Checkpoint.conversation_id == conversation_id).order_by(models.Checkpoint.created_at.desc()).first()

def get_all_checkpoints(db: Session, conversation_id: int):
     return db.query(models.Checkpoint).filter(models.Checkpoint.conversation_id == conversation_id).order_by(models.Checkpoint.created_at.desc()).all()