# Takes a question, retrieves relevant chunks, and generates an answer
# grounded specifically in those chunks, not the model's general knowledge
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
)

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")


def answer_question(question):
    # Retrieves the most relevant chunks for this specific question
    results = vectorstore.similarity_search(question, k=3)

    # Combines the retrieved chunks into one block of context text
    context = "\n\n".join(doc.page_content for doc in results)

    # Instructs the model to answer only from the provided context,
    # and to say so plainly if the answer isn't actually there
    prompt = f"""You are a helpful assistant answering questions about FastAPI.
Use ONLY the following context to answer the question. If the answer is
not contained in the context, say "I don't have enough information to
answer that" rather than guessing.

Context:
{context}

Question: {question}

Answer:"""

    response = llm.invoke(prompt)

    # Newer SDK responses return content as a list of blocks, extract
    # just the actual text rather than the full internal structure
    if isinstance(response.content, list):
        answer_text = "".join(
            block.get("text", "") for block in response.content if isinstance(block, dict)
        )
    else:
        answer_text = response.content

    # Only attach sources if the model actually found an answer,
    # showing sources alongside an "I don't know" response is
    # misleading, since the retrieved chunks weren't actually relevant
    if "I don't have enough information" in answer_text:
        sources = []
    else:
        sources = list(set(doc.metadata.get("source") for doc in results))

    return {"answer": answer_text, "sources": sources}


if __name__ == "__main__":
    result = answer_question("How do I make a query parameter optional?")
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])
