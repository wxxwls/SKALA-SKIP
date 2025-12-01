# CLAUDE.md

This file defines **rules and guardrails for Claude Code** when working on the **FastAPI AI backend** in this repository.

The FastAPI code is the **AI-only backend layer** of the system.  
Directory names under `app/` are **fixed and MUST NOT be renamed**.  
You MAY add new files and subdirectories *inside* these fixed directories, but you must preserve the top-level layout.

---

## 1. Project Overview

### 1.1 System Context

The overall system consists of:

- **Frontend**: Vue 3 SPA
- **Business Backend**: Spring Boot (Port 8080)
- **AI Backend**: FastAPI (Port 8000)
- **RDBMS**: PostgreSQL (used only by Spring Boot)
- **Vector DB**: Qdrant/Chroma (used only by FastAPI)
- **LLM / Embedding Models**: external or internal LLM endpoints

FastAPI is responsible for AI-related work only:

- Creating embeddings and managing VectorDB for ESG / sustainability documents and news
- RAG-based ESG Q&A
- Topic modeling and sentiment analysis for ESG issue pool construction
- Drafting sustainability report sections with AI
- Carbon / emissions related AI signals (advisory, not trading engine)

> **Core idea**  
> FastAPI performs **AI computation, retrieval, and generation**.  
> **All business logic, persistence, authentication, and public APIs belong to Spring Boot.**

---

## 2. Architecture Rules (MUST)

These rules must never be broken by generated code.

### 2.1 Network and Ports

- **FastAPI**
  - Port: `8000`
  - Not directly exposed to browsers or external clients
  - Called only from Spring Boot (Port `8080`) over an internal network
- FastAPI endpoints use an **internal prefix**, for example:
  - `/internal/v1/...`

> **RULE F-ARCH-001**  
> FastAPI endpoints are **never called directly by the frontend or outside systems**.  
> The call chain is always: `Vue 3 SPA → Spring Boot (8080) → FastAPI (8000)`.

### 2.2 Responsibility Split (Spring Boot vs FastAPI)

**Spring Boot (8080) – Business & Data Layer**

- Exposes public API: `/api/v1/**`
- Handles login, authentication, authorization, users, orgs
- Is the **only** component that talks to PostgreSQL
- Manages all structured data:
  - Issue pool, surveys, double materiality, report metadata, news metadata, etc.
- Orchestrates calls to FastAPI and persists results

**FastAPI (8000) – AI & ML Layer**

- Creates embeddings and stores/queries them in VectorDB
- Executes RAG-based ESG Q&A
- Performs topic modeling and sentiment analysis for ESG issues
- Generates AI drafts of report sections
- Runs AI-based analysis jobs for news, carbon, etc.

> **RULE F-ARCH-002**  
> FastAPI must **never connect directly** to PostgreSQL, authentication servers, or any Spring-specific component.  
> If persistent data is needed, Spring Boot must load it first and send it to FastAPI as input.

---

## 3. Allowed vs Forbidden Dependencies

### 3.1 Allowed (FastAPI may access directly)

Within FastAPI code, it is allowed to:

- Connect to VectorDB (Qdrant, Chroma, etc.)
- Call LLM and embedding model APIs
- Use object storage (S3-compatible) for temporary document/section storage
- Call external public/paid APIs (carbon prices, ESG news APIs, etc.)
- Use local temporary disk for cache / temporary files (no long-term storage of sensitive data)

### 3.2 Forbidden (FastAPI must NOT access directly)

Claude must NOT write code that directly connects to:

- PostgreSQL, MySQL, or any RDBMS
  - No ORM (SQLAlchemy, etc.) for real DB persistence
- Spring Security or any auth server
  - No JWT/session verification or auth flows in FastAPI
- Redis as a session store
- Any other service that Spring Boot is explicitly responsible for

> **RULE F-DATA-001**  
> FastAPI receives **already-loaded input data** from Spring Boot as JSON,  
> performs AI / ML computation (embedding, RAG, analysis, generation),  
> and returns results.  
> Any DB **save/update/delete** must be done by Spring Boot.

---

## 4. Code Structure Guidelines

### 4.1 Fixed Directory Layout

The following directories under `fastapi/app` are **fixed and MUST NOT be renamed or removed**:

```text
app/
  main.py
  core/
  api/
  services/
  ai/
  infra/
  jobs/
  tests/
```

