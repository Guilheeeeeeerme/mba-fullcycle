# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Pipeline Python: pull de prompt de baixa qualidade do LangSmith Hub → otimização com técnicas de Prompt Engineering → push público da v2 → avaliação (Helpfulness, Correctness, F1, Clarity, Precision) com meta ≥ 0.8 em todas.

Baseado no boilerplate oficial [devfullcycle/mba-ia-pull-evaluation-prompt](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt).

## Pré-requisitos

- Python 3.9+
- Conta LangSmith + API key
- Chave OpenAI e/ou Google Gemini

## Configuração

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha `.env` (`LANGSMITH_API_KEY`, `USERNAME_LANGSMITH_HUB`, e o provider escolhido).

## Providers

| Provider | Resposta | Avaliação |
| --- | --- | --- |
| OpenAI | `gpt-4o-mini` | `gpt-4o` |
| Gemini | `gemini-2.5-flash` | `gemini-2.5-flash` |

Padrão no `.env.example`: Gemini. Para OpenAI, descomente o bloco correspondente.

## A) Técnicas Aplicadas (Fase 2)

| Técnica | Uso |
| --- | --- |
| **Few-shot Learning** (obrigatório) | 3 exemplos entrada/saída (simples, médio, complexo) no `system_prompt` |
| **Role Prompting** | Persona de Product Manager sênior com regras e edge cases |
| **Chain of Thought (CoT)** | Processo interno passo a passo (quem / o quê / por quê / critérios) sem expor o raciocínio na saída |

Justificativa: Few-shot ancora o formato Markdown de User Story; Role reduz respostas genéricas; CoT melhora Correctness/Clarity em bugs ambíguos.

> Status: starter v2 no repo. Iterar após `evaluate.py` até todas as métricas ≥ 0.8.

## B) Resultados Finais

| Métrica | v1 (baseline) | v2 (otimizado) |
| --- | --- | --- |
| Helpfulness | TBD | TBD |
| Correctness | TBD | TBD |
| F1-Score | TBD | TBD |
| Clarity | TBD | TBD |
| Precision | TBD | TBD |
| Média | TBD | TBD |
| Status | — | TBD |

Link LangSmith (dashboard / prompt público): **TBD** após push + evaluate.

## C) Como Executar

```bash
# 1. Pull do prompt de baixa qualidade
python src/pull_prompts.py
# → prompts/bug_to_user_story_v1.yml

# 2. Editar / iterar o prompt otimizado
# → prompts/bug_to_user_story_v2.yml

# 3. Push público {USERNAME}/bug_to_user_story_v2
python src/push_prompts.py

# 4. Avaliar no LangSmith (usa dataset local + Hub)
python src/evaluate.py

# 5. Testes estruturais do YAML v2
pytest tests/test_prompts.py
```

### Critério de aprovação

- Helpfulness, Correctness, F1-Score, Clarity, Precision **todas** ≥ 0.8
- Média das 5 ≥ 0.8

### Exemplo CLI (alvo)

```
==================================================
Prompt: {seu_username}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

## Estrutura

```
├── .env.example
├── requirements.txt
├── README.md
├── PRD.md
├── prompts/
│   ├── bug_to_user_story_v1.yml
│   └── bug_to_user_story_v2.yml
├── datasets/
│   └── bug_to_user_story.jsonl
├── src/
│   ├── pull_prompts.py
│   ├── push_prompts.py
│   ├── evaluate.py      # boilerplate — não alterar
│   ├── metrics.py       # boilerplate — não alterar
│   └── utils.py         # boilerplate — não alterar
└── tests/
    └── test_prompts.py
```

## Variáveis de ambiente

Ver `.env.example`. Principais: `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `USERNAME_LANGSMITH_HUB`, `LLM_PROVIDER`, `OPENAI_API_KEY` / `GOOGLE_API_KEY`.
