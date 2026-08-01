# FDD — Feature Design Document: Webhooks de Pedidos

## Contexto e motivação técnica

O OMS (`order-management-api`) já persiste mudanças de status em transação Prisma (`changeStatus`), mas não emite eventos externos. A feature adiciona outbox + worker HTTP sem degradar a latência/consistência do fluxo de pedidos.

## Objetivos técnicos

- Garantir **atomicidade** status ↔ evento (mesma transação SQL).
- Desacoplar entrega HTTP da API (`src/server.ts` vs `src/worker.ts`).
- Reusar padrões: módulos, Zod, `AppError`, `requireRole`, Pino, error middleware.
- Entregar contratos claros para clientes B2B (HMAC, headers, payload).

## Escopo e exclusões

**Inclui:** modelos Prisma outbox/DLQ/config/deliveries; módulo webhooks; gancho em `changeStatus`; worker; endpoints CRUD/deliveries/replay.

**Exclui:** email de alerta, dashboard, rate limit de saída, arquivamento outbox 30d, multi-worker, inbound webhooks (ver PRD).

## Integração com o sistema existente

| Arquivo | Como integra |
| --- | --- |
| `src/modules/orders/order.service.ts` | Em `changeStatus`, após update/history (e stock), chamar `publishWebhookEvent(tx, …)` **ainda dentro** de `this.prisma.$transaction` |
| `src/shared/errors/app-error.ts` + `src/shared/errors/http-errors.ts` | Novos erros `WEBHOOK_*` estendendo o padrão `AppError` / subclasses HTTP existentes |
| `src/middlewares/error.middleware.ts` | Sem mudança obrigatória: já serializa `AppError`, Zod e Prisma |
| `src/middlewares/auth.middleware.ts` | CRUD autenticado com `authenticate`; replay com `requireRole('ADMIN')` (mesmo padrão de `user.routes.ts`) |
| `src/routes/index.ts` | Registrar `buildWebhookRouter` (e rotas admin) ao lado de orders/customers |
| `src/server.ts` | Continua só a API; worker **não** sobe neste processo |
| `src/config/database.ts` | Worker cria **outro** `PrismaClient` (mesmo `DATABASE_URL`, outro processo) |
| `src/shared/logger/index.ts` | Logs do worker/API via Pino; auditar replay admin |
| `src/modules/orders/order.status.ts` | Fonte dos status filtráveis (`PENDING`…`CANCELLED`) no schema de eventos |
| `prisma/schema.prisma` | Novos models UUID `@default(uuid())` alinhados aos models atuais |

## Fluxos detalhados

### 1. Criação do evento na outbox

1. Operador chama `PATCH /orders/:id/status`.
2. `OrderService.changeStatus` abre transação.
3. Valida transição (`canTransition`), debita/repor stock se aplicável, update order, insert `OrderStatusHistory`.
4. Resolve webhooks ativos do `customer_id` cujo filtro inclui `toStatus`.
5. Se há match: gera UUID `event_id`, monta **snapshot** JSON, insert `webhook_outbox` (`pending`) + opcional registro de delivery futuro.
6. Commit. Falha no insert outbox → rollback de tudo.

### 2. Processamento pelo worker

1. Loop a cada 2 s: seleciona batch de `pending` (e devidos a retry) ordenados por `created_at` / `next_attempt_at`.
2. Marca `processing`, monta request HTTPS com headers, assina body HMAC-SHA256.
3. Timeout 10 s. Sucesso 2xx → `delivered` + log delivery. Falha → incrementa attempt, agenda `next_attempt_at` pelo backoff.

### 3. Retry e DLQ

Backoff após falhas: **1m → 5m → 30m → 2h → 12h** (5 tentativas). Esgotado → move para `webhook_dead_letter` (payload, motivo, timestamp) e limpa/ marca outbox.

### 4. Replay DLQ

Admin `POST /admin/webhooks/dead-letter/:id/replay` → recria outbox `pending` → log de auditoria (quem).

## Contratos públicos

> Paths ilustrativos alinhados à discussão; prefixo API atual em `buildApiRouter`. Autenticação JWT como demais rotas.

### POST /webhooks

Cria configuração. Secret gerada pelo servidor.

