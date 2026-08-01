# PRD — 04 StreamTube Fase 03: Upload e Processamento de Vídeos

## Problema

StreamTube (fases 01–02) já tem NestJS + auth. Falta upload de vídeos grandes (até 10GB), armazenamento S3-compatível, processamento assíncrono (FFmpeg) e ciclo de status até o vídeo ficar pronto para streaming — sem bloquear a API.

## Objetivo

Continuar o greenfield [mba-ia-greenfield-project](https://github.com/devfullcycle/mba-ia-greenfield-project) na **Fase 03 — Upload e Processamento de Vídeos** (foco backend): módulo `videos`, MinIO/S3, fila + worker FFmpeg, compose, migration, URL única, streaming/download e status `draft → processing → ready|error`.

## Escopo

- Pesquisa → `docs/decisions/technical-decisions-phase-03-videos.md`
- Planejamento → `docs/phases/phase-03-videos/` (`context.md`, `validation.md`, `library-refs.md`, `phase-03-videos.md` com SI-03.x + Technical Specs, `progress.md`)
- Implementação em `nestjs-project/`: módulo videos, storage MinIO, queue+worker, compose, migration
- Upload até 10GB **sem** body na API (presigned / multipart)
- Streaming (range) + download; URL única por vídeo
- Atualizar `CLAUDE.md` (seção videos)
- Git flow do greenfield: `feature/*` a partir de `dev`; nunca commit em `main`
- DoD: testes + `tsc` + lint verdes

## Não-objetivos

- Frontend (`next-frontend/`) — fora de escopo desta atividade
- Fase 04+ (edição, canal, player UI, likes/comentários, home)
- Implementação completa do módulo videos **neste scaffold** (só docs + base vendored)
- Decisões inventadas sem research (queue, upload strategy, worker, URL/streaming, failure cycle ficam TBD)

## Critérios de aceite

- [ ] Research: TDs em `docs/decisions/technical-decisions-phase-03-videos.md` (storage = MinIO dado; demais abertas resolvidas)
- [ ] Plan pipeline: pasta `docs/phases/phase-03-videos/` completa (context → validation clean → library-refs → phase com SIs → progress)
- [ ] Upload ≤10GB via presigned/multipart; API não recebe o arquivo no body
- [ ] Vídeo pré-cadastrado como draft ao iniciar upload; status cycle draft → processing → ready|error
- [ ] Worker FFmpeg: metadados/duração + thumbnail; fila não bloqueia request HTTP
- [ ] MinIO no compose; migration TypeORM; streaming range + download; URL única
- [ ] `CLAUDE.md` com seção videos
- [ ] DoD: testes do módulo + `tsc` + lint OK; commits só em `feature/*` desde `dev`

## Workflow (esta atividade)

1. **Research** — decisões técnicas (fila, upload, worker/FFmpeg, URL+range, status/failure); storage MinIO já dado
2. **Plan** — skill/pipeline de fase: context → validate → library-refs → SIs + Technical Specs → progress
3. **Implement** — SIs no NestJS; compose; worker; DoD

## Decisões abertas (research)

| Tema | Status |
| --- | --- |
| Storage | **Dado:** S3-compatible MinIO |
| Queue tech | TBD |
| Upload strategy (presigned vs multipart vs hybrid) | TBD |
| Worker / FFmpeg packaging & job contract | TBD |
| Unique URL + streaming/range | TBD |
| Status / failure cycle & retries | TBD |

## Stack (base)

- NestJS 11 (`nestjs-project/`) — fases 01–02 presentes
- PostgreSQL, Mailpit (compose existente)
- MinIO, fila, worker FFmpeg — a introduzir na Fase 03
- Next.js frontend — **out of scope** aqui

## Entregáveis deste scaffold (agora)

- Cópia vendored do greenfield (sem `.git` aninhado)
- `PRD.md` + `README.md` (wrapper da atividade)
- Stubs TODO em `docs/phases/phase-03-videos/` e `docs/decisions/technical-decisions-phase-03-videos.md`
- Draft PR no monorepo `mba-fullcycle`

## Referências

- Base: https://github.com/devfullcycle/mba-ia-greenfield-project
- Plano: `docs/project-plan.md` (Fase 03)
- Formato de fase: `docs/phases/phase-02-auth/`
- README upstream: `README.upstream.md`
