# GOMYCODE Hackathon — Official Submission Form Reference

> **Event**: GOMYCODE Come Build with AI (27 September 2026)  
> **Submission Deadline**: 17:30 Tunis Time (UTC+1)  
> **Target Award**: SupplyzPro — Smart Operations Award (*"Find the Hidden Failures"*)  
> **Additional Partner Awards**: Thunders, CompTIA, Guepard, EY Studio+, Artefact

---

## Form Fields & Completed Answers

### 1. Country *
`Kenya`

### 2. Hackerspace / ONLINE *
`ONLINE`

### 3. Team name *
`AgentLens`
*(Note: If your confirmed team name on the organizer roster differs, paste the exact confirmed name).*

### 4. Team leader full name *
`Edwin Mwiti`

### 5. Team leader email *
`eduedwyn5@gmail.com`

### 6. Project title *
`AgentLens`

### 7. Team members — full name of each member, one per line *
`Edwin Mwiti`

---

### 8. Project summary — maximum 150 words *
*(Current word count: 122 words — strictly under the 150-word limit)*

> AgentLens is an AI-agent reliability and investigation platform that detects hidden failures inside AI-agent conversations and tool calls. AI agents often appear successful while using the wrong record, repeating actions, making no progress, or claiming completion when tools failed. AgentLens analyzes complete agent sessions, detects these failure patterns, links each finding to supporting event evidence, groups recurring failures, and guides developers on what to investigate first. The prototype includes the NovaCart customer-support dataset with 100 synthetic sessions, automated failure detection, evidence-based grouping, an interactive dashboard, visual session timelines, and an AI investigation assistant. The system distinguishes genuine failures from legitimate retries and ambiguous cases, helping engineering teams move from raw agent logs to actionable, evidence-backed reliability fixes.

---

### 9. Problem solved *

> AI agents can fail silently even when they report complete success with zero technical exceptions (e.g. HTTP 200). Conventional observability tools monitor infrastructure metrics like latency and crash rates, but completely miss semantic and workflow breakdowns.
>
> In real-world enterprise operations, this creates severe hidden risks:
> 1. **Unsupported Success**: The agent claims an action succeeded (e.g. "Order cancelled and refund processed") when backend tools actually failed.
> 2. **Wrong Record Interaction**: The agent operates on an incorrect order, customer ID, or shipment tracking number.
> 3. **Repeated Questions**: The agent repeatedly asks the user for information already supplied in earlier turns.
> 4. **No-Progress Loops**: The agent consumes tokens repeating unproductive tool calls without moving toward the goal.
> 5. **Incomplete Requests**: The agent resolves one aspect of a multi-part request while abandoning the rest as completed.
> 6. **Alert Fatigue**: Developers face thousands of disconnected logs without clear clustering into recurring root-cause patterns.
>
> AgentLens solves this by inspecting full session traces, linking every failure to concrete event evidence, grouping recurring patterns, and prioritizing engineer investigation.

---

### 10. Solution and key features *

> - **(1) Core User Journey & Working Features**:
>   - **Investigation Lifecycle**: Create an investigation, ingest agent conversation datasets, and trigger automated analysis.
>   - **Deterministic Signal & Rule Engine**: Evaluates 9 deterministic signals to detect 5 core failure archetypes (Unsupported Success, No Progress, Wrong Record, Repeated Question, Incomplete Request).
>   - **Legitimate Retry & Ambiguity Handling**: Distinguishes temporary tool failures that recover successfully from real failures, and flags under-evidenced runs as ambiguous rather than forcing false alarms.
>   - **Semantic Failure Grouping**: Automatically clusters related failures into prioritized groups with occurrence counts, common signals, and developer recommendations.
>   - **Evidence-Linked Inspection & Visual Timeline**: Every failure links directly to the exact sequence of session events (`event_id`, tool arguments, results, agent responses) supporting the finding.
>   - **Investigation Assistant**: An interactive AI assistant grounded strictly in stored investigation evidence to answer developer queries without hallucination.
>   - **Evaluation Benchmark Engine**: Built-in ground-truth confusion matrix calculator measuring precision, recall, and F1 score.
>   - **Multi-Format Streaming Export**: Full investigation reports exported as JSON or RFC 4180 streaming CSV.
>
> - **(2) Anything Mocked, Simulated or Unfinished**:
>   - The customer conversations, order numbers, tracking IDs, and backend tool interactions in the NovaCart dataset are synthetically generated for benchmark integrity.
>   - Automated live execution remediation (auto-patching agent prompt code) is a future roadmap item; current focus is diagnostic intelligence and developer prioritization.
>
> - **(3) Built During Hackathon vs Reused**:
>   - **Built Entirely During Hackathon**: The complete FastAPI backend, Pydantic v2 domain schemas, custom rule engine, failure grouping algorithm, AI provider abstraction (Groq/Gemini/offline), MongoDB repositories, React/Vite interactive UI, 100-session NovaCart benchmark dataset generator, evaluation engine, and test suite.
>   - **Reused Libraries**: Standard open-source frameworks (FastAPI, Motor, Pydantic, React, Lucide-React, Vite, Pytest).

