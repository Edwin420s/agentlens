# AgentLens Backend

AI Agent Failure Detection & Investigation Platform.

## Quick Start

```bash
cp .env.example .env
# fill GROQ_API_KEY or GEMINI_API_KEY

docker compose up --build
# or locally:
pip install -r requirements.txt
python -m scripts.seed_demo
uvicorn app.main:app --reload
```

## API

Base path: `/api/v1`

- `GET /health`
- `POST /api/v1/datasets/import`
- `GET /api/v1/datasets`
- `GET /api/v1/investigations`
- `GET /api/v1/investigations/{id}`
- `GET /api/v1/investigations/{id}/sessions`
- `GET /api/v1/sessions/{id}`
- `GET /api/v1/investigations/{id}/failures`
- `GET /api/v1/failures/{id}`
- `GET /api/v1/investigations/{id}/groups`
- `GET /api/v1/groups/{id}`
- `GET /api/v1/investigations/{id}/dashboard`
- `POST /api/v1/investigations/{id}/assistant`
- `GET /api/v1/investigations/{id}/export?format=json`

## Architecture

DatasetImport -> SessionDocument -> Rule Engine + AI Analyzer -> FailureDocument -> FailureGroupDocument

Ground truth is isolated inside DatasetImport only and stored in a separate `evaluation_labels` collection, never leaking into SessionDocument.

## Evaluation

```bash
python -m scripts.run_evaluation INV-0001
```

## Reset

```bash
python -m scripts.reset_db
python -m scripts.seed_demo
```
