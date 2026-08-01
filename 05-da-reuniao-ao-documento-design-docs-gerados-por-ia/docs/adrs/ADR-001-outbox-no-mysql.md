# ADR-001: Outbox no MySQL

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO)
- **Decisores:** Diego, Larissa, Bruno

## Contexto

Precisamos publicar eventos de mudança de status sem acoplar HTTP à transação de `OrderService.changeStatus` (`src/modules/orders/order.service.ts`), que já atualiza order, history e estoque.

## Decisão

Usar **padrão Transactional Outbox** em tabelas no **MySQL existente** (Prisma): na mesma transação SQL da mudança de status, inserir linha em `webhook_outbox`. Worker separado consome pendentes.

## Alternativas consideradas

1. **HTTP síncrono no service** — rejeitado (bloqueio + rollback indevido).
2. **Redis Streams / fila externa** — rejeitado (infra extra; overengineering para time pequeno).

## Consequências

- **+** Consistência atômica status↔evento; sem dual-write.
- **+** Reusa banco/Prisma já operacionais.
- **−** Worker de polling; carga na tabela outbox (índice status + `created_at`; arquivamento 30d fora de escopo).
- **−** Sem broker avançado (fan-out, replay broker-native).
