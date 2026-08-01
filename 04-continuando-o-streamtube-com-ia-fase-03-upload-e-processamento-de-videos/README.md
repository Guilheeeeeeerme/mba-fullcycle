# 04 — Continuando o StreamTube com IA — Fase 03: Upload e Processamento de Vídeos

Atividade do monorepo [mba-fullcycle](https://github.com/Guilheeeeeeerme/mba-fullcycle). Continua o greenfield StreamTube na **Fase 03** (backend): upload grande, MinIO, fila + worker FFmpeg, streaming.

Base vendored de [devfullcycle/mba-ia-greenfield-project](https://github.com/devfullcycle/mba-ia-greenfield-project) (sem `.git` aninhado). README original do upstream: [`README.upstream.md`](./README.upstream.md). Detalhes de produto: [`PRD.md`](./PRD.md).

## Overview

| Item | Valor |
| --- | --- |
| Foco | Backend NestJS — módulo videos + storage + queue/worker |
| Fora de escopo | Frontend Next.js; fases 04+ |
| Storage | MinIO (S3-compatible) — decisão dada |
| Upload | Até 10GB; **não** via body da API (presigned/multipart) |
| Status do vídeo | `draft → processing → ready \| error` |
| Status desta pasta | **Scaffold** — Phase 03 ainda TODO |

Árvore útil:

```
├── PRD.md                 # objetivos / aceite / workflow
├── README.md              # este wrapper
├── README.upstream.md     # README do greenfield
├── CLAUDE.md              # agent context (atualizar com seção videos)
├── nestjs-project/        # API NestJS (fases 01–02 prontas)
├── next-frontend/         # fora de escopo desta atividade
├── docs/
│   ├── project-plan.md
│   ├── decisions/         # + technical-decisions-phase-03-videos.md (stub)
│   └── phases/
│       ├── phase-01-… / phase-02-…
│       └── phase-03-videos/   # stubs TODO
└── scripts/
```

## Workflow

Pipeline do greenfield (research → plan → implement). Nesta atividade:

1. **Research** — preencher `docs/decisions/technical-decisions-phase-03-videos.md` (fila, upload, worker/FFmpeg, URL+streaming, status/failure; MinIO já fixo).
2. **Plan** — `docs/phases/phase-03-videos/`: `context.md` → `validation.md` clean → `library-refs.md` → `phase-03-videos.md` (SI-03.x + Technical Specs) → `progress.md`.
3. **Implement** — SIs no `nestjs-project/`; compose (MinIO + queue + worker); migration; DoD.

Git flow **dentro** do greenfield (quando for implementar de fato): branches `feature/*` a partir de `dev`; nunca commit em `main`.

No monorepo mba-fullcycle: branch `04-streamtube-fase-03-upload-processamento-videos`.

## Acceptance checklist

- [ ] TDs Phase 03 decididas (exceto o que o PRD marca como dado)
- [ ] Pasta `docs/phases/phase-03-videos/` completa e validation clean
- [ ] Módulo videos + MinIO + fila/worker FFmpeg + compose + migration
- [ ] Upload ≤10GB sem bloquear API; status cycle; URL única; streaming/download
- [ ] `CLAUDE.md` com seção videos
- [ ] Testes + `tsc` + lint verdes

## Como Executar

### Fork / base

Este diretório já contém a cópia vendored do greenfield. Para atualizar a base:

```bash
git clone --depth 1 https://github.com/devfullcycle/mba-ia-greenfield-project.git /tmp/gf
rsync -a --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='.env' \
  --exclude='*.fig' --exclude='whiteboard.svg' /tmp/gf/ ./
```

### Backend (compose — fases 01–02)

```bash
cd nestjs-project
cp .env.example .env   # ajustar secrets locais; não commitar .env
docker compose up -d
# migrations / smoke conforme README.upstream.md
```

MinIO, fila e worker FFmpeg entram na Fase 03 (ainda não wired neste scaffold).

### Frontend

Não executar para esta atividade (out of scope).

## Status

| Etapa | Estado |
| --- | --- |
| Greenfield vendored | Feito |
| PRD + README wrapper | Feito |
| Stubs Phase 03 docs | Draft/TODO |
| Research TDs | Pendente |
| Plan SIs | Pendente |
| Implement videos module | Pendente |
| DoD (test/tsc/lint) | Pendente |

## Referências

- Upstream: https://github.com/devfullcycle/mba-ia-greenfield-project
- Formato de fase: `docs/phases/phase-02-auth/`
- Plano: `docs/project-plan.md` § Fase 03
