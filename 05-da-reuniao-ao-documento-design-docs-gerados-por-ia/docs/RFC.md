# RFC — Webhooks de Notificação de Pedidos

| Campo | Valor |
| --- | --- |
| Autor | Larissa (Tech Lead) — consolidação a partir da reunião |
| Status | Draft / Proposed |
| Data | 2026-08-01 (pacote de docs) |
| Revisores | Marcos (PM), Bruno (Pedidos), Diego (Plataforma), Sofia (Segurança) |

## Resumo executivo (TL;DR)

Propor um **sistema de webhooks outbound** para notificar clientes B2B de mudanças de status de pedido. Eventos entram em uma **outbox MySQL** na mesma transação de `changeStatus`; um **worker em processo separado** faz **polling a cada 2 s**, entrega HTTP com **HMAC-SHA256**, **retry/backoff (5×)** e **DLQ** com replay admin. Semântica **at-least-once** com `X-Event-Id`. Sem Redis, sem email de alerta e sem dashboard nesta fase.

## Contexto e problema

O OMS já gerencia pedidos com máquina de estados, estoque e histórico, mas **não notifica** sistemas externos. Clientes fazem polling em `GET /orders`. Disparo síncrono no request de status é rejeitado: a transação já é pesada e falha do cliente não pode reverter o status.

## Proposta técnica

1. **Outbox**: tabela(s) no MySQL existente; insert atômico com update de order + history (+ stock).
2. **Worker**: entrypoint `src/worker.ts` + script npm; PrismaClient próprio; loop de polling 2 s; batch de pendentes ordenados por `created_at`.
3. **Módulo** `src/modules/webhooks`: CRUD config, deliveries, processor, schemas Zod, erros `WEBHOOK_*`.
4. **Gancho**: função `publishWebhookEvent(tx, …)` chamada de `OrderService.changeStatus` com o `tx` da transação.
5. **Segurança**: HTTPS only; HMAC-SHA256 do body; secret por endpoint; rotação com grace 24 h.
6. **Entrega**: headers `X-Event-Id`, `X-Signature`, `X-Timestamp`, `X-Webhook-Id`; timeout 10 s; payload snapshot sem items.
7. **Falha**: backoff 1m/5m/30m/2h/12h → `webhook_dead_letter`; `POST /admin/webhooks/dead-letter/:id/replay` com `requireRole('ADMIN')`.

Detalhamento de implementação: `docs/FDD.md`. Decisões: ADRs abaixo.

## Alternativas consideradas

### A1 — HTTP síncrono dentro de `changeStatus`

Descartada: trava o fluxo de status, acopla disponibilidade do cliente à transação, e rollback de status por falha HTTP é inaceitável (`[09:04]` Bruno, consenso Larissa/Diego).

### A2 — Redis Streams / fila externa

Descartada: time pequeno; subir Redis Cluster é overengineering; outbox no MySQL já resolve consistência transacional (`[09:07]` Larissa/Diego).

### A3 — Trigger MySQL em vez de polling

Descartada: MySQL não tem `NOTIFY/LISTEN`; trigger não notifica processo externo de forma limpa (`[09:09]` Diego). Polling 2 s atende &lt; 10 s.

### A4 — Exactly-once delivery

Descartada: exigiria coordenação bilateral complexa; padrão de mercado (Stripe/GitHub) é at-least-once + id de evento (`[09:24–09:25]` Diego).

## Questões em aberto

1. **Rate limiting de saída** quando muitos status mudam em pouco tempo — observar e decidir depois (`[09:38–09:39]`).
2. **Email (ou outro canal) de alerta** se webhook falhar N vezes seguidas — fora desta fase (`[09:37]`).
3. **Estratégia de escala multi-worker** (particionar por `order_id` / lock) — só quando single-worker não bastar (`[09:13]`).
4. **Endurecimento de autorização** no CRUD de webhooks (hoje: qualquer autenticado) — “mais pra frente” (`[09:36–09:37]` Sofia).

## Impacto e riscos

- Touchpoint crítico: `src/modules/orders/order.service.ts` (`changeStatus`).
- Novo processo operacional (`worker`) em deploy/monitoramento.
- Clientes precisam implementar verificação HMAC e dedup.
- Prazo: ~3 sprints + 2 dias revisão Sofia.

## Decisões relacionadas

- [ADR-001 Outbox no MySQL](adrs/ADR-001-outbox-no-mysql.md)
- [ADR-002 Worker polling processo separado](adrs/ADR-002-worker-polling-processo-separado.md)
- [ADR-003 Retry backoff DLQ](adrs/ADR-003-retry-backoff-dlq.md)
- [ADR-004 HMAC-SHA256](adrs/ADR-004-hmac-sha256-secret-por-endpoint.md)
- [ADR-005 At-least-once X-Event-Id](adrs/ADR-005-at-least-once-x-event-id.md)
- [ADR-006 Reuso padrões existentes](adrs/ADR-006-reuso-padroes-existentes.md)
- [ADR-007 Snapshot payload](adrs/ADR-007-snapshot-payload-na-outbox.md)
