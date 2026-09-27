# AgentLens

> **Finding the Hidden Failures in Autonomous AI Agent Workflows**  
> *Developed for the GOMYCODE Hackathon 2026 — SupplyzPro Smart Operations Award Track*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Async-47A248?logo=mongodb&logoColor=white)](https://mongodb.com)
[![Tests](https://img.shields.io/badge/Tests-11%20Passed%20(100%25)-success)](backend/tests/)
[![Evaluation](https://img.shields.io/badge/Recall-100%25%20(F1%200.963)-blueviolet)](docs/SYSTEM_GUIDE.md)

---

## What Is AgentLens?

AgentLens is an AI-agent reliability and investigation platform built to detect **silent semantic failures** that ordinary infrastructure logs completely miss.

The fundamental premise is simple:
> **An AI agent can report HTTP 200 and say "Task completed successfully" while failing the customer in reality.**

AgentLens analyzes multi-turn conversational traces and tool invocations, uncovers behavioral failure patterns, links findings to concrete chronological evidence, groups recurring issues into semantic clusters, and guides developers on what to investigate first.

---

## The SupplyzPro Challenge: "Find the Hidden Failures"

In autonomous supply chain and customer operations, agents frequently interact with backend APIs (inventory, ordering, refunds, logistics). When tools fail or return unexpected data, poorly guarded agents often:
- Hallucinate success to the customer without completing the backend action.
- Update or query the wrong customer order.
- Enter infinite retry loops without making progress.
- Repeatedly ask the customer for information they already provided.
- Prematurely terminate multi-part requests.

**AgentLens directly solves this challenge** by introducing an automated dual-layer detection pipeline:
1. **Deterministic Rule Engine**: 9 behavioral signals evaluated across complete execution sequences.
2. **AI Semantic Hypothesis Generator**: Pluggable Groq (Llama-3.3-70B) or Google Gemini intelligence that translates raw event traces into actionable engineer recommendations.

---

## The 5 Core Failure Archetypes

| Failure Archetype | Description | Real-World Example |
| :--- | :--- | :--- |
| **Unsupported Success** | Agent claims success, but tool execution failed or was omitted | Agent says *"Order cancelled and refunded"* after `cancel_order` threw a lock error |
| **No Progress** | Agent consumes execution turns looping without moving toward the goal | Running redundant `search_item` calls with identical parameters 4 times |
| **Wrong Record** | Agent interacts with an incorrect customer, order, or SKU | Customer asks about `ORD-20015`; agent queries and modifies `ORD-20091` |
| **Repeated Question** | Agent asks the user for information already provided earlier | Asking *"What is your email?"* three turns after the user already gave it |
| **Incomplete Request** | Agent resolves one sub-task but abandons the remaining intent | User asks to update address and cancel item; agent only changes address and finishes |

### Intelligent Edge Case Handling
- **Legitimate Retries (`legitimate_retry_success`)**: When a tool transiently fails (e.g. temporary database timeout) but the agent successfully retries and completes the task, AgentLens recognizes this recovery and suppresses false alarms.
- **Ambiguous Runs**: When session evidence is incomplete, AgentLens marks the session as `Ambiguous` and recommends human review rather than fabricating a conclusion.

---

## System Architecture

```
[ User Interaction ] ───► [ React 19 / Vite SPA Console ]
                                    │ (REST / JSON)
                                    ▼
                         [ FastAPI Backend API ]
                                    │
    ┌───────────────────────────────┴──────────────────────────────┐
    ▼                                                              ▼
[ Deterministic Rule Engine ]                     [ Multi-Provider AI Layer ]
(9 Signals, Sequence Validator)                   (Groq Llama-3.3 / Gemini)
    │                                                              │
    └───────────────────────────────┬──────────────────────────────┘
                                    ▼
               [ MongoDB (Motor Async, Compound Indexes) ]
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
   [ Operational Collections ]             [ Evaluation Labels ]
(Sessions, Events, Failures, Groups)           (Strictly Isolated)
```

---

## Evaluation Benchmark & Accuracy

AgentLens was benchmarked against the **NovaCart 100-Session Benchmark Dataset**:
- **Dataset Composition**: 65 Normal Successes, 7 Legitimate Retries, 8 Unsupported Successes, 6 No-Progress Loops, 5 Wrong Records, 4 Repeated Questions, 3 Incomplete Requests, and 2 Ambiguous Runs.

### Confusion Matrix & Metrics
```
Confusion Matrix:
- True Positives (TP):   26
- False Positives (FP):   2
- False Negatives (FN):   0  <-- Zero silent failures missed!
- True Negatives (TN):   72

Key Metrics:
- Precision:   92.86%
- Recall:     100.00%
- F1 Score:     0.963
```

---

## Concurrency & High-Load Stress Testing

AgentLens was tested under simultaneous multi-user stress testing against live endpoints:
- **Simultaneous Users**: 100 concurrent worker threads
- **Total Requests**: 500 requests across dashboard, failure groups, sessions, timelines, and assistant queries
- **Success Rate**: **100.00% (0 dropped or failed requests)**
- **Throughput**: **189.2 requests / second**
- **Average Latency**: **447.6 ms** (95th percentile: 1022 ms)

---

## Repository Structure

```
AgentLens/
├── backend/
│   ├── app/
│   │   ├── api/routers/      # REST API endpoints (health, investigations, sessions, failures, groups, assistant, export, eval)
│   │   ├── ai/               # Multi-provider abstraction (Groq, Gemini, deterministic fallback)
│   │   ├── db/               # Motor MongoDB client, compound unique indexes & repositories
│   │   ├── schemas/          # Strict Pydantic v2 schemas and enums
│   │   └── services/         # Rule engine, session classifier, failure builder, assistant, export
│   ├── data/                 # 100-session synthetic NovaCart dataset & demo fixtures
│   ├── scripts/              # Seed, reset, generate demo, and evaluation scripts
│   ├── tests/                # Pytest unit & integration test suite (11/11 passing)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/       # OverviewDashboard, FailureGroupsView, SessionTimeline, AssistantView, EvaluationView
│   │   ├── api.js            # Frontend REST API client
│   │   ├── main.jsx          # React 19 application entrypoint
│   │   └── styles.css        # Clean, modern enterprise CSS
│   ├── public/               # Public assets & standalone demo dataset
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── SUBMISSION.md         # Complete GOMYCODE Hackathon submission form guide
│   ├── DEMO_SCRIPT_90S.md    # Second-by-second 90-second video demo recording script
│   ├── PRESENTATION.md       # 10-slide presentation deck outline
│   └── SYSTEM_GUIDE.md       # Detailed plain-English architecture and workflow guide
└── README.md
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+ (running locally on `localhost:27017` or via Docker)

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# (Optional: Add GROQ_API_KEY or GEMINI_API_KEY to .env for live LLM features)

# Seed database with the 100-session NovaCart benchmark dataset
python -m scripts.generate_demo
python -m scripts.seed_demo

# Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`.  
Interactive Swagger docs: `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Automated Testing & Verification

Run the comprehensive pytest suite:
```bash
cd backend
pytest -v
```
*(All 11 tests pass in ~1.7 seconds).*

Run the 20-point end-to-end security and system verification test suite:
```bash
PYTHONPATH=backend python3 path/to/security_and_frontend_e2e.py
```

---

## Security & Responsible AI

- **Zero Ground-Truth Leakage**: Benchmark evaluation labels are stored in an isolated collection (`evaluation_labels`) and never exposed to the session, failure, or AI endpoints.
- **Strict Validation**: All API payloads enforce regex constraints, ISO UTC timestamps, and strict Pydantic v2 schemas.
- **NoSQL Injection Resistance**: All query parameters are strictly typed and sanitized before reaching PyMongo filters.
- **Memory-Only Streaming Exports**: Exported CSV and JSON files are buffered in-memory (`io.StringIO`), completely eliminating filesystem path traversal risks.
- **Safe Error Envelopes**: All exceptions return structured JSON error envelopes with zero internal stack traces or secrets leaked.
- **Synthetic Data**: 100% of customer names, orders, and traces are synthetic; zero private enterprise or personal data is used.

---

## GOMYCODE Hackathon Documentation Links

- [Official Submission Form Answers](docs/SUBMISSION.md)
- [90-Second Demo Video Script](docs/DEMO_SCRIPT_90S.md)
- [10-Slide Presentation Deck Outline](docs/PRESENTATION.md)
- [Plain-English Architecture & Workflow Guide](docs/SYSTEM_GUIDE.md)

---

## License

MIT License. Built with pride for the GOMYCODE Hackathon 2026.
