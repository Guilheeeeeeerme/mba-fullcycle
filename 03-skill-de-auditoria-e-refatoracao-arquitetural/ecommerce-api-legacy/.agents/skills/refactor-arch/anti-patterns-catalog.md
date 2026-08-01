# Anti-pattern catalog (minimum 8 + deprecated APIs)

Use these signals across stacks. Severity may escalate with exploitability.

## 1. Hardcoded credentials / secrets — CRITICAL

**Signals:** literal `SECRET_KEY`, API keys (`pk_live_`, `sk_`), DB passwords, SMTP passwords, payment gateway keys in source.

**Why:** credential leak; breaks 12-factor config.

## 2. SQL injection / unsafe query construction — CRITICAL

**Signals:** string concat / f-strings / `+` into SQL; `execute("... " + user_input)`; raw query from request body (`sql` field); unsafe `eval` of query text.

**Why:** data exfiltration / destruction.

## 3. God Class / God Module — CRITICAL

**Signals:** one class/file owns DB lifecycle, routing, business rules, payments, caching; hundreds of lines spanning domains.

**Why:** untestable; any change risks everything.

## 4. Broken authentication / weak crypto — CRITICAL / HIGH

**Signals:** plaintext passwords; MD5/SHA1 for passwords; custom “crypto” loops; passwords returned in JSON serializers; default passwords in seeds used as production pattern.

**Why:** account takeover.

## 5. Fat controller / business logic in routes — HIGH

**Signals:** route handlers with multi-step workflows, pricing, inventory, nested callbacks with domain rules; models used only as dumb SQL bags while controllers do everything.

**Why:** violates MVC SRP; hard to reuse/test.

## 6. Global mutable state — HIGH

**Signals:** module-level mutable caches, shared counters (`totalRevenue`), process-global DB connections without pooling strategy, singletons mutated from request handlers.

**Why:** race conditions; impossible isolation in tests.

## 7. Missing input validation — MEDIUM

**Signals:** request body fields used without type/range checks; magic short field names (`usr`, `eml`, `c_id`) with only null checks.

**Why:** corrupt data; unexpected 500s.

## 8. N+1 / chatty persistence — MEDIUM

**Signals:** query inside loop over parent rows; nested `db.get`/`db.all` per item; ORM lazy loads in loops without eager load.

**Why:** latency and load under growth.

## 9. Leaky error handling / debug leaks — MEDIUM

**Signals:** bare `except:` / empty catch; stack traces to clients; admin/debug endpoints exposing secrets (`secret_key` in health/admin payloads); unauthenticated destructive routes (`reset-db`).

**Why:** ops risk + attacker foothold.

## 10. Deprecated / obsolete APIs — MEDIUM / HIGH

**Signals (examples — extend per stack):**

| Stack | Deprecated / avoid | Prefer |
| --- | --- | --- |
| Python | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| Python hashlib | `hashlib.md5` for passwords | `bcrypt` / `argon2` / `scrypt` |
| Flask | ad-hoc globals for config secrets | env + `config` object |
| Node | homemade base64 “hash” loops | `crypto.scrypt` / `bcrypt` |
| Node sqlite3 | callback pyramid in God class | promisify + layered modules |
| Express | no helmet/cors defaults when exposed | hardened middleware (context-dependent) |
| General | `SQLALCHEMY_TRACK_MODIFICATIONS` noise flags left misleading | remove / document |

Flag deprecated usage with file:line and modern equivalent.

## 11. Magic numbers / poor naming — LOW

**Signals:** unexplained literals; abbreviations (`u`, `e`, `p`, `cid`); unused imports; god helper modules mixing unrelated utilities.

**Why:** slows onboarding; hides bugs.

## 12. Duplicated domain logic — LOW / MEDIUM

**Signals:** copy-pasted CRUD blocks; repeated status maps; parallel formatters.

**Why:** drift between paths.
