# ADR-006: Reuso dos padrões existentes do projeto

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO)
- **Decisores:** Bruno, Larissa, Diego

## Contexto

O OMS já padroniza módulos (`controller`/`service`/`repository`/`routes`/`schemas`), erros tipados, Zod, middleware de erro e logger Pino.

## Decisão

- Criar `src/modules/webhooks` no **mesmo formato** dos módulos existentes (ex.: `src/modules/orders/`).
- Erros com prefixo **`WEBHOOK_`** via `AppError` (`src/shared/errors/app-error.ts`, `http-errors.ts`).
- Reusar `authenticate` / `requireRole` (`src/middlewares/auth.middleware.ts`), `validate` + Zod, `error.middleware.ts`, logger Pino (`src/shared/logger/index.ts`).
- IDs **UUID** como no `prisma/schema.prisma`.
- Hook de publicação: função **`publishWebhookEvent(tx, …)`** recebendo o client transacional — sem injetar repository inteiro no `OrderService`.

## Alternativas consideradas

1. **Stack/pacote paralelo** de notificações — rejeitado implicitamente (reuso máximo).
2. **Injetar webhook repository completo no OrderService** — preferida função pura com `tx`.

## Consequências

- **+** Curva de aprendizado baixa; error middleware já cobre novos erros.
- **+** Consistência operacional e de código.
- **−** Acoplamento ao estilo atual do monólito modular (aceitável neste estágio).

## Referências de código

- `src/modules/orders/order.service.ts` — `changeStatus` + `$transaction`
- `src/shared/errors/app-error.ts`
- `src/middlewares/error.middleware.ts`
- `src/middlewares/auth.middleware.ts` — `requireRole('ADMIN')` (como em `user.routes.ts`)
- `src/routes/index.ts` — registro de routers
- `src/server.ts` — entry API
