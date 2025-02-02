from fastapi import FastAPI
from config import Settings
from dotenv import load_dotenv

load_dotenv()

# Import routers
from orchestrator.router import router as orchestrator_router
#from storage.router import router as storage_router

# For database init on startup
# storage.database import engine
# from storage.models import Base

def create_app() -> FastAPI:
    app = FastAPI(title="AI Agent Backend")

    # Initialize DB tables (for minimal demo; in production use migrations)
    # Base.metadata.create_all(bind=engine)

    # Register routers
    app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])
    # app.include_router(storage_router, prefix="/storage", tags=["storage"])


    return app

app = create_app()
