# Project analysis heuristics

## Language detection

| Signal | Language |
| --- | --- |
| `requirements.txt`, `pyproject.toml`, `*.py`, `Pipfile` | Python |
| `package.json`, `*.js` / `*.ts`, `yarn.lock` | JavaScript / TypeScript |
| `go.mod`, `*.go` | Go |
| `Cargo.toml`, `*.rs` | Rust |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `*.csproj`, `Program.cs` | C# / .NET |

## Framework detection

| Signal | Framework |
| --- | --- |
| `from flask import` / `Flask(` / `flask` in requirements | Flask |
| `fastapi`, `FastAPI(` | FastAPI |
| `django`, `DJANGO_SETTINGS_MODULE` | Django |
| `express()`, `require('express')`, `"express"` in package.json | Express |
| `nestjs`, `@nestjs/core` | NestJS |
| `gin.Default`, `fiber.New` | Gin / Fiber |

Read version pins from lockfiles / requirements when available.

## Database detection

- Imports / deps: `sqlite3`, `psycopg`, `sqlalchemy`, `mongoose`, `prisma`, `typeorm`, `sequelize`, `knex`
- Connection strings / URIs in config
- Migrations / schema SQL / ORM models → list table/entity names
- In-memory (`:memory:`) vs file vs remote

## Architecture mapping

Inspect directory layout and entrypoints:

1. **Flat monolith** — few files at root; routes + SQL + domain mixed → note “no layer separation”
2. **God module** — one class/file owns DB init, routes, business, payments
3. **Partial layers** — `models/`, `routes/`, `services/` exist but boundaries leak (SQL in routes, secrets in services)
4. **MVC-ish** — clear models / views-or-routes / controllers with composition root

Record:

- Entrypoint (`app.py`, `src/app.js`, `main.ts`, …)
- Route registration style (decorators, `add_url_rule`, `app.get`, blueprints, routers)
- Where validation, auth, persistence, and presentation live today

## Domain inference

From route names, model names, README, seeds:

- ecommerce / products / orders / users
- LMS / courses / enrollments / checkout
- task manager / tasks / categories
- other: summarize in one short phrase

## Source file inventory

Count analyzable source files. Exclude: `node_modules/`, `.venv/`, `venv/`, `dist/`, `build/`, `.git/`, lockfile-only trees, binary assets.