---

### 11. Technologies used *

`Python, FastAPI, Pydantic v2, MongoDB, Motor (Async PyMongo), React 19, Vite, JavaScript, Tailwind/CSS, Groq API (Llama-3.3-70B), Google Gemini API (google-genai SDK), REST API, Pytest, Git, GitHub`

---

### 12. Source code URL *
`https://github.com/Edwin420s/agentlens`

### 13. Presentation URL *
`[PASTE YOUR VIEWABLE PRESENTATION LINK HERE — e.g. Google Slides or Drive PDF]`

### 14. 90-second demo video URL *
`[PASTE YOUR VIEWABLE 90-SECOND VIDEO LINK HERE — e.g. Loom share link or unlisted YouTube]`

---

### 15. Project next step *

> Move AgentLens from synthetic benchmark evaluation into a real-time production observability platform. Key milestones:
> 1. **OpenTelemetry & Trace Adapters**: Add native ingestion adapters for LangChain, LlamaIndex, CrewAI, AutoGen, and Langfuse trace formats.
> 2. **Continuous Streaming Ingestion**: Enable Kafka / webhook streaming ingestion for live agent sessions in production customer-support systems.
> 3. **Prompt & Tool Remediation**: Close the loop from failure grouping to automated prompt guardrails and retry policy recommendations.
> 4. **Multi-Agent Swarm Tracing**: Extend semantic failure detection to multi-agent collaborative workflows and inter-agent communication breakdowns.

---

### 16. Partner awards — which prizes is your team applying for? *
Select the following checkboxes:
- [x] **SupplyzPro — Smart Operations Award**
- [x] **Thunders — Engineering Excellence Award**
- [x] **CompTIA — Skills & Technical Readiness Award**
- [x] **Guepard — AI Automation Award**
- [x] **EY Studio+ — Human-Centred Innovation Award**
- [x] **Artefact — Data & AI Award**

*(Do NOT select Yassir [Morocco only], DigiFemmes [Côte d’Ivoire only], Click Mobile [Kenya mobile-first], Kredete [Fintech/credit], or Palete.AI [Creative visual]).*

---

### 17. Primary prize application — choose the award that best fits your project *
`SupplyzPro — Smart Operations Award`

---

### 18. Award application — explain your project’s fit and eligibility *

> **SupplyzPro — Smart Operations Award**:  
> AgentLens was built directly to solve the "Find the Hidden Failures" challenge. It analyzes agent conversations and tool calls to detect recurring failures (unsupported success, no progress, wrong record, repeated questions, incomplete requests), groups related incidents into semantic failure clusters, and provides evidence-backed prioritization so operations teams know where to intervene first. Evidence is demonstrated in the failure-grouping view (`frontend/src/components/FailureGroupsView.jsx`), the detection rules (`backend/app/services/rule_engine.py`), and the 90-second video demo. Eligible globally; submitted from Kenya.
>
> **Thunders — Engineering Excellence Award**:  
> AgentLens delivers a robust, production-grade architecture combining an async FastAPI backend, Pydantic v2 schemas with strict regex validation, MongoDB compound-indexed persistence, React 19 UI, and a 100-user concurrency stress test achieving 189 req/s with 0 dropped requests. The codebase includes 11 passing automated unit/integration tests and a 20-point verification test suite (`scratch/security_and_frontend_e2e.py`). All source code is cleanly structured under `backend/` and `frontend/`.
>
> **CompTIA — Skills & Technical Readiness Award**:  
> The project demonstrates professional software engineering readiness across full-stack architecture, asynchronous database design, multi-tenant index isolation, strict type safety, REST API design, and automated testing. It embodies rigorous QA practices with zero ground-truth data leakage, secure memory-only CSV/JSON streaming, and resilient fallback handling when AI providers are unavailable.
>
> **Guepard — AI Automation Award**:  
> AgentLens automates the end-to-end diagnosis of autonomous agent operations: automated session ingestion, deterministic signal detection, semantic failure clustering, and an evidence-grounded AI assistant that interprets root causes. This replaces hours of manual transcript audits with instant, automated operational intelligence. Demonstrated live in the failure groups and investigation assistant UI.
>
> **EY Studio+ — Human-Centred Innovation Award**:  
> AgentLens transforms raw, overwhelming agent execution traces into an intuitive, developer-centric investigation workflow. By synthesizing complex multi-turn conversations into visual timelines, confidence scores, and clear "Where Engineers Should Look First" callouts, it drastically shortens incident triage time and empowers support engineers to resolve agent reliability issues confidently.
>
> **Artefact — Data & AI Award**:  
> AgentLens converts unstructured conversational data and tool call histories into structured, actionable business intelligence. Evaluated against the 100-session NovaCart benchmark, it delivers 92.86% precision, 100.00% recall, and an F1 score of 0.963 across operational failure modes, turning raw agent data into measurable reliability improvements.

