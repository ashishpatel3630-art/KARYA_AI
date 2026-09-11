# KARYA AI

> **A Sovereign AI Employee for Confidential Industrial Work**

KARYA is an on-premise, privacy-first Agentic AI Workbench designed for organizations that work with sensitive industrial documents, engineering reports, technical diagrams, operational data, and internal knowledge.

Instead of sending confidential information to external cloud AI systems, KARYA brings **LLMs, RAG, multimodal understanding, AI agents, automation, and enterprise security into the organization's own environment.**

---

## 🚀 What is KARYA?

Modern industrial organizations generate enormous amounts of confidential information:

* Engineering reports
* Inspection documents
* Maintenance records
* SOPs and manuals
* Technical drawings
* P&IDs and diagrams
* Equipment data
* Vendor documents
* Financial and operational reports
* Internal policies
* Incident reports

Traditional AI platforms often require this information to leave the organization's infrastructure.

That creates a major problem:

> **How can an organization use powerful AI without giving its confidential data to external cloud AI providers?**

### KARYA solves this with sovereign, on-premise AI.

KARYA provides an AI workspace where organizations can:

**Upload → Understand → Retrieve → Reason → Execute → Verify**

while keeping sensitive data inside their controlled infrastructure.

---

# 🧠 Core Vision

KARYA is designed around one principle:

> **AI should work for the organization without taking the organization's data outside its security boundary.**

The platform combines:

* Local / on-premise LLM inference
* Retrieval-Augmented Generation
* Multimodal document understanding
* OCR
* Vision models
* AI agents
* Tool calling
* MCP
* Workflow automation
* Secure authentication
* Role-based authorization
* Auditability
* Sandboxed execution
* Background workers
* Persistent storage

---

# ✨ Key Capabilities

## 1. Sovereign AI

Run AI workloads inside the organization's own environment.

Sensitive documents do not need to be uploaded to external AI services.

---

## 2. Enterprise RAG

KARYA can transform organizational documents into searchable knowledge.

Typical pipeline:

```text
Document
   ↓
Parsing
   ↓
Chunking
   ↓
Embedding
   ↓
Vector Storage
   ↓
Semantic Retrieval
   ↓
Context Construction
   ↓
Local LLM
   ↓
Grounded Answer
```

The goal is to provide answers based on organizational knowledge rather than unsupported model memory.

---

## 3. Multimodal Understanding

Industrial information is not always plain text.

KARYA is designed to work with:

* Text
* PDFs
* Tables
* Images
* Technical diagrams
* Scanned documents
* Engineering drawings
* Visual information

The AI engine contains dedicated areas for OCR, vision, documents, models, RAG and orchestration.

---

## 4. AI Employees

Instead of using AI only as a chatbot, KARYA introduces the concept of an **AI Employee**.

An AI Employee can:

```text
Understand a task
      ↓
Analyze available knowledge
      ↓
Retrieve relevant information
      ↓
Reason about the problem
      ↓
Use tools
      ↓
Execute actions
      ↓
Verify results
      ↓
Return an auditable response
```

---

## 5. Agentic AI

KARYA is designed to move beyond simple prompt → response systems.

Agents can coordinate:

* Knowledge retrieval
* Tool usage
* Planning
* Reasoning
* Task execution
* Validation
* Workflow steps

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      KARYA UI       │
                         │ React + Tailwind    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI API      │
                         │ Auth / RBAC / APIs  │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │  AI Engine   │  │ MCP / Tools  │  │   Workers    │
          └──────┬───────┘  └──────────────┘  └──────┬───────┘
                 │                                    │
       ┌─────────┼──────────┐                         │
       ▼         ▼          ▼                         ▼
     LLM       RAG       Vision                 Background Jobs
       │         │          │
       │         ▼          │
       │     Embeddings     │
       │         │          │
       └─────────┼──────────┘
                 ▼
        ┌───────────────────┐
        │ Secure Storage    │
        │ PostgreSQL/Redis  │
        │ Documents/Vector  │
        └───────────────────┘
```

---

# 📁 Repository Structure

```text
KARYA_AI/
│
├── Database/
│
├── Docker/
│
├── ai_engine/
│   ├── agents/
│   ├── config/
│   ├── conversations/
│   ├── documents/
│   ├── evaluation/
│   ├── llm/
│   ├── models/
│   ├── ocr/
│   ├── orchestrator/
│   ├── rag/
│   ├── router/
│   ├── sandbox/
│   ├── tools/
│   ├── utils/
│   └── vision/
│
├── backend/
│   ├── app/
│   ├── migrations/
│   └── tests/
│
├── frontend/
│
├── mcp/
│
├── storage/
│
├── tests/
│
└── workers/
```

---

# 🧩 System Components

| Component   | Responsibility                                              |
| ----------- | ----------------------------------------------------------- |
| `frontend`  | KARYA user interface                                        |
| `backend`   | API, authentication, authorization and application services |
| `ai_engine` | LLM, RAG, agents, OCR, vision and orchestration             |
| `Database`  | Database-related infrastructure                             |
| `mcp`       | Model Context Protocol integrations                         |
| `storage`   | Document and application storage                            |
| `workers`   | Background processing                                       |
| `tests`     | System and integration testing                              |
| `Docker`    | Containerized deployment                                    |

The current repository confirms these major top-level components.

---

# ⚙️ Technology Stack

## Frontend

* React
* Vite
* Tailwind CSS
* JavaScript / JSX
* Modern component architecture

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis
* Alembic
* JWT authentication

## AI

* Local / open-weight LLMs
* RAG
* Embeddings
* Vector retrieval
* OCR
* Vision models
* Agent orchestration
* Tool calling

## Infrastructure

* Docker
* Redis
* PostgreSQL
* Local model runtime
* Background workers

---

# 🔐 Security

Security is a core part of KARYA rather than an afterthought.

The backend includes dedicated application, migration and testing layers.

KARYA is designed around:

* Authentication
* Authorization
* Role-based access control
* JWT-based sessions
* Token rotation
* Password security
* Brute-force protection
* Rate limiting
* Audit logging
* Security headers
* Request tracing
* Suspicious activity detection
* MFA support
* Secure password recovery

---

# 🔎 Knowledge Pipeline

```text
                 USER
                   │
                   ▼
             Upload Document
                   │
                   ▼
            Document Parser
                   │
                   ▼
              OCR / Vision
                   │
                   ▼
                Chunking
                   │
                   ▼
               Embeddings
                   │
                   ▼
             Vector Storage
                   │
                   ▼
             Semantic Search
                   │
                   ▼
             Context Builder
                   │
                   ▼
                Local LLM
                   │
                   ▼
           Grounded Response
                   │
                   ▼
               Citations
