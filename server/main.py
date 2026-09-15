# FastAPI server exposing the RAG pipeline as a real HTTP endpoint
from fastapi import FastAPI
from pydantic import BaseModel
from generate import answer_question
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allows the React frontend, running on a different port, to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

# Defines the expected shape of an incoming question request,
# FastAPI uses this to automatically validate the request body


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: QuestionRequest):
    result = answer_question(request.question)
    return result
