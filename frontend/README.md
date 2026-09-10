# # KARYA Frontend

The KARYA frontend is the user-facing interface for the sovereign AI workbench.

It provides an interactive workspace for communicating with AI employees, managing knowledge, creating workflows and monitoring tasks.

---

## Technology

* React
* Vite
* Tailwind CSS
* JavaScript / JSX

---

## Product Areas

The frontend is designed around:

```text
KARYA
│
├── Dashboard
├── AI Employees
├── Workflows
├── Tasks
├── Knowledge
├── Ask KARYA
├── Authentication
└── Settings
```

---

## Frontend → Backend

The frontend communicates with the FastAPI backend.

```text
React
  │
  │ HTTP / JSON
  ▼
FastAPI
  │
  ├── Auth
  ├── Knowledge
  ├── Tasks
  ├── Workflows
  └── AI
       │
       ▼
   AI Engine
```

---

## Authentication Flow

```text
Loading
   ↓
Landing
   ↓
Login / Register
   ↓
Authentication
   ↓
Authorization
   ↓
KARYA Workspace
```

---

## Knowledge Flow

```text
Upload Document
      ↓
Frontend
      ↓
FastAPI
      ↓
Storage
      ↓
AI Processing
      ↓
RAG
      ↓
Ask KARYA
```

---

## UX Principles

The KARYA interface follows an industrial AI aesthetic:

* Dark interface
* High information density
* Clear system states
* Strong visual hierarchy
* Subtle motion
* Technical visual language
* Security indicators
* Real-time feedback
* Minimal unnecessary decoration

The goal is to make KARYA feel like an **AI operating system for industrial work**, rather than a generic chatbot.
