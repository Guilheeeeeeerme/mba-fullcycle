# 03 — Skill de auditoria e refatoração arquitetural

Skill Claude Code (`/refactor-arch`) agnóstica de stack: analisa codebase → audita anti-patterns (CRITICAL/HIGH/MEDIUM/LOW) → pede confirmação → refatora para MVC → valida.

**Base:** fork/conteúdo de [devfullcycle/mba-ia-refactor-projects-skill](https://github.com/devfullcycle/mba-ia-refactor-projects-skill) (sem `.git` aninhado). Enunciado original em `ENUNCIADO-BASE.md`.

## Projetos-alvo

| Projeto | Stack | Domínio |
| --- | --- | --- |
| `code-smells-project/` | Python / Flask | E-commerce API |
| `ecommerce-api-legacy/` | Node.js / Express | LMS + checkout |
| `task-manager-api/` | Python / Flask | Task Manager (camadas parciais) |

Skill em cada projeto: `.claude/skills/refactor-arch/` (`SKILL.md` + referências).

## Análise Manual

> Pré-skill: ≥5 issues/projeto com mix de severidades (≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW).

### code-smells-project (Python/Flask)

| # | Severidade | Problema | Onde | Por quê |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | `SECRET_KEY` hardcoded | `app.py` | Credencial no código |
| 2 | CRITICAL | SQL por concatenação (SQLi) | `models.py` (ex.: `id` / login) | Input vira SQL |
| 3 | CRITICAL | Endpoint admin executa SQL arbitrário + reset DB | `app.py` (`/admin/*`) | RCE de dados sem auth |
| 4 | HIGH | `models.py` God Module (SQL + domínio misturados) | `models.py` | Sem SRP / testes |
| 5 | MEDIUM | N+1 em listagem de pedidos/itens | `models.py` | Query por item em loop |
| 6 | MEDIUM | Health/controller vaza `secret_key` | `controllers.py` | Info leak |
| 7 | LOW | Magic strings de status / nomes genéricos | `models.py` / controllers | Legibilidade |
| 8 | LOW | Conexão SQLite global `check_same_thread=False` | `database.py` | Estado global frágil |

### ecommerce-api-legacy (Node/Express)

| # | Severidade | Problema | Onde | Por quê |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | Credenciais / payment key no source | `src/utils.js` `config` | Leak de segredos |
| 2 | CRITICAL | God Class `AppManager` (DB + rotas + checkout) | `src/AppManager.js` | Sem separação MVC |
| 3 | HIGH | Crypto caseira `badCrypto` (não é hash seguro) | `src/utils.js` | Auth quebrada |
| 4 | HIGH | Estado global mutável (`globalCache`, `totalRevenue`) | `src/utils.js` | Corridas / acoplamento |
| 5 | MEDIUM | Validação fraca / campos abreviados no checkout | `AppManager.js` checkout | Dados inválidos |
| 6 | MEDIUM | N+1 em listagens (enrollments por course) | `AppManager.js` | Performance |
| 7 | LOW | Nomes `usr`/`eml`/`pwd`/`c_id` | checkout handler | DX ruim |
| 8 | LOW | Seed com senha fraca em claro no fluxo | `initDb` | Hábito inseguro |

### task-manager-api (Python/Flask)

| # | Severidade | Problema | Onde | Por quê |
| --- | --- | --- | --- | --- |
| 1 | CRITICAL | `SECRET_KEY` hardcoded | `app.py` | Credencial no código |
| 2 | CRITICAL | MD5 para senha (+ serializa hash no JSON) | `models/user.py` | Auth obsoleta / leak |
| 3 | HIGH | SMTP password hardcoded no service | `services/notification_service.py` | Segredo em service |
| 4 | MEDIUM | `datetime.utcnow()` deprecated | models/routes/helpers | API obsoleta |
| 5 | MEDIUM | Rotas gordas / helpers “god util” | `routes/*`, `utils/helpers.py` | Camadas vazam |
| 6 | LOW | `MIN_PASSWORD_LENGTH = 4` / seeds fracos | helpers / `seed.py` | Política fraca |
| 7 | LOW | Imports não usados / ruído em `app.py` | `app.py` | Qualidade |
| 8 | HIGH | Debug + bind `0.0.0.0` default | `app.py` | Superfície de ataque |

## Construção da Skill

### Design

- **Invocação:** `/refactor-arch`
- **Fases:** (1) Analysis → (2) Audit + pause → (3) MVC refactor + validation
- **Referências (obrigatórias):**
  - `project-analysis.md` — heurísticas de stack/arquitetura
  - `anti-patterns-catalog.md` — ≥8 anti-patterns + APIs deprecated
  - `audit-report-template.md` — formato Fase 2
  - `mvc-guidelines.md` — responsabilidades MVC
  - `refactor-playbook.md` — ≥8 before/after
- **Agnosticismo:** branch por stack detectada; smells semânticos (God Class, SQLi, secrets) em vez de regras só-Python/só-Node; projeto 3 melhora in-place.

### Catálogo (resumo)

Hardcoded secrets, SQLi, God Class, weak crypto, fat controller, global mutable state, missing validation, N+1, info leaks, deprecated APIs, magic numbers, duplication.

### Desafios (esperados na execução ao vivo)

- Calibrar Fase 2 para ≥5 findings + ≥1 CRITICAL/HIGH nos 3 stacks
- Não quebrar contratos HTTP na Fase 3
- Adaptar MVC em projeto já parcialmente organizado

## Resultados

> Placeholders — preencher após `claude "/refactor-arch"` em cada projeto.

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | App OK pós-Fase 3 |
| --- | --- | --- | --- | --- | --- |
| code-smells-project | TBD | TBD | TBD | TBD | TBD |
| ecommerce-api-legacy | TBD | TBD | TBD | TBD | TBD |
| task-manager-api | TBD | TBD | TBD | TBD | TBD |

Relatórios: `reports/audit-project-{1,2,3}.md` (placeholders até a run).

### Checklist de validação (por projeto)

- [ ] Fase 1: linguagem / framework / domínio / #arquivos
- [ ] Fase 2: template + ≥5 findings + ≥1 CRITICAL/HIGH + pause
- [ ] Fase 3: MVC + boot + endpoints

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado
- Python 3 + deps dos projetos Flask; Node 18+ para `ecommerce-api-legacy`

### Comandos

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 (skill já copiada)
cd ../ecommerce-api-legacy
npm install
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salvar output da Fase 2 em `reports/audit-project-N.md`. Commitar código refatorado após Fase 3.

### Validar apps (smoke)

```bash
# Flask (1 e 3) — ajustar porta se necessário
pip install -r requirements.txt
python app.py
curl -s localhost:5000/health

# Express (2)
npm start
# ver api.http / curl endpoints documentados no README do projeto
```

## Critérios de aceite

| Critério | Meta |
| --- | --- |
| Fase 1 stack correta | 3/3 |
| Fase 2 ≥5 findings | 3/3 |
| Fase 2 ≥1 CRITICAL/HIGH | 3/3 |
| Fase 3 app funciona | 3/3 |

## Fonte

- Boilerplate: https://github.com/devfullcycle/mba-ia-refactor-projects-skill
- PRD local: `PRD.md`
