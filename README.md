# RAG Knowledge Assistant

A chatbot that answers questions about FastAPI, grounded specifically in
FastAPI's own documentation, not just the AI's general training
knowledge. If the answer isn't actually in the documentation, it says so
honestly instead of guessing.

## How it works

1. A set of FastAPI documentation pages is split into small chunks
2. Each chunk is converted into an embedding, a numeric representation
   of its meaning, and stored in a vector database
3. When someone asks a question, the question is embedded the same way,
   and the chunks with the closest meaning are retrieved
4. Those retrieved chunks, and only those chunks, are handed to an AI
   model, which answers using just that context
5. If the retrieved chunks don't actually contain the answer, the model
   says "I don't have enough information to answer that" instead of
   making something up, and no misleading sources are shown

## Why grounding matters

An AI answering purely from general training knowledge can be
confidently wrong, outdated, or simply not reflect what a specific set
of documents actually says. Retrieval augmented generation forces every
answer to be traceable back to real source material, and this project
is deliberately honest when that source material doesn't have the
answer, rather than filling the gap with a plausible sounding guess.

## Tech stack

- Backend: Python, FastAPI
- Vector database: ChromaDB
- Orchestration: LangChain
- Embeddings and generation: Google Gemini API
- Frontend: React, built with Vite, styled with Tailwind CSS
- Testing: Pytest, with all external API calls mocked

## Project structure

    rag-knowledge-assistant/
      server/
        docs/          source fastapi documentation, chunked and embedded
        ingest.py       one time script, builds the vector database
        generate.py     retrieval and answer generation logic
        main.py         the api itself
      client/           react chat interface

## Running it locally

**Backend**

    cd server
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

You'll need a free Gemini API key from https://aistudio.google.com/apikey,
placed in `server/.env` as:

    GEMINI_API_KEY=your-key-here

Build the vector database, this only needs to be run once:

    python ingest.py

Then start the server:

    uvicorn main:app --reload --port 3000

**Frontend**

    cd client
    npm install
    npm run dev

## Running the tests

    cd server
    pytest test_generate.py -v

These tests mock every external API call, so running them costs
nothing and needs no real API key. A separate script,
`test_retrieval.py`, does make real calls and is meant to be run
manually, not as part of automated testing.

## Continuous integration

Every push to main automatically runs the mocked test suite using
GitHub Actions, confirming the core answer generation logic still
works correctly before anything else depends on it.

## API endpoints

| Method | Path    | What it does                                      |
| ------ | ------- | ------------------------------------------------- |
| GET    | /health | Confirms the server is running                    |
| POST   | /ask    | Answers a question, grounded in the documentation |

Each endpoint was manually tested in Postman during development,
including deliberately out of scope questions, before the automated
tests were written.

## A note on the documentation set

This project answers questions about a deliberately small, hand
picked set of FastAPI documentation pages, not the entire site. This
keeps retrieval quality easy to reason about and test, a production
version answering questions about a much larger document set would
need the same core approach, just at a larger scale.
