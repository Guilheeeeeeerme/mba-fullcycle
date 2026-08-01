import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/semantic_search",
)
COLLECTION_NAME = os.getenv("PGVECTOR_COLLECTION", "pdf_documents")
PDF_PATH = os.getenv("PDF_PATH", "document.pdf")


def _provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider not in {"openai", "gemini"}:
        raise ValueError("LLM_PROVIDER deve ser 'openai' ou 'gemini'.")
    return provider


def get_embeddings():
    if _provider() == "gemini":
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_llm():
    if _provider() == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    return ChatOpenAI(model="gpt-5-nano", temperature=0)
