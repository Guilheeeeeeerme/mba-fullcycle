# PRD — Sistema de Webhooks de Notificação de Pedidos

## Resumo e contexto da feature

Clientes B2B (Atlas Comercial, MaxDistribuição, Nova Cargo) precisam ser notificados quando o status dos pedidos muda no OMS. Hoje fazem polling em `GET /orders`, o que é lento e caro; a Atlas sinalizou risco de churn se não houver entrega até o fim do trimestre. A solução acordada é **webhooks outbound**: o OMS publica eventos de mudança de status para endpoints HTTPS cadastrados pelos clientes.

Fonte: reunião técnica (~55 min) em `TRANSCRICAO.md`; aplicação base sem mecanismo de notificação/eventos.

## Problema e motivação

- Integrações atuais dependem de polling no `GET /orders`.
- Clientes querem percepção de “tempo real” com latência aceitável **abaixo de 10 segundos**.
- Disparo síncrono HTTP dentro da mudança de status é inviável: a transação de `changeStatus` já atualiza pedido, histórico e estoque; HTTP externo travaria o fluxo e não pode causar rollback de status.

## Público-alvo e cenários de uso

| Público | Cenário |
| --- | --- |
| Clientes B2B integrados via API | Recebem `order.status_changed` no endpoint deles quando um pedido muda de status |
| Operadores / usuários autenticados da API | Cadastram, listam, editam e removem webhooks; consultam histórico de entregas |
| Admins | Reprocessam itens da DLQ via endpoint admin |

## Objetivos e métricas de sucesso

| Objetivo | Métrica | Meta |
| --- | --- | --- |
| Notificação com latência aceitável | Tempo entre commit do status e início da tentativa HTTP pelo worker | ≤ 10 s (polling de 2 s atende com folga) |
| Retenção Atlas / B2B | Entrega da feature no prazo alinhado com PM | Até fim de novembro (estimativa: 3 sprints) |
| Confiabilidade de entrega | Política de retry antes de DLQ | 5 tentativas com backoff 1m/5m/30m/2h/12h (~15 h de janela) |

## Escopo

### Incluso

- Outbox MySQL na mesma transação de mudança de status
- Worker separado com polling a cada 2 s
- Retry com backoff + tabela `webhook_dead_letter` + replay admin (`ADMIN`)
- Autenticação de payload HMAC-SHA256, secret por endpoint, rotação com grace 24 h
- Entrega at-least-once com `X-Event-Id` (UUID) para dedup no cliente
- CRUD de configuração de webhooks (url, secret gerada, filtro de status, customer)
- Histórico de deliveries (últimos envios com sucesso/falha, payload, response, latência)
- TLS obrigatório (apenas `https` nas URLs)
- Limite de payload 64 KB (erro se ultrapassar)
- Timeout HTTP do worker: 10 s
- Módulo `src/modules/webhooks` alinhado aos padrões do OMS

### Fora de escopo

1. **Email de alerta** quando webhook falha repetidas vezes — adiado para fase futura (`[09:37]` Larissa / Marcos).
2. **Dashboard visual** / painel frontend para o cliente — projeto separado (`[09:39–09:40]`).
3. **Rate limiting de saída** para o endpoint do cliente — observar e decidir depois (`[09:38–09:39]`).
4. **Arquivamento** de linhas entregues na outbox (ex.: após 30 dias) — fora desta feature (`[09:08]` Diego).
5. **Webhooks inbound** (cliente → OMS) — só outbound (`[09:02–09:03]`).
6. **Escalonamento multi-worker** com particionamento / locks — limitação conhecida; futuro (`[09:12–09:13]`).

## Requisitos funcionais

