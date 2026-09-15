# Standalone script to test retrieval quality directly, before involving
# the LLM at all, confirms the right chunks come back for real questions
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Must use the exact same embedding model used during ingestion,
# otherwise the question's vector and the stored vectors won't be
# comparable in the same space
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
)

# Test question specifically about authentication, should retrieve
# only from security-first-steps.md, confirming retrieval correctly
# distinguishes between different topics, not just returning whatever
# was embedded first
question = "How do I make an endpoint require authentication?"

# Retrieves the 3 most relevant chunks for this question
results = vectorstore.similarity_search(question, k=3)

print(f"Question: {question}\n")
for i, doc in enumerate(results):
    print(f"--- Result {i + 1} ---")
    print(f"Source: {doc.metadata.get('source')}")
    print(doc.page_content[:300])
    print()
