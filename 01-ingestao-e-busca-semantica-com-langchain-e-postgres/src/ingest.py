from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import COLLECTION_NAME, DATABASE_URL, PDF_PATH, get_embeddings


def ingest_pdf(pdf_path: str = PDF_PATH) -> int:
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF não encontrado: {path}")

    pages = PyPDFLoader(str(path)).load()
    if not any(page.page_content.strip() for page in pages):
        raise ValueError(
            f"PDF sem texto extraível: {path}. "
            "Use um PDF com camada de texto (não só imagem/scan)."
        )

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    ).split_documents(pages)
    if not chunks:
        raise ValueError(f"Nenhum chunk gerado a partir de {path}.")

    PGVector.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
        pre_delete_collection=True,
    )
    return len(chunks)


if __name__ == "__main__":
    total = ingest_pdf()
    print(f"Ingestão concluída: {total} chunks armazenados.")
