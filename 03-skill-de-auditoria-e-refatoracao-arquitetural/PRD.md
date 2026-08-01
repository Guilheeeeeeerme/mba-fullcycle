# PRD — 03 Skill de auditoria e refatoração arquitetural

## Problema

Três backends legados (2× Flask, 1× Express) misturam segurança fraca, God Classes e MVC quebrado. Auditoria + refatoração manual escala mal.

## Objetivo

Entregar uma **Claude Code skill** (`refactor-arch`, invocação `/refactor-arch`) agnóstica de tecnologia que:

1. Detecta stack e arquitetura atual
2. Audita anti-patterns com severidade CRITICAL / HIGH / MEDIUM / LOW (MVC + SOLID), com arquivo/linha
3. Pausa para confirmação humana
4. Refatora para MVC e valida boot + endpoints

## Escopo

- Skill em `.claude/skills/refactor-arch/` (SKILL.md + markdown de referência) nos 3 projetos
- Projetos-base do repositório oficial Full Cycle (`mba-ia-refactor-projects-skill`)
- Relatórios em `reports/audit-project-{1,2,3}.md`
- README com Análise Manual, Construção da Skill, Resultados, Como Executar

## Não-objetivos (neste scaffold)

- Execução live completa da skill nos 3 projetos (próximo passo)
- UI / deploy cloud
- Outras ferramentas além de Claude Code / Gemini CLI / Codex (enunciado permite; este repo usa Claude Code)

## Critérios de aceite

| Critério | Requisito |
| --- | --- |
| Fase 1 detecta stack | 3/3 projetos |
| Fase 2 ≥5 findings | 3/3 |
| Fase 2 ≥1 CRITICAL ou HIGH | 3/3 |
| Fase 3 aplicação funciona | 3/3 |

## Referências

- Base: https://github.com/devfullcycle/mba-ia-refactor-projects-skill
- Branch monorepo: `03-skill-auditoria-refatoracao-arquitetural`
- Pasta: `03-skill-de-auditoria-e-refatoracao-arquitetural/`
