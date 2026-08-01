---
kind: phase
name: phase-03-videos
status: draft
sources_mtime: {}
---

# phase-03-videos — Context

> **TODO / DRAFT** — preencher no research→plan. Espelhar formato de `docs/phases/phase-02-auth/context.md`.

## Scope

**Phase name:** Fase 03 — Upload e Processamento de Vídeos

**Capabilities** (from `docs/project-plan.md`)

- Serviço de armazenamento de arquivos (vídeos e thumbnails) — MinIO
- Serviço de processamento em segundo plano (filas)
- Upload até 10GB sem impacto na performance da API
- Pré-cadastro automático do vídeo como rascunho ao iniciar o upload
- Processamento automático (duração/metadados) + thumbnail via FFmpeg
- URL única por vídeo
- Reprodução via streaming (range) + download

**Out of scope:** Frontend upload UI; Fase 04+ (edição, canal, player page, social).

**Deliverables:** upload ≤10GB funcional, processamento automático, streaming, URLs únicas.

**Affected subprojects:** `nestjs-project/`

**Deferred subprojects:** `next-frontend/`

**Sequencing notes:** Depends on Fase 01 + Fase 02.

**Neighbors:** Fase 02 Auth (prior), Fase 04 Gerenciamento de Vídeos e Canal (next).

## Decisions Index

- [ ] TD-01 Queue — TBD → `docs/decisions/technical-decisions-phase-03-videos.md`
- [ ] TD-02 Upload strategy — TBD
- [ ] TD-03 Worker/FFmpeg — TBD
- [ ] TD-04 Unique URL + streaming/range — TBD
- [ ] TD-05 Status/failure cycle — TBD
- [x] Storage MinIO — given

## Notes

Stub only. Do not treat as validated context until research + validation pass.
