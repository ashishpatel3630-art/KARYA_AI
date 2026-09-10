# KARYA AI Engine

The `ai_engine` is the intelligence layer of KARYA.

It is responsible for transforming user requests and organizational knowledge into intelligent, grounded and actionable results.

---

## Architecture

```text
User Request
     │
     ▼
   Router
     │
     ▼
Orchestrator
     │
 ┌───┼───────────────┐
 ▼   ▼               ▼
LLM  RAG            Tools
 │    │               │
 ▼    ▼               ▼
Vision/OCR       MCP / APIs
 │    │               │
 └────┴───────┬───────┘
               ▼
             Agent
               │
               ▼
          Verification
               │
               ▼
            Response
```

---

## Modules

### `agents/`

Contains AI-agent logic.

Responsible for:

* Agent behavior
* Task execution
* Planning
* Tool usage
* Agent state

### `llm/`

LLM abstraction and model communication.

Responsible for:

* Model configuration
* Prompt handling
* Inference
* Model providers
* Response processing

### `rag/`

Retrieval-Augmented Generation.

Responsible for:

* Document retrieval
* Semantic search
* Context construction
* Grounded generation

### `documents/`

Document processing pipeline.

Handles:

* PDF
* Text
* Document extraction
* Chunking
* Metadata

### `ocr/`

Optical Character Recognition.

Used for scanned and image-based documents.

### `vision/`

Multimodal understanding.

Used for:

* Images
* Diagrams
* Visual documents
* Engineering drawings

### `models/`

AI model definitions and model configuration.

### `orchestrator/`

Coordinates multiple AI components and execution steps.

### `router/`

Determines which AI capability should process a request.

### `tools/`

Tool-calling infrastructure.

### `sandbox/`

Provides controlled execution boundaries for agent operations.

### `evaluation/`

Evaluates AI quality and system behavior.

### `conversations/`

Conversation and contextual interaction handling.

### `config/`

AI-engine configuration.

### `utils/`

Shared helper utilities.

---

## Design Principle

The AI engine should remain modular.

A model should be replaceable without rewriting the entire application.

For example:

```text
Frontend
   ↓
Backend
   ↓
AI Engine
   ↓
LLM Interface
   ↓
Local Model
```

The underlying model can evolve while the application interface remains stable.

---

## RAG Flow

```text
Documents
    ↓
Parser
    ↓
Chunker
    ↓
Embedding Model
    ↓
Vector Store
    ↓
Retriever
    ↓
Context
    ↓
LLM
    ↓
Grounded Answer
```

---

## Multimodal Flow

```text
PDF / Image / Diagram
          ↓
     Document Router
          ↓
    ┌─────┴─────┐
    ▼           ▼
   OCR        Vision
    │           │
    └─────┬─────┘
          ▼
     Structured Data
          ↓
         RAG
          ↓
         LLM
```

---

## Goal

The AI engine should provide:

* Grounded answers
* Source-aware responses
* Multimodal understanding
* Agentic execution
* Local inference
* Tool integration
* Secure execution
* Evaluation and observability
