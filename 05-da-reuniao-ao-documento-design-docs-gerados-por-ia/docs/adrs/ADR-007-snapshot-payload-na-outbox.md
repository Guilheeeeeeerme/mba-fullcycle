# ADR-007: Snapshot do payload na inserção da outbox

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO) — fechamento pós-resumo
- **Decisores:** Larissa, Diego, Bruno

## Contexto

Dúvida: outbox guarda payload já renderizado ou só `order_id` para renderizar no envio?

## Decisão

Persistir **payload snapshot** no momento da inserção na outbox (estado da mudança de status). Se o pedido mudar depois, o evento continua refletindo o momento original.

## Alternativas consideradas

1. **Renderizar no envio** a partir de `order_id` — rejeitado (estado posterior poderia distorcer o evento).

## Consequências

- **+** Fidelidade histórica do evento; simplifica retries (mesmo body/assinatura base).
- **−** Mais armazenamento na outbox/DLQ; payload precisa caber no limite 64 KB.
