# ADR-004: HMAC-SHA256 com secret por endpoint

- **Status:** Accepted
- **Data:** reunião técnica (TRANSCRICAO)
- **Decisores:** Sofia, Larissa, Bruno, Diego

## Contexto

Payloads de pedido saem da nossa infra. Clientes precisam autenticar origem e integridade. Já houve vazamento de secret em log de cliente.

## Decisão

- Assinar o **corpo** com **HMAC-SHA256**; enviar em `X-Signature`.
- **Secret única por endpoint** (não global).
- Secret **gerada pelo sistema** na criação; **rotacionável** com **grace period 24 h** (antiga + nova válidas).
- URL **somente https** (validação Zod no schema do módulo).
- Headers auxiliares: `X-Timestamp` (detecção de replay no cliente), `X-Webhook-Id`.

## Alternativas consideradas

1. **Secret global da plataforma** — rejeitado (blast radius de vazamento).
2. **Outros algoritmos** — HMAC-SHA256 é padrão de mercado / libs amplas.

## Consequências

- **+** Autenticidade e integridade; rotação operacional.
- **+** Alinha com práticas Stripe/GitHub-like.
- **−** Cliente deve implementar verificação; complexidade de dual-secret no grace.
- **−** Revisão de segurança Sofia obrigatória antes do deploy.
