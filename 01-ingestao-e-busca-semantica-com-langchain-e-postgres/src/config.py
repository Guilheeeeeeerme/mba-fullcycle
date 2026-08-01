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

OPENCODE_GO_BASE_URL = "https://opencode.ai/zen/go/v1"
OPENCODE_GO_MODEL = os.getenv("OPENCODE_GO_MODEL", "glm-5.1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
FASTEMBED_MODEL = os.getenv(
    "FASTEMBED_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


def _provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider not in {"openai", "gemini", "opencode-go"}:
        raise ValueError(
            "LLM_PROVIDER deve ser 'openai', 'gemini' ou 'opencode-go'."
        )
    return provider


def _require_env(name: str, hint: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} é obrigatória {hint}")
    return value


def get_embeddings():
    provider = _provider()
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "").lower() or (
        "fastembed" if provider == "opencode-go" else provider
    )

    if embedding_provider == "gemini":
        api_key = _require_env(
            "GOOGLE_API_KEY",
            "com EMBEDDING_PROVIDER=gemini "
            "(ou LLM_PROVIDER=gemini).",
        )
        return GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=api_key,
        )
    if embedding_provider == "fastembed":
        # OpenCode Go não oferece embeddings; FastEmbed roda local.
        import warnings

        from langchain_community.embeddings import FastEmbedEmbeddings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            return FastEmbedEmbeddings(model_name=FASTEMBED_MODEL)
    if embedding_provider != "openai":
        raise ValueError(
            "EMBEDDING_PROVIDER deve ser 'openai', 'gemini' ou 'fastembed'."
        )
    api_key = _require_env(
        "OPENAI_API_KEY",
        "com EMBEDDING_PROVIDER=openai "
        "(ou LLM_PROVIDER=openai).",
    )
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL, api_key=api_key)


def get_llm():
    provider = _provider()
    if provider == "gemini":
        api_key = _require_env(
            "GOOGLE_API_KEY",
            "com LLM_PROVIDER=gemini.",
        )
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=api_key,
            temperature=0,
        )
    if provider == "opencode-go":
        api_key = _require_env(
            "OPENCODE_API_KEY",
            "com LLM_PROVIDER=opencode-go "
            "(assinatura OpenCode Go em https://opencode.ai/auth).",
        )
        return ChatOpenAI(
            model=OPENCODE_GO_MODEL,
            api_key=api_key,
            base_url=OPENCODE_GO_BASE_URL,
            temperature=0,
        )
    api_key = _require_env(
        "OPENAI_API_KEY",
        "com LLM_PROVIDER=openai.",
    )
    return ChatOpenAI(model=OPENAI_MODEL, api_key=api_key, temperature=0)
