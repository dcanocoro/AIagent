from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from storage.database import Base, engine


load_dotenv()

# Import routers
from orchestrator.router import router as orchestrator_router
from storage.router import router as storage_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Agent Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (for testing; restrict in production)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
        allow_headers=["*"],  # Allow all headers
)
    #CREATE TABLES IN THE DATABASE
    Base.metadata.create_all(bind=engine)  # to be removed in production

    # Register routers
    app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])
    app.include_router(storage_router, prefix="/storage", tags=["storage"])


    return app

app = create_app()
