# Ingestão e Busca Semântica com LangChain e Postgres

Aplicação Python que divide um PDF em chunks, cria embeddings, armazena-os no PostgreSQL com pgVector e responde perguntas em um chat de terminal usando somente o conteúdo recuperado.

## Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- Chave da OpenAI ou do Google Gemini

## Configuração

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha `.env` com a chave do provedor escolhido. O padrão é OpenAI. Para Gemini, defina `LLM_PROVIDER=gemini` e `GOOGLE_API_KEY`.

Coloque na raiz do projeto o arquivo a ser consultado com o nome `document.pdf`. Para usar outro caminho, altere `PDF_PATH` no `.env`.

## Execução

Suba o PostgreSQL com pgVector:

```bash
docker compose up -d
```

Espere o container ficar saudável e ingira o PDF:

```bash
python src/ingest.py
```

Cada nova ingestão substitui a coleção anterior, evitando documentos duplicados. Em seguida, inicie o chat:

```bash
python src/chat.py
```

Digite `sair` para encerrar. Perguntas sem resposta explícita no contexto retornam: `Não tenho informações necessárias para responder sua pergunta.`

## Variáveis de ambiente

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `LLM_PROVIDER` | `openai` | Provedor: `openai` ou `gemini` |
| `OPENAI_API_KEY` | — | Chave da OpenAI |
| `GOOGLE_API_KEY` | — | Chave do Google Gemini |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/semantic_search` | Conexão com PostgreSQL |
| `PGVECTOR_COLLECTION` | `pdf_documents` | Nome da coleção vetorial |
| `PDF_PATH` | `document.pdf` | Caminho do PDF |

## Modelos e parâmetros

- Chunks: 1000 caracteres, overlap de 150
- Busca vetorial: 10 resultados
- OpenAI: `text-embedding-3-small` e `gpt-5-nano`
- Gemini: `models/embedding-001` e `gemini-2.5-flash-lite`
