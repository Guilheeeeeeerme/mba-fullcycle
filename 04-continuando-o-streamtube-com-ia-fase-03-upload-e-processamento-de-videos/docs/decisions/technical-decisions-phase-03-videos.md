# Technical Decisions — Phase 03: Upload e Processamento de Vídeos

> **Status:** DRAFT / TODO — research ainda não executado. Não inventar decisões aqui; preencher após skill research.

---
scope_type: phase
related_phases: [3]
status: draft
date: TBD
scope_description: "Backend video upload (≤10GB), S3-compatible storage, async processing (FFmpeg worker + queue), unique URL, streaming/download, status cycle."
---

_Subprojects in scope:_

- `nestjs-project/` — videos module, storage integration, queue producer, compose services, migration, streaming/download endpoints.
- `next-frontend/` — **out of scope** for this assignment (upload UI deferred).

---

## Given

### Storage = MinIO (S3-compatible)

**Decision:** MinIO as object storage for videos and thumbnails (S3 API). Wire into `nestjs-project/compose.yaml` in Phase 03.

---

## Open decisions (research later)

### TD-01: Queue technology — TBD

**Context:** Background jobs for FFmpeg processing must not block HTTP.

**Options:** TBD (e.g. BullMQ/Redis, RabbitMQ, SQS-compatible, etc.)

**Decision:** TBD

---

### TD-02: Upload strategy (≤10GB, non-blocking API) — TBD

**Context:** Files must not go through API request body. Prefer presigned URL and/or multipart upload to MinIO.

**Options:** TBD

**Decision:** TBD

---

### TD-03: Worker / FFmpeg packaging & job contract — TBD

**Context:** Extract duration/metadata, generate thumbnail from a frame; report success/failure back to API/DB.

**Options:** TBD

**Decision:** TBD

---

### TD-04: Unique URL + streaming (HTTP range) + download — TBD

**Context:** Public/stable unique URL per video; range requests for playback; explicit download path.

**Options:** TBD

**Decision:** TBD

---

### TD-05: Status / failure cycle & retries — TBD

**Context:** `draft → processing → ready | error`; retries, idempotency, poison messages.

**Options:** TBD

**Decision:** TBD

---

## Next

1. Run research skill against project-plan Fase 03 + NestJS ecosystem.
2. Fill options/recommendation/decision for TD-01…05.
3. Unlock plan pipeline (`docs/phases/phase-03-videos/`).
