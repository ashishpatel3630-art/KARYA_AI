# KARYA Backend

The KARYA backend is the application and security API layer.

It connects the frontend with the AI engine, database, authentication system, storage and background processing infrastructure.

---

## Responsibilities

The backend handles:

* REST APIs
* Authentication
* Authorization
* User management
* Sessions
* RBAC
* Security controls
* Database access
* AI requests
* Document APIs
* Task APIs
* Knowledge APIs
* Workflow APIs
* Audit operations

---

## Architecture

```text
React Frontend
      │
      ▼
   FastAPI
      │
 ┌────┼───────────────┐
 ▼    ▼               ▼
Auth  Application     AI Engine
 │    Services          │
 │                      │
 ▼                      ▼
PostgreSQL             LLM/RAG
 │
 ▼
Redis
```

---

## Directory Structure

```text
backend/
│
├── app/
│
├── migrations/
│
├── tests/
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
└── requirements.txt
```

---

# Authentication

KARYA uses token-based authentication.

Core flow:

```text
Login
  ↓
Validate Credentials
  ↓
Create Access Token
  ↓
Create Refresh Token
  ↓
Create Session
  ↓
Authenticated API Requests
```

---

# Authorization

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

KARYA uses role and permission checks to control protected operations.

---

# Security

Backend security includes:

* Password hashing
* JWT validation
* Token identifiers
* Refresh-token rotation
* Session management
* Rate limiting
* Brute-force protection
* Audit logging
* Security headers
* Request IDs
* Suspicious activity handling
* MFA support

---

# Database

PostgreSQL is used for persistent application data.

Typical responsibilities:

* Users
* Roles
* Sessions
* Authentication data
* Documents metadata
* Tasks
* Workflows
* Audit records

---

# Redis

Redis provides fast, temporary and distributed state.

Potential uses include:

* Rate limiting
* Session-related state
* Caching
* Temporary tokens
* Security counters
* Background-job coordination

---

# Migrations

Database migrations are handled through Alembic.

Run:

```bash
alembic upgrade head
```

Create a migration:

```bash
alembic revision --autogenerate -m "description"
```

---

# Development

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure:

```bash
cp .env.example .env
```

Start server:

```bash
uvicorn app.main:app --reload
```

---

# Testing

```bash
pytest
```

Security-specific tests should cover:

* JWT
* Redis
* Brute force
* Authentication
* Authorization
* Security middleware
* Sessions
