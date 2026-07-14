# Review Tool Design Document

**Tool Name**: `review`  
**Type**: MCP Tool  

---

## 1. Core Objective
Calculates and retrieves learning topics that have decayed beyond Ebbinghaus forgetting thresholds, serving as the data source for active recall reviews.

---

## 2. Design Philosophy
*   **Threshold-Based Recall**: Topics are flagged for review depending on their last-practiced timestamp and current mastery level. Low mastery topics decay faster and require more frequent recall checks.
*   **Fatigue Mitigation**: Caps the returned list to the top 5 decayed items, protecting the user from context fatigue during study sessions.

---

## 3. Tool Signature

```python
def review() -> str:
    """
    Fetch topics that need spaced repetition based on the Ebbinghaus forgetting curve.
    The Agent will receive these topics and act as a Spaced Repetition Coach.
    """
```

---

## 4. Execution Logic

### 4.1 Decay Calculation
*   Queries `learning_logs` table in `memory.db` for all records.
*   Iterates over the latest log entry per topic and computes `days_elapsed` since the practice timestamp.
*   Maps Ebbinghaus review thresholds:
    *   `mastery_level <= 2`: Threshold is 1 day.
    *   `mastery_level == 3`: Threshold is 3 days.
    *   `mastery_level >= 4`: Threshold is 7 days.
*   Flags topics where `days_elapsed >= threshold`.

### 4.2 Output Format
If no topics meet the threshold:
```text
[USER REVIEW CONTEXT]
No topics currently meet the threshold for spaced repetition. The user's memory is fresh!
[USER REVIEW END]
```

If topics require review:
```text
[USER REVIEW CONTEXT START]
The following topics have crossed their forgetting curve thresholds and desperately need review:
- **Distributed Training** (Mastery: 2, Days elapsed: 4, Threshold: 1)
- **Flash Attention** (Mastery: 3, Days elapsed: 6, Threshold: 3)
[USER REVIEW CONTEXT END]
```
