# Project Instructions

## Architecture & Stack
- Backend: FastAPI (Python 3.11, Pydantic v2)
- Database: PostgreSQL

## Core Rules
- Do not modify database schemas without explicit permission.
- Do not introduce new third-party dependencies without explaining the rationale.
- Run linting and tests before proposing a completed task.

## Code Style
- Use asynchronous database operations (async/await) in Python.
- Add unit tests for all new business logic.

## Safety Constraints
- Never print secrets, API tokens, or environment files to standard out.
- Do not delete source files unless explicitly requested.
- Present a concrete plan before executing multi-file changes.
