# Interview Tool Design Document

**Tool Name**: `manage_interview`  
**Type**: MCP Tool  

---

## 1. Core Objective
Manages interview stages, schedules, and statuses inside `memory.db`'s `interviews` table, supporting timeline logging (UX Feature 5).

---

## 2. Design Philosophy
*   **Pipeline Tracking**: Keeps a clean chronological list of interview rounds, marking whether preparatory files (`has_prep`) or debrief sheets (`has_debrief`) have been completed.
*   **Proactive Warnings**: When listing interviews, alerts the Agent if upcoming active rounds lack prep work, triggering a warning to run prep workflows.

---

## 3. Tool Signature

```python
def manage_interview(
    action: str, 
    company: Optional[str] = None, 
    role: Optional[str] = None, 
    stage: Optional[str] = None, 
    status: Optional[str] = None, 
    date: Optional[str] = None,
    interview_id: Optional[int] = None
) -> str:
    """
    Manage interview timeline and states in memory.db.
    
    Args:
        action: 'add', 'update_status', 'mark_prep', 'mark_debrief', or 'list'
        company: Name of the company (e.g. 'Meta')
        role: Title applied for (e.g. 'ML Engineer')
        stage: Round name (e.g. 'Phone Screen', 'Onsite')
        status: Progress state (e.g. 'Scheduled', 'Passed', 'Rejected')
        date: Date of the round
        interview_id: ID of the entry for selective edits
    """
```

---

## 4. Execution Logic

### 4.1 SQL Timeline Operations
*   Creates `interviews` table if not exists with columns tracking has_prep and has_debrief flags.
*   Supports actions:
    *   `add`: Inserts a new interview round.
    *   `update_status`: Alters the state and date fields.
    *   `mark_prep` / `mark_debrief`: Sets completed checkboxes.
    *   `list`: Returns the 10 most recent rounds.

### 4.2 Output Format
For listing queries:
```text
[USER INTERVIEW TIMELINE START]
### Upcoming / Recent Interviews

| ID | Company | Role | Stage | Date | Status | PREP? | DEBRIEF? |
|---|---|---|---|---|---|---|---|
| 1 | Meta | ML Engineer | Phone Screen | 2026-07-20 | Scheduled | ❌ | ❌ |
[USER INTERVIEW TIMELINE END]
4. I notice they have upcoming interviews with `PREP?` marked as ❌. YOU MUST strongly suggest using the `tm-prep` skill or `search/learn` tools to generate a PREP document right now.
```
