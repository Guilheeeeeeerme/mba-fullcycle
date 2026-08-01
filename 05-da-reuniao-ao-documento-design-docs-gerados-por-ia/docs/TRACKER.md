# Tracker de rastreabilidade

Mapeia itens dos design docs → origem em `TRANSCRICAO.md` ou código. Itens sem localização verificável não devem existir nos docs.

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
| --- | --- | --- | --- | --- | --- |
| PRD-CTX-01 | docs/PRD.md | Contexto | Clientes B2B Atlas/MaxDistribuição/Nova Cargo pedem notificação | TRANSCRICAO | `[09:00] Marcos` |
| PRD-NFR-01 | docs/PRD.md | Requisito Não Funcional | Latência aceitável &lt; 10 s | TRANSCRICAO | `[09:02] Marcos` |
| PRD-ESC-01 | docs/PRD.md | Restrição | Apenas webhooks outbound | TRANSCRICAO | `[09:02] Sofia` / `[09:02] Marcos` |
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | POST webhook; secret gerada; events; customer no body/path | TRANSCRICAO | `[09:31] Marcos` / `[09:32] Larissa` |
| PRD-FR-02 | docs/PRD.md | Requisito Funcional | PATCH/DELETE/GET webhooks | TRANSCRICAO | `[09:33] Bruno` |
| PRD-FR-03 | docs/PRD.md | Requisito Funcional | Filtro de status na inserção da outbox | TRANSCRICAO | `[09:33] Marcos` / `[09:34] Bruno` |
| PRD-FR-04 | docs/PRD.md | Requisito Funcional | GET deliveries histórico | TRANSCRICAO | `[09:34] Marcos` |
| PRD-FR-05 | docs/PRD.md | Requisito Funcional | Outbox na mesma transação de changeStatus | TRANSCRICAO | `[09:40] Bruno` |
| PRD-FR-07 | docs/PRD.md | Requisito Funcional | Retry 5× backoff 1m/5m/30m/2h/12h → DLQ | TRANSCRICAO | `[09:17] Larissa` / `[09:18] Diego` |
| PRD-FR-08 | docs/PRD.md | Requisito Funcional | Replay DLQ admin + role ADMIN | TRANSCRICAO | `[09:18] Diego` / `[09:36] Sofia` |
| PRD-FR-09 | docs/PRD.md | Requisito Funcional | HMAC-SHA256; secret por endpoint; grace 24h | TRANSCRICAO | `[09:20–09:22] Sofia` |
| PRD-FR-10 | docs/PRD.md | Requisito Funcional | Headers X-Event-Id, X-Signature, X-Timestamp, X-Webhook-Id | TRANSCRICAO | `[09:44] Diego` / `[09:44] Sofia` |
| PRD-FR-11 | docs/PRD.md | Requisito Funcional | Payload enxuto sem items | TRANSCRICAO | `[09:43] Diego` |
| PRD-FR-12 | docs/PRD.md | Requisito Não Funcional | HTTPS obrigatório | TRANSCRICAO | `[09:23] Sofia` |
| PRD-OUT-01 | docs/PRD.md | Fora de escopo | Email de alerta adiado | TRANSCRICAO | `[09:37] Larissa` |
| PRD-OUT-02 | docs/PRD.md | Fora de escopo | Dashboard visual fora | TRANSCRICAO | `[09:39–09:40] Larissa` |
| PRD-OUT-03 | docs/PRD.md | Fora de escopo | Rate limiting observar depois | TRANSCRICAO | `[09:38–09:39] Diego/Larissa` |
| PRD-MET-01 | docs/PRD.md | Objetivo | Meta latência &lt; 10 s / polling 2 s | TRANSCRICAO | `[09:10] Marcos` / `[09:09] Diego` |
| PRD-RSK-01 | docs/PRD.md | Risco | Cliente offline → retry+DLQ | TRANSCRICAO | `[09:14–09:18]` |
| PRD-RSK-02 | docs/PRD.md | Risco | Vazamento de secret → rotação 24h | TRANSCRICAO | `[09:22] Diego/Sofia` |
| RFC-ALT-01 | docs/RFC.md | Trade-off | Descarte HTTP síncrono | TRANSCRICAO | `[09:04] Bruno` |
| RFC-ALT-02 | docs/RFC.md | Trade-off | Descarte Redis Streams | TRANSCRICAO | `[09:07] Diego` |
| RFC-ALT-03 | docs/RFC.md | Trade-off | Descarte trigger MySQL | TRANSCRICAO | `[09:09] Diego` |
| RFC-ALT-04 | docs/RFC.md | Trade-off | Descarte exactly-once | TRANSCRICAO | `[09:25] Diego` |
| RFC-OPEN-01 | docs/RFC.md | Questão em aberto | Rate limiting de saída | TRANSCRICAO | `[09:38–09:39]` |
| RFC-OPEN-02 | docs/RFC.md | Questão em aberto | Email de alerta futuro | TRANSCRICAO | `[09:37]` |
| RFC-OPEN-03 | docs/RFC.md | Questão em aberto | Escala multi-worker | TRANSCRICAO | `[09:13] Diego` |
| RFC-OPEN-04 | docs/RFC.md | Questão em aberto | Endurecer auth CRUD | TRANSCRICAO | `[09:36–09:37] Sofia` |
| FDD-FLOW-01 | docs/FDD.md | Fluxo | publishWebhookEvent dentro da transação | TRANSCRICAO | `[09:41] Bruno` |
| FDD-FLOW-02 | docs/FDD.md | Fluxo | Worker polling 2s | TRANSCRICAO | `[09:09] Diego` |
| FDD-NFR-01 | docs/FDD.md | Requisito Não Funcional | Timeout HTTP 10s | TRANSCRICAO | `[09:42] Diego` |
| FDD-NFR-02 | docs/FDD.md | Requisito Não Funcional | Payload max 64KB | TRANSCRICAO | `[09:24] Diego/Larissa` |
| FDD-ERR-01 | docs/FDD.md | Restrição | Códigos WEBHOOK_* | TRANSCRICAO | `[09:28–09:29] Bruno/Larissa` |
| FDD-INT-01 | docs/FDD.md | Integração | changeStatus + $transaction | CODIGO | `src/modules/orders/order.service.ts` |
| FDD-INT-02 | docs/FDD.md | Integração | AppError base | CODIGO | `src/shared/errors/app-error.ts` |
| FDD-INT-03 | docs/FDD.md | Integração | error middleware | CODIGO | `src/middlewares/error.middleware.ts` |
| FDD-INT-04 | docs/FDD.md | Integração | requireRole ADMIN | CODIGO | `src/middlewares/auth.middleware.ts` |
| FDD-INT-05 | docs/FDD.md | Integração | Registro de rotas API | CODIGO | `src/routes/index.ts` |
| FDD-INT-06 | docs/FDD.md | Integração | Entry API vs worker | CODIGO | `src/server.ts` |
| FDD-INT-07 | docs/FDD.md | Integração | PrismaClient factory | CODIGO | `src/config/database.ts` |
| FDD-INT-08 | docs/FDD.md | Integração | Logger Pino | CODIGO | `src/shared/logger/index.ts` |
| FDD-INT-09 | docs/FDD.md | Integração | Status machine | CODIGO | `src/modules/orders/order.status.ts` |
| FDD-INT-10 | docs/FDD.md | Integração | UUID no schema | CODIGO | `prisma/schema.prisma` |
| ADR-001 | docs/adrs/ADR-001-outbox-no-mysql.md | Decisão | Outbox MySQL | TRANSCRICAO | `[09:06–09:08] Diego` |
| ADR-002 | docs/adrs/ADR-002-worker-polling-processo-separado.md | Decisão | Worker separado + polling 2s | TRANSCRICAO | `[09:09–09:11]` |
| ADR-003 | docs/adrs/ADR-003-retry-backoff-dlq.md | Decisão | Retry/backoff/DLQ + replay | TRANSCRICAO | `[09:15–09:18]` |
| ADR-004 | docs/adrs/ADR-004-hmac-sha256-secret-por-endpoint.md | Decisão | HMAC-SHA256 + rotação | TRANSCRICAO | `[09:20–09:22] Sofia` |
| ADR-005 | docs/adrs/ADR-005-at-least-once-x-event-id.md | Decisão | At-least-once + X-Event-Id | TRANSCRICAO | `[09:24–09:26]` |
| ADR-006 | docs/adrs/ADR-006-reuso-padroes-existentes.md | Decisão | Reuso módulos/AppError/Pino | TRANSCRICAO | `[09:27–09:30]` / CODIGO `src/modules/orders/` |
| ADR-007 | docs/adrs/ADR-007-snapshot-payload-na-outbox.md | Decisão | Snapshot na inserção | TRANSCRICAO | `[09:51–09:52] Larissa/Diego` |
| ADR-002-LIM | docs/adrs/ADR-002-worker-polling-processo-separado.md | Restrição | Ordering só single-worker / por order_id | TRANSCRICAO | `[09:12–09:13] Diego/Larissa` |
| ADR-006-UUID | docs/adrs/ADR-006-reuso-padroes-existentes.md | Decisão | IDs UUID | TRANSCRICAO | `[09:51] Larissa` / CODIGO `prisma/schema.prisma` |