- The directory names above are **contractual**.
- You may add **new subdirectories and files inside** these, but:
  - Do NOT rename `core`, `api`, `services`, `ai`, `infra`, `jobs`, or `tests`.
  - Do NOT move their responsibilities elsewhere.

### 4.2 Layer Responsibilities

The exact file names are flexible (as long as they match Python norms), but the **layering rules** must hold:

- `app/main.py`
  - FastAPI application entry point
  - Registers routers, middleware, and lifecycle hooks (`on_startup`, `on_shutdown`)

- `app/core/`
  - Configuration (settings, environment)
  - Logging setup
  - Global error/exception handling
  - Dependency injection (common Depends helpers)

- `app/api/`
  - FastAPI routers (HTTP layer)
  - Pydantic request/response models
  - NO direct calls to LLMs, VectorDB, S3, or external services  
    (delegate these to services / AI / infra)

- `app/services/`
  - Domain-level services (use cases):
    - RAG orchestration
    - Issue pool AI analysis
    - Report draft generation
    - News sentiment pipeline
    - Carbon signal generation
  - Compose `ai/` and `infra/` modules

- `app/ai/`
  - Pure AI logic:
    - LLM clients
    - Embedding clients
    - RAG pipelines
    - Topic modeling
    - Sentiment analysis
  - Should not depend on HTTP or FastAPI directly

- `app/infra/`
  - Infrastructure adapters:
    - VectorDB clients
    - S3 / object storage clients
    - External HTTP API clients (carbon, news, etc.)
  - Encapsulate low-level details

- `app/jobs/`
  - Batch/cron jobs:
    - News refresh
    - Embedding refresh
    - Carbon data refresh
  - Typically executable as scripts or via a scheduler

- `app/tests/`
  - pytest-based tests (unit + integration)

> **RULE F-LAYER-001**  
> Always maintain the hierarchy: **API → Service → AI / Infra**.  
> Never mix HTTP handling, business orchestration, and low-level AI/infra calls in a single file.

---

## 5. API Design Rules (FastAPI Side)

### 5.1 Endpoint Patterns

- Base path is internal-only, for example:
  - `/internal/v1/issue-pool/...`
  - `/internal/v1/rag/...`
  - `/internal/v1/reports/...`
  - `/internal/v1/news/...`
  - `/internal/v1/carbon/...`

- HTTP methods:
  - `POST` for:
    - Running AI analyses
    - RAG queries
    - Report draft generation
  - `GET` for:
    - Health checks
    - Simple status/config reads

> **RULE F-API-001**  
> FastAPI should expose **“operation-style” endpoints** (run analysis, generate draft, run RAG).  
> Resource-style CRUD (`GET/POST/PUT/DELETE /things/{id}`) belongs to Spring Boot.

### 5.2 Spring Boot ↔ FastAPI Contract

- Spring Boot:
  - Prepares all needed input data (texts, IDs, metadata)
  - Sends it to FastAPI as JSON via internal HTTP
- FastAPI:
  - Returns AI/ML results only:
    - Drafts, summaries, RAG answers
    - Topic clusters and scores
    - Sentiment labels and scores
    - Embedding/vector keys or references

JSON schemas should remain consistent with higher-level documentation (`api.md`, `srs.md`, `fsd.md`, etc.). When adding new fields, add comments that higher-level specs must be updated.

---

## 6. AI / RAG / NLP Implementation Guidelines

### 6.1 Embeddings & VectorDB

FastAPI typically:

1. Receives raw texts (documents, news, issues, etc.) from Spring Boot.
2. Generates embeddings using an embedding model.
3. Stores or updates vectors in VectorDB.
4. Performs similarity search for RAG and analysis.

Implementation guidelines:

- Model names and endpoints must come from configuration, not hard-coded strings.
- Collection names and VectorDB schema should be managed via constants or config modules.

### 6.2 RAG-Based Q&A

Typical processing steps:

1. Receive user question (and optional context) from Spring Boot.
2. Perform VectorDB search to retrieve top-k relevant documents/snippets.
3. Build a prompt that includes:
   - System role (ESG expert, sustainability advisor, etc.)
   - Retrieved context snippets
   - Clear instruction on output format and constraints
4. Call LLM to generate the answer.
5. Return both:
   - The answer text
   - The list of sources (document IDs, titles, scores, etc.)

