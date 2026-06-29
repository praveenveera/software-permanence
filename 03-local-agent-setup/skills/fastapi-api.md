# FastAPI API Skill

When adding a new API endpoint to the backend:

1. Check existing router imports in `app/main.py`.
2. Use async database sessions if DB connectivity is required.
3. Include explicit error handlers using `HTTPException` with clear detail messages.
4. Create a corresponding test file in `tests/test_api.py`.
5. Run linting and verify API responses before marking the task complete.
