from fastapi import FastAPI, HTTPException

app = FastAPI(title="Local Agent Mockup Project")

@app.get("/")
async def root():
    return {"message": "Welcome to the mockup FastAPI service!"}

@app.get("/health")
async def health_check():
    try:
        # Simulate a database check or other critical resource
        # For demonstration, we'll just return OK
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e