Request:

```json
{
  "customerId": "uuid",
  "url": "https://cliente.example/hooks/orders",
  "events": ["SHIPPED", "DELIVERED"]
}
```

Response `201`:

```json
{
  "id": "uuid",
  "customerId": "uuid",
  "url": "https://cliente.example/hooks/orders",
  "events": ["SHIPPED", "DELIVERED"],
  "secret": "whsec_…",
  "active": true
}
```

Erros: `400 WEBHOOK_INVALID_URL`, `400 WEBHOOK_SECRET_REQUIRED` (se fluxo de update exigir), `401`, `404`.

### GET /webhooks?customerId=

Lista webhooks do customer. Response `200` array (secret omitida ou mascarada após criação — **TODO implementação**: alinhar política de exposição; na criação a secret é devolvida uma vez conforme Marcos `[09:31]`).

### PATCH /webhooks/:id

Atualiza url/events/active; rotação de secret via endpoint dedicado se separado.

### DELETE /webhooks/:id

Remove. `204` / `404 WEBHOOK_NOT_FOUND`.

### GET /webhooks/:id/deliveries

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "eventId": "uuid",
      "status": "success",
      "httpStatus": 200,
      "latencyMs": 120,
      "payload": { "event_type": "order.status_changed" },
      "responseBody": "ok",
      "createdAt": "2026-08-01T12:00:00.000Z"
    }
  ]
}
```

### POST /admin/webhooks/dead-letter/:id/replay

Requer `ADMIN`. Response `202`/`200` com novo outbox id. Loga ator.

### Entrega outbound (cliente)

Headers: `Content-Type: application/json`, `X-Event-Id`, `X-Signature`, `X-Timestamp`, `X-Webhook-Id`.

Body (exemplo):

```json
{
  "event_id": "uuid",
  "event_type": "order.status_changed",
  "timestamp": "2026-08-01T12:00:00.000Z",
  "order_id": "uuid",
  "order_number": "ORD-…",
  "from_status": "PROCESSING",
  "to_status": "SHIPPED",
  "customer_id": "uuid",
  "total_cents": 15000
}
```

## Matriz de erros previstos

| Código | Quando | HTTP |
| --- | --- | --- |
| `WEBHOOK_NOT_FOUND` | id inexistente | 404 |
| `WEBHOOK_INVALID_URL` | não-https / URL inválida | 400 |
| `WEBHOOK_SECRET_REQUIRED` | secret ausente onde obrigatória | 400 |
| `WEBHOOK_PAYLOAD_TOO_LARGE` | &gt; 64 KB | 422 |
| `WEBHOOK_INACTIVE` | envio/config inativa | 409 |
| `WEBHOOK_DEAD_LETTER_NOT_FOUND` | replay id inválido | 404 |
| `WEBHOOK_FORBIDDEN` | sem role ADMIN no replay | 403 |

## Estratégias de resiliência

- Timeout 10 s
- Retry 5× backoff 1m/5m/30m/2h/12h
- DLQ + replay manual
- At-least-once + dedup cliente
- Filtrar na inserção (menos ruído na outbox)

## Observabilidade

- **Logs (Pino)**: event_id, webhook_id, attempt, http_status, latency, dead_letter_reason; **não** logar secret em claro (estender redact paths do logger)
- **Métricas**: pending outbox depth, deliveries success/fail rate, DLQ size, worker poll lag
- **Tracing**: correlation via `event_id` / request id da API no enqueue; worker propaga `event_id` nos logs

## Dependências e compatibilidade

Node ≥20, Express, Prisma/MySQL, Zod, JWT existentes. Novo script `worker` no `package.json` (sem alterar comportamento da API atual até o gancho ser ligado).

## Critérios de aceite técnicos

- Outbox insert no mesmo `$transaction` de `changeStatus`
- Worker processo separado; crash da API não mata o loop
- HMAC e headers conforme RFC/ADR-004/005
- Replay admin com auditoria
- Testes cobrindo transação, retry→DLQ, validação https

## Riscos e mitigação

Ver PRD; tecnicamente: regressão em `changeStatus` (mitigar com testes de integração + feature flag opcional se o time decidir — **não discutido na call**; não adotar flag sem nova decisão).
