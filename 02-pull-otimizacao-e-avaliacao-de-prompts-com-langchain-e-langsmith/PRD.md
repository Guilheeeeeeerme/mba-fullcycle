# PRD — 02 Pull, otimização e avaliação de prompts

## Problema

Prompts no LangSmith Hub com qualidade baixa geram User Stories inconsistentes a partir de relatos de bugs. Sem ciclo pull → otimizar → push → avaliar com métricas objetivas, é difícil provar melhoria e atingir o limiar de aprovação do curso.

## Objetivo

Software Python que: faz pull de `leonanluppi/bug_to_user_story_v1`, otimiza o prompt (Few-shot + ≥1 técnica adicional), faz push público de `{username}/bug_to_user_story_v2` com metadados, e avalia no LangSmith atingindo ≥ 0.8 em Helpfulness, Correctness, F1, Clarity e Precision (e média ≥ 0.8).

## Escopo

- Pull via LangChain Hub → `prompts/bug_to_user_story_v1.yml`
- Prompt otimizado YAML: `prompts/bug_to_user_story_v2.yml` (System/User, regras, few-shot, edge cases)
- Push público com tags/descrição/técnicas
- Avaliação com boilerplate (`evaluate.py` / `metrics.py` / `utils.py` + dataset JSONL de 15 exemplos)
- Providers: OpenAI (`gpt-4o-mini` / `gpt-4o`) e Gemini (`gemini-2.5-flash`)
- 6 testes pytest de estrutura do prompt v2
- Documentação: técnicas, resultados, como executar

## Não-objetivos

- Alterar `evaluate.py`, `metrics.py`, `utils.py` ou o dataset do boilerplate
- UI web / API HTTP
- Treinamento de modelos
- Avaliação live neste scaffold (requer API keys + créditos)

## Critérios de aceite

- [ ] `python src/pull_prompts.py` salva `prompts/bug_to_user_story_v1.yml` a partir de `leonanluppi/bug_to_user_story_v1`
- [ ] `prompts/bug_to_user_story_v2.yml` com Few-shot + ≥1 de CoT/ToT/SoT/ReAct/Role
- [ ] `python src/push_prompts.py` publica `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` público com metadados
- [ ] `python src/evaluate.py`: todas as 5 métricas ≥ 0.8 e média ≥ 0.8
- [ ] `pytest tests/test_prompts.py`: 6 testes passando
- [ ] README com seções A (técnicas), B (resultados), C (execução)

## Entregáveis

- Pasta da atividade no monorepo com estrutura obrigatória
- Scripts implementados: `pull_prompts.py`, `push_prompts.py`, `test_prompts.py`, v2 YAML
- README + PRD locais
- Evidência LangSmith (link prompt + resultados) após push/eval — TBD neste draft

## Stack

- Python 3.9+
- LangChain + LangSmith Prompt Hub
- YAML (prompts), JSONL (dataset)
- OpenAI / Google Gemini
- pytest

## Referências

- Boilerplate: https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt
- Prompt base Hub: `leonanluppi/bug_to_user_story_v1`
