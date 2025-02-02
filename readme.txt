# 1. Overall Architecture

## Microservice-Like Structure in a Single Application

Even though we’re implementing everything within one FastAPI application (for simplicity and ease of local deployment), we’ve separated the code into different modules (or folders) that represent distinct “microservices.” These modules are:

- **Orchestrator**: Handles the overall conversation and workflow logic.
- **Storage**: Manages data persistence (e.g., user data) using a database.
- **LLM Connector**: Interfaces with a large language model (or a simulated version for our demo).

Each module has its own router (set of endpoints) and specific functionality, which helps with separation of concerns, scalability, and ease of testing.

---

# 2. Main Application Entry Point (`main.py`)

## Creating the FastAPI App

The `create_app()` function instantiates the FastAPI application. It also loads configuration settings from our `Settings` class (described later) and sets up the application.

## Router Registration

The app includes routers from the **orchestrator, storage, and LLM connector** modules. This is done by mounting each router under a distinct URL prefix (`/orchestrator`, `/storage`, `/llm`), which makes it clear which endpoints belong to which service.

## Database Initialization

For our minimal demo, we automatically create all database tables at startup by calling:

Base.metadata.create_all(bind=engine)

# 3. Configuration Management (config.py):

Settings via Pydantic’s BaseSettings
The Settings class is used to load configuration variables (like database credentials and API keys) from environment variables or a .env file. This centralizes configuration so that no credentials or “magic numbers” are hard-coded into the rest of the code.

Benefits:
Makes the application more secure and easier to configure for different environments (local development, production, etc.).

# 4. Storage Microservice
This module is responsible for interacting with the database and managing data persistence:

- **Database Connection (storage/database.py)**:

SQLAlchemy Engine & Session
A database URL is constructed from the settings, and an SQLAlchemy engine is created.
A session factory (SessionLocal) is defined so that each incoming request gets its own database session via the get_db dependency function.
Dependency Injection
FastAPI’s dependency injection mechanism uses get_db to ensure that every endpoint interacting with the database has a properly managed session.

-  **Data Models (storage/models.py)**:

User Model
We define a simple User model (using SQLAlchemy’s declarative_base) with fields such as:

    id
    username
    email
    This model represents a table in our PostgreSQL database.

**Pydantic Schemas (storage/schemas.py)**:

Data Validation & Serialization

The UserCreate schema is used to validate incoming data (e.g., from a POST request).
The UserRead schema is used for responses.
The orm_mode = True setting in Pydantic allows SQLAlchemy objects to be returned directly.

- **CRUD Operations (storage/crud.py)**:

Abstracting Database Logic. This module contains helper functions, such as:

    create_user
    get_user
    These functions encapsulate the logic for interacting with the database, keeping the routers clean and focused on HTTP request/response handling.

- **API Router (storage/router.py)**: 
Endpoints for CRUD Operations. Two endpoints are provided:

    POST /storage/users → Create a new user.
    GET /storage/users/{user_id} → Retrieve user information.
    Error Handling
    If a user already exists or if the user isn’t found, the appropriate HTTP exceptions are raised.