```

---

# 🤖 Agent Pipeline

```text
User Request
     │
     ▼
Intent Detection
     │
     ▼
Agent Router
     │
     ▼
Planning
     │
     ├───────────────┐
     ▼               ▼
Knowledge          Tools
Retrieval          / MCP
     │               │
     └───────┬───────┘
             ▼
          Reasoning
             │
             ▼
          Execution
             │
             ▼
         Verification
             │
             ▼
           Result
```

---

# 🎯 Example Use Cases

### Industrial Operations

Ask:

> "What was the last recorded temperature of Compressor C-101?"

KARYA searches the organization's approved knowledge base and returns a grounded answer with its source.

### Maintenance

> "Show previous maintenance records for Pump P-204."

### Engineering

> "Explain the relationship between these components in this diagram."

### Safety

> "Find all inspection reports mentioning abnormal pressure."

### Management

> "Summarize the major operational issues reported this month."

---

# 🖥️ Product Modules

KARYA is designed as a complete AI workbench rather than a single chatbot.

Core product areas include:

* Dashboard
* AI Employees
* Workflows
* Tasks
* Knowledge
* Ask KARYA
* Authentication
* Settings
* Security
* Administration

---

# 🔌 MCP

KARYA includes an MCP layer for connecting AI agents with external or internal tools.

Conceptually:

```text
AI Agent
   │
   ▼
MCP
   │
   ├── Internal APIs
   ├── Databases
   ├── Industrial Tools
   ├── File Systems
   └── Enterprise Services
```

This allows KARYA agents to move from **answering questions** to **performing controlled actions**.

---

# ⚡ Local-First AI

A major architectural principle of KARYA is local-first execution.

```text
             INTERNET
                 X
                 │
        ┌────────┴────────┐
        │     KARYA       │
        │                 │
        │ Local LLM       │
        │ Local RAG       │
        │ Local Storage   │
        │ Local Agents    │
        │ Local Tools     │
        │ Local Database  │
        └─────────────────┘
```

This architecture is particularly suitable for environments where confidentiality, network isolation and data sovereignty are important.

---

# 🚀 Getting Started

## Clone

```bash
git clone https://github.com/ashishpatel3630-art/KARYA_AI.git
cd KARYA_AI
```

---

# Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Configure environment variables:

```bash
cp .env.example .env
```

Run database migrations:

```bash
alembic upgrade head
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🐳 Docker

KARYA also contains Docker-related infrastructure for reproducible deployment.

Example:

```bash
docker compose up --build
```

---

# 🧪 Testing

Run backend tests:

```bash
cd backend
pytest
```

Run the broader test suite:

```bash
pytest
```

Tests are maintained both inside the backend and at the repository level.

---

# 📊 Engineering Principles

KARYA follows several important engineering principles:

### Privacy First

Confidential information should remain within the organization's controlled environment.

### Modular AI

LLMs, RAG, vision, OCR, agents and tools should remain independently replaceable.

### Security by Design

Authentication, authorization, auditing and isolation are architectural concerns.

### Grounded AI

AI responses should be connected to trusted organizational knowledge whenever possible.

### Human Control

AI agents should operate within defined permissions and controlled tool boundaries.

### Observable Systems

Important operations should be traceable and auditable.

---

# 🗺️ Roadmap

* [x] KARYA frontend
* [x] FastAPI backend
* [x] Authentication
* [x] Authorization / RBAC
* [x] PostgreSQL integration
* [x] Redis integration
* [x] AI engine foundation
* [x] RAG architecture
* [x] MCP foundation
* [x] Worker architecture
* [ ] Production-grade agent orchestration
* [ ] Advanced multimodal RAG
* [ ] Enterprise workflow automation
* [ ] Advanced observability
* [ ] On-premise deployment packages
* [ ] Kubernetes deployment
* [ ] Enterprise SSO
* [ ] Advanced policy engine

---

# 🏆 Hackathon

KARYA is developed for:

**Smart India Hackathon — Problem Statement SIH26117**

### Team

**The Bug Busters**

KARYA focuses on building a secure, sovereign AI workbench for confidential industrial environments.

---

# 📜 License

License information will be added as the project reaches its release stage.

---
# ⭐ Vision

KARYA is not intended to be another generic AI chatbot.

The long-term vision is:

> **An AI employee that can understand organizational knowledge, reason about complex industrial problems, use authorized tools, execute workflows, and operate securely inside the organization's own infrastructure.**

**KARYA — AI that works where your data lives.**
