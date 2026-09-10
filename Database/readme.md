# KARYA Database

The `Database` directory contains database-related resources for KARYA.

## Purpose

The database layer provides persistent storage for application state and enterprise metadata.

---

## Core Responsibilities

* Persistent application data
* User data
* Authentication state
* Sessions
* Roles and permissions
* Task metadata
* Workflow metadata
* Knowledge metadata
* Audit records

---

## Database Architecture

```text
KARYA Backend
      │
      ▼
 SQLAlchemy
      │
      ▼
 PostgreSQL
      │
      ├── Users
      ├── Sessions
      ├── Roles
      ├── Permissions
      ├── Tasks
      ├── Workflows
      ├── Knowledge
      └── Audit Logs
```

---

## Principles

The database layer should provide:

* Data consistency
* Transaction safety
* Referential integrity
* Migration support
* Secure access
* Efficient indexing
* Auditable operations

PostgreSQL is the primary persistent database used by the KARYA backend.
