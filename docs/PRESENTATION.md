# AgentLens — Presentation Deck Outline (10 Slides)

> **Hackathon**: GOMYCODE Come Build with AI (27 September 2026)  
> **Track**: SupplyzPro — Smart Operations Award (*"Find the Hidden Failures"*)  
> **Format**: Ready for Google Slides / Canva / Keynote export.

---

### Slide 1: Title Slide
- **Title**: AgentLens
- **Subtitle**: Discovering Hidden Failures in Autonomous AI Agent Workflows
- **Presenter**: Edwin Mwiti (Lead & Builder) | Kenya Online
- **Challenge Track**: SupplyzPro — Smart Operations Award
- **Live System**: FastAPI + MongoDB + React 19 + Groq/Gemini

---

### Slide 2: The Silent Failure Dilemma
- **The Core Problem**:
  - AI agents can complete execution with HTTP 200 and zero runtime errors, yet completely fail the end-user.
- **Real-World Examples**:
  - *False Completion*: Agent claims "Order cancelled!" after `cancel_order` tool failed.
  - *Entity Confusion*: Agent looks up and modifies the wrong customer order.
  - *Endless Loops*: Agent repeatedly re-runs failing searches without progress.
  - *Premature Hand-Off*: Agent answers 1 part of a 2-part customer request and terminates.
- **Why It Matters**:
  - Infrastructure observability (APMs, logs) monitors crash rates; it misses semantic & behavioral breakdowns.

---

### Slide 3: The Solution — AgentLens
- **What is AgentLens?**
  - An end-to-end reliability and investigation console for AI agent operations.
- **Key Capabilities**:
  - **Deterministic Rule Engine**: Analyzes conversation turns and tool calls for 9 concrete behavioral signals.
  - **Semantic Failure Grouping**: Automatically clusters individual failures into systemic problem categories.
  - **Evidence-Linked Findings**: Every failure is anchored to chronological event IDs, arguments, and return values.
  - **Investigation Assistant**: An AI co-pilot grounded strictly in verified event facts.

---

### Slide 4: The 5 Failure Archetypes
1. **Unsupported Success**:
   - The agent claims success despite absent or explicitly failing tool confirmations.
2. **No Progress**:
   - High event count with repetitive, redundant tool calls that make no forward progress.
3. **Wrong Record**:
   - Mismatches between user-specified entity IDs (order ID, tracking number) and tool query parameters.
4. **Repeated Question**:
   - The agent asks the user for information already provided earlier in the conversation.
5. **Incomplete Request**:
   - Multi-intent queries where primary user objectives are left unexecuted.

---

### Slide 5: Intelligent Edge Case Handling
- **Legitimate Retries ≠ Failures**:
  - When a tool call encounters a temporary error (e.g. rate limit, momentary database timeout) but the agent successfully retries and completes the task, AgentLens flags it as `legitimate_retry_success`—preventing alert fatigue.
- **Ambiguous Cases**:
  - When available session evidence is insufficient for a confident classification (e.g. async operations pending), AgentLens marks the session as `Ambiguous` and recommends human review rather than fabricating a verdict.

---

### Slide 6: System Architecture & Tech Stack
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
```
- **Performance**: Sustains 189 req/s under 100 concurrent users with 0 dropped requests.
- **Multi-Tenant Isolation**: Compound unique indexing `(investigation_id, session_id)`.

---

### Slide 7: Evaluation & Ground-Truth Benchmark
- **NovaCart 100-Session Benchmark**:
  - 65 Normal Successes
  - 7 Legitimate Retries (Successfully handled without false alerts)
  - 8 Unsupported Successes | 6 No-Progress Loops | 5 Wrong Records | 4 Repeated Questions | 3 Incomplete Requests | 2 Ambiguous Runs
- **Confusion Matrix**:
  - **True Positives (TP)**: 26
  - **False Positives (FP)**: 2
  - **False Negatives (FN)**: 0
  - **True Negatives (TN)**: 72
- **Metrics**:
  - **Precision**: 92.86%
  - **Recall**: 100.00% (Zero silent failures missed!)
  - **F1 Score**: 0.963

---

### Slide 8: Interactive Investigation Experience
- **Overview Dashboard**: High-level failure rate, severity distributions, and quick KPIs.
- **Failure Groups View**: Focuses engineer attention on "Where Engineers Should Look First".
- **Visual Session Timeline**: Step-by-step trace showing user turns, tool invocations, and agent responses.
- **Evidence Inspector**: Collapsible raw JSON payloads for auditing exact parameters.
- **Investigation Assistant**: Context-aware queries grounded in observed session events.

---

### Slide 9: Partner Awards Fit
- **SupplyzPro (Smart Operations)**: Directly solves "Find the Hidden Failures" with automated grouping & evidence.
- **Thunders (Engineering Excellence)**: Async FastAPI backend, React 19 UI, MongoDB indexes, 100-user stress tested.
- **CompTIA (Technical Readiness)**: Strict type safety with Pydantic v2, unit test coverage, secure error envelopes.
- **Guepard (AI Automation)**: End-to-end automated session analysis replacing manual transcript audits.
- **EY Studio+ (Human-Centred Innovation)**: Developer-first UX turning complex event logs into actionable root-cause insights.
- **Artefact (Data & AI)**: Transforms unstructured agent logs into structured reliability intelligence.

---

### Slide 10: Vision & Roadmap
- **Short Term**:
  - Native OpenTelemetry and Langfuse trace format ingestion adapters.
  - Webhook streaming ingestion for live production agent monitoring.
- **Medium Term**:
  - Automated prompt guardrail patching and retry policy recommendations.
  - Multi-agent swarm tracing to detect communication breakdowns across collaborative agent teams.
- **Repository**: `https://github.com/Edwin420s/agentlens`
