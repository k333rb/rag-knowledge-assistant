# Minimal FastAPI server, sample backend for the RAG knowledge assistant
from fastapi import FastAPI

app = FastAPI()

# Liveness check, confirms the server is running and reachable
@app.get("/health")
def health():
    return {"status": "ok"}