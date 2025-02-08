# storage/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Settings  # Assuming you have a config file
import os #Import to take the data from env

# Use environment variables for database connection
#DB_USER = os.environ.get("POSTGRES_USER", "postgres")
#DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "Mobydick&15")
#DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")  # Or the Docker service name
#DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
#DB_NAME = os.environ.get("POSTGRES_DB", "Finace_agent")

#DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL = os.environ.get("DATABASE_URL")

#Added echo true for debugging
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()