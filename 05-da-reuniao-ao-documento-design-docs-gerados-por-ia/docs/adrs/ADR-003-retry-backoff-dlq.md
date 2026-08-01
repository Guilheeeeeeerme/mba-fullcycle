# ADR-003: Retry com backoff exponencial e DLQ

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO)
- **Decisores:** Diego, Larissa, Bruno, Marcos

## Contexto

Endpoints de clientes podem ficar offline. Precisamos retentar sem pendurar evento para sempre e preservar evidência para debug/reprocessamento.

## Decisão

- **5 tentativas** com backoff **1m / 5m / 30m / 2h / 12h** (~15 h).
- Após teto: mover para tabela **`webhook_dead_letter`** (payload, motivo, timestamp) — separada da outbox.
- Replay manual: `POST /admin/webhooks/dead-letter/:id/replay` com role **ADMIN** e auditoria de quem executou (`requireRole` em `src/middlewares/auth.middleware.ts`).
- Timeout HTTP por tentativa: **10 s**.

## Alternativas consideradas

1. **3 tentativas** — rejeitado (janela curta demais vs manutenções de ~2 h).
2. **Retry indefinido** — rejeitado (evento eternamente pendente se cliente sumiu).
3. **Marcar `failed` só na outbox** — preferida tabela DLQ separada para limpeza/leitura.

## Consequências

- **+** Cobertura típica de indisponibilidade; evidência clara na DLQ.
- **+** Replay controlado por admin.
- **−** Sem notificação proativa ao cliente (email fora de escopo).
- **−** Operação manual de replay.
