# Processo — Design Docs gerados por IA

## Sobre o desafio

Transformar a transcrição de uma reunião técnica (`TRANSCRICAO.md`) e o código de um OMS Node.js/TypeScript em um pacote acionável de design docs: PRD, RFC, ADRs, FDD e Tracker. A feature alvo é o **Sistema de Webhooks de Notificação de Pedidos** (outbound). Nenhuma informação nos documentos deve ser inventada — tudo rastreia à transcrição ou ao código existente em `src/` / `prisma/`.

Este README documenta **como** o pacote foi produzido (ferramentas, workflow, prompts, iterações), não o enunciado original. O repositório base do desafio: [mba-ia-desafio-design-docs-com-ia](https://github.com/devfullcycle/mba-ia-desafio-design-docs-com-ia).

## Ferramentas de IA utilizadas

| Ferramenta | Papel |
| --- | --- |
| Cursor (Composer) | Leitura do repo, extração de decisões da transcrição, geração e revisão dos Markdowns, checagem de caminhos reais em `src/` |
| Graph/search do workspace | Localizar símbolos (`changeStatus`, `AppError`, `requireRole`, logger Pino) para amarrar FDD/ADRs ao código |

## Workflow adotado

1. **Setup**: clonar o repositório base sem `.git` aninhado; preservar `TRANSCRICAO.md`, `src/`, `prisma/`, `tests/` intactos.
2. **Exploração**: mapear módulos (`orders`, middlewares, erros, Prisma UUID) e ler a transcrição completa (~55 min).
3. **ADRs primeiro**: fechar as 6 decisões principais da call (outbox, worker, retry/DLQ, HMAC, at-least-once, reuso de padrões) + snapshot de payload.
4. **RFC**: consolidar proposta, alternativas descartadas e questões em aberto, com links aos ADRs.
5. **FDD**: detalhar fluxos, contratos HTTP, erros `WEBHOOK_*`, integração com arquivos reais.
6. **PRD**: consolidar por quê/o quê, escopo, métricas e fora de escopo explícito.
7. **Tracker**: cruzar cada item com `[hh:mm] Falante` ou caminho de código.
8. **README do processo**: este arquivo (por último).

## Prompts customizados

```text
A partir de TRANSCRICAO.md, liste APENAS decisões FECHADAS (com consenso explícito),
itens FORA DE ESCOPO / adiados, e questões em aberto. Para cada item cite
timestamp + falante. Não invente requisitos. Agrupe nas 6 decisões-alvo:
outbox MySQL, worker polling separado, retry/backoff/DLQ, HMAC-SHA256,
at-least-once + X-Event-Id, reuso de padrões do código.
```

```text
Escreva docs/FDD.md acionável. Seção obrigatória "Integração com o sistema
existente" deve citar ≥4 caminhos REAIS do repo (verifique que existem):
order.service changeStatus, AppError, error middleware, requireRole, server.ts,
routes/index.ts. Contratos: CRUD webhooks + deliveries + replay admin.
Erros com prefixo WEBHOOK_. Payload e headers exatamente como na transcrição.
Não altere src/, prisma/, tests/.
```

## Iterações e ajustes

1. **Rascunho genérico vs. fonte**: primeira passagem misturou “fila Redis” como opção viva; a call descarta Redis como overengineering. Ajuste: Redis só como alternativa descartada no RFC/ADR-001, com trade-off citado por Diego `[09:07]`.
2. **JWT / customer_id**: rascunho assumiu `customer_id` do JWT; a reunião corrige — JWT é de operador, `customer_id` vai no body/path (`[09:32]` Larissa). PRD/FDD atualizados.
3. **Ordering**: texto inicial falou em “garantia global”; call limita a single-worker / por `order_id`. Registrado como limitação conhecida.
4. **Tracker**: itens sem timestamp removidos ou reescritos até cada linha ter `TRANSCRICAO`/`CODIGO` verificável.

## Como navegar a entrega

Ordem sugerida de leitura:

1. `TRANSCRICAO.md` — fonte primária
2. `docs/adrs/` — decisões fechadas
3. `docs/RFC.md` — proposta e abertos
4. `docs/FDD.md` — como implementar
5. `docs/PRD.md` — produto / escopo
6. `docs/TRACKER.md` — rastreabilidade
7. Este `README.md` — processo

Estrutura do pacote:

```
.
├── README.md
├── TRANSCRICAO.md
├── docs/
│   ├── PRD.md
│   ├── RFC.md
│   ├── FDD.md
│   ├── TRACKER.md
│   └── adrs/
│       ├── ADR-001-outbox-no-mysql.md
│       ├── ADR-002-worker-polling-processo-separado.md
│       ├── ADR-003-retry-backoff-dlq.md
│       ├── ADR-004-hmac-sha256-secret-por-endpoint.md
│       ├── ADR-005-at-least-once-x-event-id.md
│       ├── ADR-006-reuso-padroes-existentes.md
│       └── ADR-007-snapshot-payload-na-outbox.md
├── src/          (não alterado)
├── prisma/       (não alterado)
└── tests/        (não alterado)
```

## TODO / refinamentos futuros

- [ ] Revisar cobertura do Tracker ≥80% após qualquer expansão de seções
- [ ] Passar checklist de aceite do enunciado item a item antes do PR final (não-draft)
- [ ] Revisar exemplos de payload/status codes no FDD contra schemas Zod quando forem implementados
