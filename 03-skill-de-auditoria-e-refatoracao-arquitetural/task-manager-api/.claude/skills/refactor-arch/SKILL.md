---
name: refactor-arch
description: Analyze any backend codebase, audit MVC/SOLID anti-patterns by severity, pause for confirmation, then refactor toward MVC and validate the app still works. Technology-agnostic.
---

# /refactor-arch — Architectural Audit & MVC Refactor

Invoke with `/refactor-arch`. Run the three phases **in order**. Do not skip the Phase 2 confirmation gate.

## References (read before acting)

| File | Purpose |
| --- | --- |
| `project-analysis.md` | Stack/architecture detection heuristics |
| `anti-patterns-catalog.md` | Anti-pattern signals + severity |
| `audit-report-template.md` | Exact Phase 2 report format |
| `mvc-guidelines.md` | Target MVC layer responsibilities |
| `refactor-playbook.md` | Before/after transformation patterns |

## Severity scale (MVC + SOLID)

- **CRITICAL** — Security exposure, credentials hardcoded, SQLi, God Class spanning DB + business + routing, broken separation that blocks safe change
- **HIGH** — Heavy business logic in controllers/routes, no DI / global mutable state, strong MVC/SOLID violations
- **MEDIUM** — N+1 queries, missing validation, duplication, weak middleware/error handling
- **LOW** — Naming, magic numbers, readability, minor style debt

## Phase 1 — Analysis

1. Scan the project root (manifests: `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, etc.).
2. Detect language, framework, DB, domain, and current architecture shape using `project-analysis.md`.
3. Count source files analyzed (exclude `node_modules`, `.venv`, `vendor`, build artifacts).
4. Print a summary block:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <lang>
Framework:     <framework + version if known>
Dependencies:  <key libs>
Domain:        <inferred domain>
Architecture:  <monolith / layered / partial MVC / other>
Source files:  <N> files analyzed
DB tables:     <list or unknown>
================================
```

Do **not** modify files in Phase 1.

## Phase 2 — Audit report + confirmation

1. Walk source against `anti-patterns-catalog.md` (≥ check all catalog entries; include deprecated API detection when applicable).
2. Emit findings using `audit-report-template.md`.
3. Every finding MUST include: severity, title, file path, line range, description, impact, recommendation.
4. Order findings CRITICAL → HIGH → MEDIUM → LOW.
5. Require **at least 5 findings** when smells exist; always include ≥1 CRITICAL or HIGH if present in the codebase.
6. **STOP and ask:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

7. Modify **no** files until the user explicitly confirms `y` / yes.
8. Optionally save the Phase 2 report to `../reports/audit-project-N.md` (or `reports/` at assignment root) when the user requests it.

## Phase 3 — MVC refactor + validation

Only after confirmation:

1. Plan target structure from `mvc-guidelines.md` adapted to the stack (Flask blueprints / Express routers / equivalent).
2. Apply transformations from `refactor-playbook.md` for each confirmed finding of CRITICAL/HIGH (and MEDIUM when safe).
3. Preserve public API surface (same routes/methods/status codes unless a security fix requires tightening and you document it).
4. Extract config (no secrets in source); introduce Models, Controllers/Services, Views/Routes; centralize error handling; keep a clear composition-root entrypoint.
5. Validate:
   - App boots without errors
   - Health / key endpoints still respond
   - Re-scan: no remaining CRITICAL from the original set (or document residual with justification)
6. Print:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree>

## Validation
  ✓/✗ Application boots without errors
  ✓/✗ All endpoints respond correctly
  ✓/✗ Critical anti-patterns addressed
================================
```

## Agnosticism rules

- Never hardcode Python-only or Node-only steps in the control flow; branch on detected stack.
- Prefer semantic smells (God Class, SQLi, hardcoded secrets) over language trivia.
- For partially layered projects (e.g. existing `models/` + `routes/`), improve in place — do not force a full rewrite if MVC-ish structure already exists; fix smells and clarify boundaries.
