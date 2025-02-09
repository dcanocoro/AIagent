from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Import routers
from orchestrator.router import router as orchestrator_router
# from storage.router import router as storage_router

def create_app() -> FastAPI:
    app = FastAPI(title="AI Agent Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Your frontend's exact origin
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
        allow_headers=["*"],  # Allow all headers
    )

    # Register routers
    app.include_router(orchestrator_router, prefix="/orchestrator", tags=["orchestrator"])
    # app.include_router(storage_router, prefix="/storage", tags=["storage"])

    return app

app = create_app()
