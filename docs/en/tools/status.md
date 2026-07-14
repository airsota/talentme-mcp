# Status Tool Design Document

**Tool Name**: `status`  
**Type**: MCP Tool  

---

## 1. Core Objective
Aggregates local learning logs and mastery metrics into a consolidated career readiness report (UX Feature 19: Readiness Evaluation). It computes overall score percentages and groups topics into Mastered, Familiar, and Struggling segments, providing the data necessary to plot skill radars.

---

## 2. Design Philosophy
*   **Encapsulation of Analytics**: Simplifies raw database aggregation into a structured Markdown metrics dashboard.
*   **Actionable Categorization**: Sorts topics strictly by their mastery levels (1-5), helping the Agent quickly prioritize struggling domains in subsequent coaching prompts.

---

## 3. Tool Signature

```python
def status() -> str:
    """
    Aggregate Mastery data into a Readiness Score and Topic Distribution.
    The Agent will use this to generate a radar chart or analytics report.
    """
```

---

## 4. Execution Logic

### 4.1 SQLite Aggregation
*   Queries `learning_logs` table in `memory.db`.
*   Groups results by topic, keeping only the latest log entry per topic to compute current states.
*   Aggregates the total score and compares it against the maximum possible score (total topics multiplied by 5) to compute a percentage readiness score.

### 4.2 Segment Mapping
Categorizes topics into three priority levels:
*   🟢 **Mastered**: Mastery level >= 4
*   🟡 **Familiar**: Mastery level == 3
*   🔴 **Struggling**: Mastery level <= 2

### 4.3 Output Format
Returns a Markdown dashboard block:
```text
[USER MASTERY STATUS START]
### TalentMe Readiness Dashboard

**Overall Readiness Score**: 78.5%
**Total Topics Tracked**: 12

| Mastery Level | Count | Topics |
|---|---|---|
| 🟢 Mastered (4-5) | 4 | Transformers, Self-Attention, CNNs |
| 🟡 Familiar (3) | 5 | PyTorch, Backpropagation, SGD |
| 🔴 Struggling (1-2) | 3 | Distributed Training, Flash Attention |
[USER MASTERY STATUS END]
```