---

### 19. AI/tool disclosure *

> **AI Inside Your Product**:  
> AgentLens integrates **Groq (Llama-3.3-70B)** and **Google Gemini (1.5-Flash / 2.5-Flash)** as an intelligent reasoning and interpretation layer.  
> *Input*: A cluster of 8 sessions where order cancellations failed in backend tool calls, but the agent reported success to the user.  
> *AI Action*: The AI receives the structured event evidence (tool calls, error codes, agent final utterance) without any ground-truth labels. It analyzes the common failure pattern and isolates the behavioral root cause.  
> *Output*: Generates a structured JSON response identifying the failure mechanism: *"Agent falsely reported order ORD-20015 as cancelled after cancel_order returned failed status."*, accompanied by concrete recommendations for engineer investigation.  
> *Offline Fallback*: If external LLM APIs are offline or unconfigured, the system automatically falls back to an internal deterministic analysis engine, ensuring 100% operational uptime.
>
> **AI Used to Help Build the Project**:  
> Claude and Gemini coding assistants were used for architectural co-planning, boilerplate generation, and debugging. Every component—including domain Pydantic schemas, rule logic, MongoDB compound indexes, security boundaries, and React state management—was verified, customized, tested, and audited by the author.
>
> **Datasets & APIs**:  
> - **Dataset**: NovaCart 100-session synthetic benchmark dataset created specifically for the project, featuring 65 successes, 7 legitimate retries, 8 unsupported successes, 6 no-progress loops, 5 wrong records, 4 repeated questions, 3 incomplete requests, and 2 ambiguous runs.  
> - **APIs**: Groq API, Google Gemini API via official `google-genai` SDK.  
> - **NVIDIA Brev**: Brev was not required or utilized for this prototype; all inference operates via efficient serverless endpoints and local deterministic execution.

---

### 20. Project cover / screenshot / logo URL — optional
`[PASTE A VIEWABLE LINK TO A SCREENSHOT OF THE AGENTLENS DASHBOARD IF AVAILABLE, OR LEAVE BLANK]`

### 21. Live demo URL — optional
`[PASTE DEPLOYED URL IF HOSTED ON VERCEL/RENDER, OR LEAVE BLANK FOR LOCAL RUN]`  
*(Note: A live public deployment is not required; the repository includes complete local run instructions via Docker Compose and native CLI).*

---

### 22. Testing, results and known limitations — optional

> - **100-Session Benchmark Test → Actual Result**: Ingested and analyzed all 100 NovaCart sessions. Achieved 26 True Positives, 2 False Positives, 0 False Negatives, and 72 True Negatives—delivering **92.86% Precision, 100.00% Recall, and an F1 score of 0.963**. Verified via the `/api/v1/investigations/{id}/evaluation` endpoint.
> - **Edge Case / Legitimate Retry Handling**: Evaluated sessions where a tool initially returned an error (e.g. transient network timeout) followed by a successful retry and task completion. The system correctly recognized the recovery as a legitimate retry (`legitimate_retry_success`), avoiding false failure alerts.
> - **Concurrency & Known Limitations**: Under 100 concurrent simulated users, the API sustained 189.2 req/s with an average latency of 447 ms and zero dropped requests. A known limitation is that the current prototype evaluates single-agent workflows against a defined 5-archetype ontology; multi-agent swarm tracing is planned for future releases.

---

### 23. Responsible AI and data *

> All conversational data, customer identifiers, orders, and tool traces in the NovaCart dataset are 100% synthetic and generated specifically for benchmarking; no real user or proprietary enterprise data was used. Ground-truth benchmark labels are strictly isolated in a protected database collection and never leaked to the operational session, failure, or AI endpoints. The system incorporates an explicit "Ambiguous" classification to prevent overconfident hallucinations on low-evidence sessions, routing uncertain cases to human review. All exports and error responses are sanitized in-memory to prevent data leakage.

---

### 24. Final confirmation *
`[X] I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.`

---

### 25. Public project showcase — optional
`Yes — publish our project and approved team member names in the public showcase.`