Guidelines:

- Prefer answer formats that include source references so the UI can show “where it came from”.
- Prompt building should be encapsulated in dedicated helpers or classes, not in routers.

### 6.3 Issue Pool, Topic Modeling, Sentiment

FastAPI is responsible for:

- Topic modeling / clustering of ESG-related texts.
- Suggesting an issue pool with scores (e.g., top 20 candidate issues).
- Sentiment analysis of news or stakeholder texts (POSITIVE / NEGATIVE / NEUTRAL + numeric score).

Spring Boot then:

- Stores the suggested issues and scores.
- Allows users to confirm, edit, or reject these suggestions.
- Uses them in double materiality workflows and reports.

> **RULE F-DOMAIN-001**  
> FastAPI provides **“candidates and scores”**,  
> but **never decides final business outcomes**.  
> Final acceptance, rejection, and persistence is always handled by Spring Boot.

### 6.4 Report Section Drafts

FastAPI:

- Receives:
  - Issue pool and double materiality results
  - Previous year’s report text
  - Relevant news and documents summaries
- Generates:
  - Section-level AI drafts
  - Optional metadata about sources used

Guidelines:

- Prompts should clearly define:
  - Tone and style for sustainability reports
  - Structure (headings, bullet points, narrative)
  - Compliance with ESG standards, where applicable
- Prefer deterministic or low-temperature settings when reproducibility is important.

---

## 7. Coding Style & Quality

### 7.1 Python / FastAPI Style

- Target Python 3.11+
- Use type hints consistently:
  - Function parameters and return types
  - Pydantic models
- Use `async def` for endpoints and I/O-heavy operations where possible.
- Separate concerns:
  - No business logic in `main.py`
  - Minimize logic in routes; delegate to services.

### 7.2 Errors and Exceptions

- Define central exception types in `core` (for example):
  - `DomainError`
  - `ExternalServiceError`
  - `ValidationError`
  - `LLMError`
- Use FastAPI exception handlers for consistent HTTP responses.
- Do not expose sensitive internal details in error messages.

### 7.3 Tests

- Use `pytest` for tests under `app/tests/`.
- Minimum expectations:
  - Unit tests for service layer.
  - Integration tests for RAG pipelines with mocked LLMs.
- External APIs (LLM, VectorDB, HTTP services) should be mocked/stubbed in CI.

---

## 8. Logging & Observability

When adding logs:

- Use a consistent logger from `core/logging` (or similar).
- Include a trace or correlation ID (e.g. `X-Trace-Id`) when available.
- Log:
  - Request start/end for important operations
  - LLM, VectorDB, and external API call durations
- Never log sensitive raw content (e.g., entire internal documents or KPIs).  
  Log only IDs or short summaries where needed.

---

## 9. Security & Data Privacy

- Treat all internally generated data as potentially sensitive.
- When calling external LLM APIs:
  - Minimize content sent; avoid full raw internal documents when possible.
  - Prefer summarized or anonymized content.
- Secrets (API keys, tokens, passwords) must:
  - Come from environment variables or secret stores.
  - Never be hard-coded in the repository.

---

## 10. How Claude Should Behave in This Repo

When Claude Code works in this repository on FastAPI code:

1. **Recall the role and constraints**  
   - “This is an AI-only layer. I must not handle DB or auth.”

2. **Respect the fixed directory layout**  
   - Keep the existing top-level directories under `app/`:
     - `main.py`, `core/`, `api/`, `services/`, `ai/`, `infra/`, `jobs/`, `tests/`
   - Add new subdirectories/files *inside* these as needed, but do not rename or remove them.

3. **Maintain the layering**  
   - Handle HTTP in `api/`, orchestration in `services/`, AI logic in `ai/`, infra in `infra/`.

4. **Align with higher-level specs**  
   - When adding new endpoints or fields, keep in mind they should align with `srs.md`, `fsd.md`, `architecture.md`, and `api.md`.
   - If a new behavior is introduced, make it clear in comments that the specs should be updated.

5. **Prefer clarity and separation over cleverness**  
   - Write readable, well-structured code that future humans (and AIs) can understand.

This file exists to ensure the FastAPI layer **stays as a clean, well-bounded AI backend**,  
even as the codebase grows and as tools like Claude Code help generate more code.
