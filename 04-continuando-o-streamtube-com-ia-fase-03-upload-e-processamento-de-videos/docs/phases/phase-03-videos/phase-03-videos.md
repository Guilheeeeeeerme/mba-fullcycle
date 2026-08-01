---
kind: phase
name: phase-03-videos
status: draft
sources_mtime: {}
---

# Phase 03 — Upload e Processamento de Vídeos

> **TODO / DRAFT** — SIs e Technical Specs entram após research + validation clean. Espelhar `docs/phases/phase-02-auth/phase-02-auth.md`.

## Objective

Deliver large-file video upload (≤10GB) without blocking the NestJS API, async FFmpeg processing via a queue/worker, MinIO storage, unique video URLs, HTTP range streaming and download, and a clear status cycle `draft → processing → ready | error`.

---

## Step Implementations

### SI-03.x — TBD

**Description:** Placeholder. Break down after TDs are decided. Expected themes:

- SI — Config namespaces + MinIO + queue services in compose
- SI — Video entity + migration + status enum
- SI — Presigned/multipart upload initiation (draft create)
- SI — Queue producer on upload complete
- SI — Worker FFmpeg (metadata + thumbnail) + status updates
- SI — Unique URL + streaming (Range) + download endpoints
- SI — Failure/retry + error status
- SI — Tests (unit/integration/e2e) + CLAUDE.md videos section

**Dependencies:** Phase 01, Phase 02; TDs 01–05

**Acceptance criteria:**

- TBD after plan skill

---

## Technical Specs

_TBD — fill when SIs are written (endpoints, DTOs, env vars, compose services, job payloads)._
