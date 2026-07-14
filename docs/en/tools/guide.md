# Guide Tool Design Document

**Tool Name**: `guide`  
**Type**: MCP Tool  

---

## 1. Core Objective
Aggregates the user's active learning logs and study plan status (Hot Context) from `memory.db` and the local vault, feeding it to the Agent to deliver a personalized Daily Digest (UX Feature 22).

---

## 2. Design Philosophy
*   **Active Summarization**: Synthesizes structured SQLite tables and Markdown plan status in a single call, preventing the Agent from wasting tokens performing global file checks.
*   **Empty State Support**: Identifies if the workspace is blank, returning a clean empty state context to trigger onboarding flows.

---

## 3. Tool Signature

```python
def guide() -> str:
    """
    Fetch the user's current Hot Context (recent logs, plans, review targets) 
    and prompt the Agent to deliver a Daily Digest.
    """
```

---

## 4. Execution Logic

### 4.1 Hot Context Ingestion
*   Queries `memory.db`'s `learning_logs` table:
    *   Retrieves the 3 most recently created logs.
    *   Retrieves the 3 oldest logs with `mastery_level <= 2` as review targets.
*   Reads the first 500 characters of `study-plan.md` (if exists).

### 4.2 Output Format
If the vault is empty:
```text
[USER HOT CONTEXT START]
- The user's memory database is completely empty.
- No recent topics, no weaknesses, no study plan.
[USER HOT CONTEXT END]
```

If the vault has data:
```text
[USER HOT CONTEXT START]
- Recent Topics:
  - Transformers (Mastery: 3)
- Weaknesses to Review:
  - Distributed Training (Mastery: 2)
- Current Plan Snapshot:
  # Study Roadmap...
[USER HOT CONTEXT END]
```
