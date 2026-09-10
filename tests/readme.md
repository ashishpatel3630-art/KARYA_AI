# KARYA Tests

The `tests` directory contains system-level and integration tests for KARYA.

## Testing Goals

KARYA testing should validate:

* Authentication
* Authorization
* JWT handling
* Sessions
* Redis
* Database
* RAG
* AI engine
* API integration
* Security
* Document processing
* Agent execution

---

## Testing Layers

```text
Unit Tests
    ↓
Integration Tests
    ↓
API Tests
    ↓
AI / RAG Tests
    ↓
Security Tests
    ↓
End-to-End Tests
```

---

## Important Security Tests

Security tests should verify:

* Invalid credentials
* Expired tokens
* Refresh-token rotation
* Token reuse
* Brute-force protection
* Rate limits
* Unauthorized access
* Role restrictions
* Session invalidation
* Audit logging

---

## Running Tests

```bash
pytest
```

For verbose output:

```bash
pytest -v
```