| ID | Requisito |
| --- | --- |
| FR-01 | Cliente cadastra webhook via `POST` autenticado: URL; secret gerada pelo sistema e devolvida na criação; lista de status de interesse; `customer_id` no body/path (não implícito do JWT) |
| FR-02 | `PATCH` edita, `DELETE` remove, `GET` lista webhooks de um customer |
| FR-03 | Filtro de eventos por lista de status; filtrar **na inserção** da outbox |
| FR-04 | `GET /webhooks/:id/deliveries` — histórico (ex.: últimos 100) com sucesso/falha, payload, response, tempo de resposta |
| FR-05 | Inserir evento na outbox **dentro da mesma transação** de `changeStatus` |
| FR-06 | Worker separado processa pendentes e dispara HTTP |
| FR-07 | Retry 5× com backoff 1m/5m/30m/2h/12h; após teto → DLQ |
| FR-08 | `POST /admin/webhooks/dead-letter/:id/replay` com role `ADMIN`; auditar quem reprocessou |
| FR-09 | Assinar corpo com HMAC-SHA256; header `X-Signature`; secret única por endpoint; rotação com grace 24 h |
| FR-10 | Headers de entrega: `X-Event-Id`, `X-Signature`, `X-Timestamp`, `Content-Type: application/json`, `X-Webhook-Id` |
| FR-11 | Payload JSON enxuto: `event_id`, `event_type` (`order.status_changed`), timestamp ISO 8601, `order_id`, `order_number`, `from_status`, `to_status`, `customer_id`, `total_cents` — **sem items** |
| FR-12 | Recusar URL `http` na validação; exigir `https` |

## Requisitos não funcionais

| ID | Requisito |
| --- | --- |
| NFR-01 | Latência percebida &lt; 10 s; polling 2 s |
| NFR-02 | Timeout HTTP 10 s |
| NFR-03 | Payload máximo 64 KB; erro se ultrapassar |
| NFR-04 | Single-worker: ordenação por `created_at` / por `order_id`; sem garantia global multi-worker |
| NFR-05 | IDs UUID (padrão do Prisma/projeto) |
| NFR-06 | Snapshot do payload na inserção da outbox (estado no momento da mudança) |
| NFR-07 | Logs com Pino existente; revisão de segurança (Sofia) ≥ 2 dias úteis antes do deploy |

## Decisões e trade-offs principais

Ver ADRs. Em resumo: outbox MySQL vs Redis; polling vs trigger; at-least-once vs exactly-once; DLQ em tabela separada; reuso de padrões (`AppError`, Zod, módulos).

## Dependências

- OMS atual (Express, Prisma/MySQL, JWT, `requireRole`)
- Integração no `OrderService.changeStatus`
- Clientes preparados para deduplicar por `X-Event-Id` e validar HMAC

## Riscos e mitigação

| Risco | Probabilidade | Impacto | Mitigação |
| --- | --- | --- | --- |
| Endpoint do cliente indisponível por horas | Média | Alto (atraso de notificação) | Retry 5× ~15 h + DLQ + replay admin |
| Vazamento de secret no lado do cliente | Baixa–média | Alto | Secret por endpoint; rotação com grace 24 h |
| Perda de ordering ao escalar workers | Baixa (agora) | Médio | Documentar limitação single-worker; particionar por `order_id` no futuro |
| Atraso de revisão de segurança | Média | Médio (slip de prazo) | Reservar 2 dias úteis Sofia antes do deploy |

## Critérios de aceitação

- [ ] Mudança de status commitada implica linha na outbox na mesma transação (ou rollback conjunto)
- [ ] Worker (`npm run worker` / `src/worker.ts`) entrega eventos com latência típica &lt; 10 s
- [ ] Cliente valida HMAC-SHA256; URL http rejeitada
- [ ] Após 5 falhas, evento vai à DLQ; admin consegue replay
- [ ] Duplicata possível; `X-Event-Id` estável por evento
- [ ] CRUD + deliveries disponíveis autenticados; replay exige `ADMIN`
- [ ] Sem email de alerta, sem dashboard visual nesta fase

## Estratégia de testes e validação

- Testes de unidade: filtro de status, backoff, assinatura HMAC, validação https
- Testes de integração: `changeStatus` + outbox na mesma transação; worker processa e marca entregue
- Testes de contrato: headers/payload; códigos `WEBHOOK_*`
- Cenários de falha: timeout 10 s, 5xx do cliente, replay DLQ
- Revisão de segurança Sofia (HMAC + geração/rotação de secret) antes do deploy
