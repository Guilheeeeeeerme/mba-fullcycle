# MVC guidelines (target architecture)

Technology-agnostic layering. Map names to the stack idiom.

## Models

- Own persistence and domain data access
- Encapsulate queries (parameterized); no HTTP concerns
- Do not format transport DTOs mixed with SQL string building in callers
- One cohesive domain per module when practical (`produto_model`, `user_model`, …)

## Views / Routes

- HTTP/API surface only: parse request, call controller/service, return response
- No business rules, no raw SQL, no credential handling beyond passing tokens
- Framework idioms: Flask blueprints / Express routers / FastAPI routers

## Controllers (or Application Services)

- Orchestrate use cases: validate → model calls → map errors → result
- Injectable dependencies (db, clock, mailer) instead of globals
- Keep handlers thin enough to unit-test without spinning the full HTTP stack when possible

## Config

- Secrets and environment-specific values from env / config module
- Never commit live keys; provide `.env.example` when introducing env vars

## Cross-cutting

- Central error handler / middleware
- Consistent logging without dumping secrets
- Clear composition root (`app.py` / `src/app.js`) that wires layers only

## Partial-MVC projects

If folders already exist (`models/`, `routes/`, `services/`):

1. Keep the skeleton
2. Push SQL out of routes into models/repositories
3. Push workflows out of routes into controllers/services
4. Fix security smells in place
5. Only rename/move when it clarifies boundaries
