# ADR-002: Worker em processo separado com polling

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO)
- **Decisores:** Diego, Larissa, Bruno, Marcos

## Contexto

Eventos na outbox precisam ser entregues com latência &lt; 10 s sem viver no mesmo processo da API (`src/server.ts`).

## Decisão

- Entry nova `src/worker.ts` + script tipo `npm run worker`.
- **Polling a cada 2 s** dos eventos pendentes (batch pequeno).
- Processo **separado** da API; mesmo `DATABASE_URL`, **novo** `PrismaClient` (`src/config/database.ts` como referência de factory).
- Single-worker por ora: ordenação por `created_at` / por `order_id`.

## Alternativas consideradas

1. **Trigger MySQL** para “notificar” worker — inviável sem NOTIFY/LISTEN; improvisos (arquivo/endpoint) rejeitados.
2. **Worker embutido na API** — reinício da API derruba o worker.

## Consequências

- **+** Atende SLA &lt; 10 s; isolamento de falhas API↔worker.
- **+** Deploy/ops claros (dois processos).
- **−** Latência mínima ~2 s; sem push imediato.
- **−** Multi-worker futuro perde ordering global (limitação documentada).
