# ADR-005: Entrega at-least-once com X-Event-Id

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO)
- **Decisores:** Diego, Larissa, Sofia, Marcos

## Contexto

Falhas após envio bem-sucedido no cliente (ou retries) podem duplicar entregas. Exactly-once end-to-end é complexo.

## Decisão

- Garantia **at-least-once**.
- Gerar **UUID `event_id` na inserção da outbox**; enviar header **`X-Event-Id`**.
- Cliente é responsável por **deduplicar**.
- Documentar no portal de desenvolvedores (Marcos).

## Alternativas consideradas

1. **Exactly-once** — rejeitado (coordenação bilateral; complexidade alta).

## Consequências

- **+** Implementação simples e alinhada ao mercado.
- **+** Id estável por evento (mesmo em retry).
- **−** Carga de dedup no cliente; risco se cliente ignorar a orientação.
