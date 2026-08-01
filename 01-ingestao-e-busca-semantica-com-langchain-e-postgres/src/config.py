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


def get_embeddings():
    provider = _provider()
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "").lower() or (
        "fastembed" if provider == "opencode-go" else provider
    )

    if embedding_provider == "gemini":
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    if embedding_provider == "fastembed":
        # OpenCode Go não oferece embeddings; FastEmbed roda local.
        import warnings

        from langchain_community.embeddings import FastEmbedEmbeddings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            return FastEmbedEmbeddings(model_name=FASTEMBED_MODEL)
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_llm():
    provider = _provider()
    if provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    if provider == "opencode-go":
        api_key = os.getenv("OPENCODE_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENCODE_API_KEY é obrigatória com LLM_PROVIDER=opencode-go "
                "(assinatura OpenCode Go em https://opencode.ai/auth)."
            )
        return ChatOpenAI(
            model=OPENCODE_GO_MODEL,
            api_key=api_key,
            base_url=OPENCODE_GO_BASE_URL,
            temperature=0,
        )
    return ChatOpenAI(model="gpt-5-nano", temperature=0)
