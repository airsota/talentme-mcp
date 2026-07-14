# Import Expert Feedback Tool Design Document (Inactive in Current Release)

**Tool Name**: `import_expert_feedback`  
**Type**: MCP Tool (Disabled in current release)

---

## 1. Core Objective
Parses structured evaluation JSON documents received from human tutors or mock interviewers, importing graded scores directly into the local SQLite database.

---

## 2. Design Philosophy
*   **Calibration Loop**: Connects external manual assessments with the user's local learning tracker to update readiness metrics.

---

## 3. Tool Signature

```python
def import_expert_feedback(feedback_json: str) -> str:
    """
    Parse expert grading feedback JSON and update local db mastery values.
    
    Args:
        feedback_json: Graded JSON output containing topic names and mastery ratings.
    """
```

---

## 4. Execution Logic
*   Decodes the feedback payload.
*   Performs database write calls to insert or replace entries in `learning_logs` with updated mastery levels.
