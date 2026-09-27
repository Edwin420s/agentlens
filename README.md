# AgentLens

AgentLens is an AI-agent reliability and observability platform built for detecting semantic workflow failures that ordinary error logs miss. It analyzes agent sessions for subtle failure signals, groups recurring failures into actionable patterns, links conclusions to verifiable event evidence, and provides an evidence-grounded investigation assistant.

## Architecture

- **Backend**: FastAPI + Pydantic v2 + Motor / PyMongo Async + MongoDB
- **Frontend**: React + Vite SPA
- **AI**: Groq (Llama-3.3-70B) or Google Gemini (1.5-Flash / 2.5-Flash) with graceful offline fallback
- **Deterministic Rule Engine**: 9-signal safety baseline with legitimate-retry suppression
- **Evaluation Isolation**: Ground-truth labels are stored in an isolated `evaluation_labels` collection and never leak into session analysis documents

## Repository Structure

```
AgentLens/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # REST routers (9 routers, versioned under /api/v1)
│   │   ├── ai/               # Multi-provider abstraction (Groq, Gemini, offline fallback)
│   │   ├── db/               # Motor MongoDB client, indexes & repositories
│   │   ├── schemas/          # Strict Pydantic v2 schemas & enums
│   │   └── services/         # Rule engine, session classifier, failure builder, assistant, etc.
│   ├── data/                 # 100-session synthetic NovaCart dataset & demo fixtures
│   ├── scripts/              # Seed, reset, generate demo, and evaluation scripts
│   ├── tests/                # Pytest unit & integration test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/                 # React + Vite frontend application
│   ├── src/                  # React components, styles & API client
│   ├── public/               # Public assets and demo dataset
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
# With virtualenv active:
pip install -r requirements.txt
cp .env.example .env

# Optional: Add GROQ_API_KEY or GEMINI_API_KEY to .env

# Generate 100-session NovaCart dataset & seed database:
python -m scripts.generate_demo
python -m scripts.seed_demo

# Run server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## Evaluation & Benchmarks

Run the evaluation script to calculate precision, recall, confusion matrix, and per-failure-type metrics against the isolated evaluation labels:

```bash
cd backend
python -m scripts.run_evaluation INV-0001
```

## Automated Tests

Run the backend test suite:

```bash
cd backend
pytest -v
```
