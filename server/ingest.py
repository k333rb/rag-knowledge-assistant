# One time script that reads the source documentation, splits it into
# chunks, generates embeddings, and stores everything in ChromaDB
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Loads every markdown file in the docs folder as a separate document
loader = DirectoryLoader(
    "docs",
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)
documents = loader.load()

# Splits each document into overlapping chunks, so context isn't lost
# at chunk boundaries and each chunk stays a manageable, focused size
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(documents)

print(f"Loaded {len(documents)} documents, split into {len(chunks)} chunks")

# Converts each chunk into an embedding and stores it in a local Chroma database
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db",
)

print("Embeddings generated and stored in chroma_db")