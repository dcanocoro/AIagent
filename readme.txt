# AI Agent Backend (Prototype)

This repository contains the backend prototype for an AI-powered agent designed for tasks such as data analysis and report generation. The system is built with a microservices architecture, leveraging FastAPI, LangGraph, and PostgreSQL.

## Architecture Overview

The backend is composed of the following key components:

*   **Orchestrator Microservice:** This service acts as the central coordinator for the AI agent. It handles user interactions via a chat interface, manages conversation state, and orchestrates the execution of tasks using LangGraph. It interacts with the LLM Connector and Storage services to fulfill user requests.

*   **Storage Microservice:**  This service is responsible for persistent data storage. It uses PostgreSQL to manage user information, conversation history, and LangGraph checkpoints.  It exposes a RESTful API for CRUD operations on users, conversations, and checkpoints.  SQLAlchemy is used as the ORM.

*   **LLM Connector Microservice:** (Described but not fully implemented in the provided code) This service provides an abstraction layer for interacting with large language models (LLMs), such as OpenAI's GPT models.  It handles sending prompts to the LLM and receiving responses.

*   **Main Application (FastAPI):**  The `main.py` file serves as the entry point for the application. It initializes the FastAPI application, registers the routers for the different microservices, and handles configuration loading.

## Data Model

The Storage microservice manages the following key entities:

*   **Users:** Stores user information, including username, email, and a hashed password (security best practices are *essential* here – use a proper hashing library).
*   **Conversations:** Represents a single conversation thread between a user and the AI agent. Each user can have multiple conversations.
*   **Checkpoints:** Stores the state of a LangGraph conversation at a specific point in time. This enables resuming conversations and maintaining context. Checkpoints are stored as JSONB data in PostgreSQL, allowing for efficient storage and retrieval of complex data structures.

## Technologies Used

*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python.
*   **LangGraph:** A library for building stateful, multi-actor applications with LLMs, built on top of LangChain.
*   **PostgreSQL:** A powerful, open-source relational database.
*   **SQLAlchemy:** A Python SQL toolkit and Object-Relational Mapper (ORM).
*   **Pydantic:** A data validation and parsing library that uses Python type hints.
*   **Docker:** (Planned) Used for containerization, ensuring consistent environments across development, testing, and production.
*   **JWT Authentication:** (Planned) JSON Web Tokens will be used for user authentication.

## Getting Started
Before running the code you need to have docker and docker compose (v2) installed. 

To run the project, modify the database url in the storage/database.py: 
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:Mobydick&15@localhost:5432/Finance_agent") 
to connect to your local db

To run the backend, navigate to the project's root directory and run:
uvicorn main:app --reload

## API Endpoints (Storage Microservice)

The Storage microservice exposes the following API endpoints (relative to the `/storage` prefix):

**Users:**

*   `POST /users/`: Create a new user.
*   `GET /users/`: Get a list of all users.
*   `GET /users/{user_id}`: Get a user by ID.
* `GET /users/name/{username}`: Get user by the username.

**Conversations:**

*   `POST /users/{user_id}/conversations/`: Create a new conversation for a user.
*   `GET /conversations/{conversation_id}`: Get a conversation by ID.
*   `GET /users/{user_id}/conversations/`: Get all conversations for a user.

**Checkpoints:**

*   `POST /conversations/{conversation_id}/checkpoints/`: Create a new checkpoint for a conversation.
*   `GET /conversations/{conversation_id}/checkpoints/latest`: Get the latest checkpoint for a conversation.
*  `GET /conversations/{conversation_id}/checkpoints/`: Get all checkpoints.

## Future Improvements

*   **Dockerization:** Containerize the application and its dependencies (PostgreSQL) using Docker Compose for easier deployment and management.
*   **Authentication:** Implement JWT-based authentication for secure user access.
*   **Error Handling:** Implement more robust error handling and logging throughout the application.
*   **Testing:** Add unit and integration tests to ensure code quality and reliability.
*   **Migrations:** Use a database migration tool (e.g., Alembic) to manage schema changes.
*   **Asynchronous Operations:**  Use asynchronous operations (e.g., `async` and `await`) where appropriate to improve performance.
*   **LLM Connector:** Complete the implementation of the LLM Connector microservice.