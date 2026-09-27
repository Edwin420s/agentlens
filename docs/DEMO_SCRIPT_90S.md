# AgentLens: 90-Second Demo Video Script & Walkthrough

> **Recommended Tool**: Loom (screen share + narration, camera optional)  
> **Target Duration**: Exactly 90 seconds (01:30)  
> **Key Goal**: Demonstrate the problem, live working prototype, evidence-backed failure detection, grouping, and evaluation proof.

---

## Storyboard & Timing Breakdown

```
00:00 - 00:15 | The Silent Failure Problem
00:15 - 00:30 | Investigation & Overview Dashboard
00:30 - 00:45 | Semantic Failure Grouping & Prioritization
00:45 - 01:05 | Evidence-Linked Session Timeline
01:05 - 01:20 | Investigation Assistant & Ground-Truth Proof
01:20 - 01:30 | Business Impact & What's Next
```

---

## Second-by-Second Script & Screen Action

### 1. The Problem (00:00 - 00:15)
- **Screen**: Start on the AgentLens Landing Page / Investigation list (`http://localhost:5173`).
- **Narrator**:
  > *"Autonomous customer support and supply chain agents can report 100% success on surface logs while completely failing the user in reality: modifying the wrong order, looping infinitely, or falsely claiming an order is cancelled when backend tools failed.  
  > Traditional monitoring only checks if the API crashed. **AgentLens** checks whether the agent actually accomplished what the user asked."*

---

### 2. Loading Investigation & Overview Dashboard (00:15 - 00:30)
- **Screen**: Click into the **NovaCart 100-Session Investigation** (`INV-0001` or newly seeded investigation) to display the **Overview Dashboard**.
- **Visual Focus**: Point cursor to the KPI cards: Total Sessions (100), Success Rate (72%), Failures (28 sessions / 36 failure occurrences), and the Severity Breakdown bar chart.
- **Narrator**:
  > *"Here on the AgentLens dashboard, we've ingested 100 customer-support sessions from our NovaCart dataset.  
  > Notice how AgentLens separates genuine successes from legitimate retries, isolating 28 failed sessions containing 36 critical operational failures across 5 core failure archetypes."*

---

### 3. Failure Groups — "Where Engineers Look First" (00:30 - 00:45)
- **Screen**: Click the **Failure Groups** tab in the navigation bar.
- **Visual Focus**: Select the first group: `Unsupported Success — Order Cancellation`.
- **Visual Focus**: Highlight the badge: **8 Occurrences**, **High Severity**, and the **"Where Engineers Should Look First"** callout box.
- **Narrator**:
  > *"Instead of forcing developers to triage 100 disconnected logs, AgentLens automatically groups recurring failures into semantic clusters.  
  > Here, 8 sessions share a pattern: the `cancel_order` tool failed, but the agent still told the customer their order was cancelled and refunded. The AI summary pinpoints the exact failure mechanism."*

---

### 4. Evidence-Linked Session Timeline (00:45 - 01:05)
- **Screen**: Click on a linked member session (e.g. `SES-0002` or `SES-0009`) or switch to the **Sessions** tab.
- **Visual Focus**: Scroll through the chronological event timeline:
  - Event 1: User prompt *"Cancel order ORD-20015"*.
  - Event 2: Agent calls `cancel_order`.
  - Event 3: Tool returns `error: "Payment settlement locked"`.
  - Event 4: Agent falsely replies *"Your order has been cancelled and refunded!"* (highlighted in red failure badge).
- **Narrator**:
  > *"Every single failure is grounded in verifiable event evidence. Looking at Session SES-0002, we can see the exact turn where the agent calls cancel order, receives an error, but hallucinated success.  
  > No black-box guesswork—every finding is backed by timestamps, tool payloads, and event IDs."*

---

### 5. Investigation Assistant & Evaluation Proof (01:05 - 01:20)
- **Screen**: Switch to the **Assistant** tab, type *"Why are orders failing in the unsupported success group?"*, and press send.
- **Screen**: Then quickly click the **Evaluation** tab to display the Confusion Matrix.
- **Narrator**:
  > *"Our evidence-grounded Investigation Assistant answers developer queries using only observed session facts, avoiding hallucinations.  
  > And our built-in evaluation engine validates our detection accuracy against ground truth: **100% Recall, 92.86% Precision, and an F1 score of 0.963**, missing zero silent failures."*

---

### 6. Value & Next Steps (01:20 - 01:30)
- **Screen**: Show the Export button (downloading RFC 4180 CSV / JSON) and return to the main header.
- **Narrator**:
  > *"With exportable reports, sub-second latency, and multi-tenant isolation, AgentLens empowers engineering teams to build autonomous agents that customers can truly trust.  
  > Thank you!"*

---

## Recording Checklist for Presenter

- [ ] Ensure MongoDB is running (`localhost:27017`).
- [ ] Backend active on `http://localhost:8000` with clean logs.
- [ ] Frontend active on `http://localhost:5173` with full browser window maximized.
- [ ] Pre-seed the demo dataset using `python -m scripts.seed_demo` so the dashboard has rich data ready immediately.
- [ ] Hide browser bookmarks and close unrelated tabs.
- [ ] Verify microphone audio quality before recording.
- [ ] Set Loom sharing permissions to **"Anyone with the link can view"** after recording.
