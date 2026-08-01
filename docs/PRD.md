# PRD — mba-fullcycle

Documento curto de produto por atividade. Atividades futuras entram aqui quando forem definidas.

---

## 01 — Ingestão e busca semântica (LangChain + Postgres)

### Problema

Consultar um PDF via chat exige recuperar trechos relevantes e responder só com base nesse contexto, sem inventar conteúdo.

### Objetivo

Aplicação Python que: divide um PDF em chunks, gera embeddings, persiste em PostgreSQL/pgVector e responde perguntas em chat de terminal usando somente o contexto recuperado.

### Escopo

- Ingestão: PDF → chunks (1000 / overlap 150) → embeddings → coleção pgVector (substitui a anterior a cada ingestão)
- Chat terminal grounded no contexto; sem resposta no contexto → mensagem fixa de “sem informações”
- Providers: OpenAI, Gemini, OpenCode Go (embeddings via FastEmbed quando aplicável)
- Infra local: `docker compose` com pgvector
- Config via `.env` / `.env.example`

### Não-objetivos

- UI web / API HTTP
- Multi-documento com versionamento avançado
- Avaliação automática de qualidade das respostas
- Deploy em nuvem

### Critérios de aceite

- [ ] `docker compose up -d` sobe Postgres/pgvector
- [ ] `python src/ingest.py` ingere `document.pdf` (ou `PDF_PATH`)
- [ ] `python src/chat.py` responde com base no PDF; pergunta fora do contexto usa a mensagem padrão
- [ ] Troca de `LLM_PROVIDER` / `EMBEDDING_PROVIDER` documentada (re-ingestão necessária)
- [ ] Chat sem warnings ruidosos no terminal

### Referências

- Branch / PR: [PR #1](https://github.com/Guilheeeeeeerme/mba-fullcycle/pull/1)
- README da atividade: `01-ingestao-e-busca-semantica-com-langchain-e-postgres/README.md`

---

## 02 — TBD

Aguardando enunciado da atividade.
