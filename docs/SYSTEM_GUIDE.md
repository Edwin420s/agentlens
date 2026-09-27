# AgentLens: System Guide & Plain-English Architecture

> A clear, plain-English reference explaining what AgentLens is, why it was built, how the workflow works step-by-step, and how it detects hidden failures in AI agents.

---

## 1. What Is AgentLens?

AgentLens is a system for checking whether an AI agent actually completed a user's request correctly.

The main idea is simple:

> **An AI agent can say "Done" even when something went wrong behind the scenes.**

AgentLens looks at what happened during an AI agent's conversation, finds these hidden problems, groups similar problems together, and helps a developer understand what needs to be fixed.

It is a quality-control and investigation platform for AI agents.

---

## 2. The Problem: Silent Semantic Failures

Imagine an online shopping AI agent for an e-commerce store called **NovaCart**.

A customer says:
> *"Please cancel my order ORD-20015 and refund me."*

1. The AI agent talks to its internal tools.
2. The agent calls `cancel_order(order_id="ORD-20015")`.
3. The tool execution fails because the payment settlement is locked.
4. But the AI agent still tells the customer:
   > *"Your order has been cancelled successfully and your refund has been processed."*

From the customer's point of view, everything looked successful.
From the server's point of view, the HTTP response code was 200 OK.
**In reality, the order was not cancelled, the money was not refunded, and the customer will be charged.**

A normal technical log only shows:
```
tool_call: cancel_order -> error: "locked"
agent_response: "Your order has been cancelled..."
```

That does not tell the engineering team:
- What the customer originally asked for.
- What the agent tried to do.
- Where the process went wrong.
- Whether the agent incorrectly claimed success.
- How many other customers experienced the exact same problem.
- Which problem should be investigated first.
- What evidence proves that the problem happened.

**AgentLens is built to answer those questions.**

---

## 3. The End-to-End System Workflow

```
AI Agent Interaction Traces
            │
            ▼
    [ Dataset Import ]
            │
            ▼
    [ Validation Engine ] ──► (Rejects malformed IDs, sequences, or missing events)
            │
            ▼
 [ Rule & Signal Detection ] ──► (Detects 9 behavioral signals like tool retries, errors)
            │
            ▼
   [ Session Analysis ] ──► (Classifies into Success, Failure, or Ambiguous)
            │
            ▼
  [ Failure Grouping ] ──► (Clusters into semantic groups: "Where Engineers Look First")
            │
            ▼
   [ AI Investigation ] ──► (AI synthesizes evidence into recommendations; or deterministic fallback)
            │
            ▼
  [ Interactive UI ] ──► (Dashboard, Failure Groups, Visual Event Timeline, Assistant)
            │
            ▼
 [ Evaluation & Export ] ──► (Ground-truth confusion matrix & streaming CSV/JSON export)
```

---

## 4. The 5 Core Failure Archetypes

AgentLens detects five primary failure patterns:

### 1. Unsupported Success
The agent tells the customer that a task succeeded, but the tool results either show an explicit failure or no tool was called at all.
- *Example*: The agent says *"Your return label has been created!"* but no return tool was ever invoked.

### 2. No Progress
The agent gets caught in a loop, calling tools repeatedly without getting any closer to fulfilling the user's request.
- *Example*: Searching for an order status 4 times with the same parameters without progressing the workflow.

### 3. Wrong Record
The agent works with the wrong order, customer, shipment, or payment record.
- *Example*: Customer asks about `ORD-20021`, but the agent looks up and modifies `ORD-20091`.

### 4. Repeated Question
The agent asks the customer for information that the customer already provided earlier in the chat.
- *Example*: Customer says *"My email is alex@example.com"*, and 2 turns later the agent asks *"What is your email address?"*.

### 5. Incomplete Request
The customer asks for two things (e.g. *"Change my shipping address and apply a coupon"*), but the agent only does one and closes the conversation as finished.

---

## 5. Intelligent Handling of Retries & Ambiguity

AgentLens does **not** treat every single error as a failure.

### Legitimate Retries (`legitimate_retry_success`)
Suppose:
1. Agent calls `get_tracking_info` → Tool returns a transient network timeout.
2. Agent retries `get_tracking_info` → Tool returns valid tracking details.
3. Agent answers customer *"Your package is in transit"*.

AgentLens understands that the first attempt failed, but the overall task ultimately succeeded. It records this as a legitimate recovery, avoiding false alarms.

### Ambiguous Cases
Sometimes the evidence is incomplete (for example, a refund is listed as "pending manual audit"). AgentLens flags the session as **Ambiguous** and recommends human review rather than guessing or fabricating an outcome.

---

## 6. The NovaCart 100-Session Benchmark Dataset

The prototype includes a comprehensive 100-session synthetic benchmark dataset representing realistic customer service scenarios:

| Category | Sessions | Description |
| :--- | :---: | :--- |
| **Normal Success** | 65 | Straightforward, error-free request fulfillment |
| **Legitimate Retry** | 7 | Transient failure recovered via retry |
| **Unsupported Success** | 8 | False completion claim following tool failure |
| **No Progress** | 6 | Redundant loops without forward movement |
| **Wrong Record** | 5 | Entity ID / customer record mismatch |
| **Repeated Question** | 4 | Redundant inquiries for already provided data |
| **Incomplete Request** | 3 | Multi-part intent partially abandoned |
| **Ambiguous** | 2 | Insufficient evidence for confident verdict |
| **Total** | **100** | Full benchmark coverage |

---

## 7. Strict Ground-Truth Isolation

To ensure scientific integrity:
- Ground-truth benchmark labels are stored in an isolated database collection (`evaluation_labels`).
- The operational session and failure APIs **never** receive or return ground-truth labels.
- The AI layer is evaluated purely on its ability to detect failures from the raw event stream, preventing any data leakage.

---

## 8. Verified Evaluation Metrics

AgentLens includes an evaluation endpoint that tests predictions against the benchmark ground truth:

```
Confusion Matrix:
- True Positives (TP):   26
- False Positives (FP):   2
- False Negatives (FN):   0
- True Negatives (TN):   72

Performance:
- Precision:  92.86%
- Recall:    100.00%  (Zero silent failures missed!)
- F1 Score:    0.963
```

---

## 9. Technology Stack

- **Backend**: FastAPI with async Python 3.12, strict Pydantic v2 schemas.
- **Persistence**: MongoDB with Motor async driver and compound multi-tenant indexes.
- **Frontend**: React 19 SPA powered by Vite, with Lucide icons and clean CSS.
- **AI Models**: Groq (Llama-3.3-70B) or Google Gemini (1.5-Flash / 2.5-Flash), with an automatic deterministic fallback baseline when offline.
- **Export**: Standards-compliant RFC 4180 streaming CSV and structured JSON.
- **Testing**: Pytest unit tests, end-to-end verification suite, and 100-user concurrency stress testing.
