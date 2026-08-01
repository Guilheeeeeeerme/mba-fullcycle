# Refactor playbook (≥8 before/after patterns)

Patterns are illustrative; adapt syntax to the detected stack.

## 1. Extract hardcoded secret → env config

**Before (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

**After:**
```python
import os
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
```

## 2. Parameterize SQL

**Before:**
```python
cursor.execute("SELECT * FROM usuarios WHERE id = " + str(id))
```

**After:**
```python
cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
```

## 3. Split God Class into layers

**Before:** one `AppManager` with `initDb` + `setupRoutes` + checkout + revenue.

**After:**
```
src/
  config.js
  models/course_model.js
  models/user_model.js
  controllers/checkout_controller.js
  routes/api.js
  app.js  # composition root
```

## 4. Move business logic out of route

**Before:**
```javascript
app.post('/api/checkout', (req, res) => {
  // price checks, user create, payment, enrollment...
});
```

**After:**
```javascript
app.post('/api/checkout', (req, res) => checkoutController.handle(req, res));
```

## 5. Replace weak password hashing

**Before:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

**After:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
```

## 6. Eliminate global mutable cache

**Before:**
```javascript
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```

**After:** inject a `Cache` port or request-scoped store; avoid process-wide mutable maps for domain state.

## 7. Fix N+1 with join / batch

**Before:** for each pedido, query itens, then query produto nome.

**After:** single join query or `WHERE pedido_id IN (...)` batch, map in memory.

## 8. Centralize error handling

**Before:** try/except returning ad-hoc dicts in every handler; admin route leaks `secret_key`.

**After:** middleware/`@app.errorhandler` maps domain errors → HTTP; never serialize secrets.

## 9. Deprecated datetime API

**Before:**
```python
datetime.utcnow()
```

**After:**
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

## 10. Composition root only wires

**Before:** routes import models and open DB connections inline.

**After:** `create_app()` / `buildApp()` constructs db + controllers + registers routes.
