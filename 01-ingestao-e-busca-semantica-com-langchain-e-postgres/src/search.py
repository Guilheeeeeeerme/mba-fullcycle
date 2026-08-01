from langchain_postgres import PGVector

from config import COLLECTION_NAME, DATABASE_URL, get_embeddings, get_llm

FALLBACK_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

PROMPT_TEMPLATE = """CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A \"PERGUNTA DO USUÁRIO\""""  # noqa: E501


def _vector_store() -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )


def search(question: str, k: int = 10):
    return _vector_store().similarity_search_with_score(question, k=k)


def _message_text(content) -> str:
    """Normalize AIMessage.content (str or Gemini content blocks) to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(block, "text", None)
                if text:
                    parts.append(str(text))
        return "".join(parts).strip()
    return str(content).strip()


def answer_question(question: str) -> str:
    results = search(question, k=10)
    if not results:
        return FALLBACK_ANSWER

    context = "\n\n---\n\n".join(document.page_content for document, _ in results)
    response = get_llm().invoke(PROMPT_TEMPLATE.format(context=context, question=question))
    return _message_text(response.content)
