# Assess Tool Design Document

**Tool Name**: `assess`  
**Type**: MCP Tool  

---

## 1. Core Objective
Retrieves standardized domain assessment rubrics from the cloud, serving as the data source for cold-start evaluations (UX Feature 1: Onboarding Assessment).

---

## 2. Design Philosophy
*   **Separation of Orchestration**: The Python tool only delivers the raw evaluation rubric. The interactive quiz flow, grading, and follow-up study plan generation are managed by the `tm-assess` Agent Skill.

---

## 3. Tool Signature

```python
def assess(domain: str, level: str) -> str:
    """
    Fetch an assessment rubric from the cloud for a specific domain and level,
    and prompt the Agent to conduct an interactive evaluation.
    
    Args:
        domain: Domain of assessment (e.g., "Machine Learning", "System Design")
        level: Target job seniority (e.g., "Junior", "Senior", "L5")
    """
```

---

## 4. Execution Logic

### 4.1 Cloud Ingestion
*   Queries the Cloud API endpoint `/api/kb/assessment` with the provided `domain` and `level` query parameters.
*   Strips title headers and filters metadata.

### 4.2 Output Format
Returns the rubric in a markdown format:
```markdown
--- CLOUD ASSESSMENT RUBRIC ({domain} - {level}) ---
(Rubric criteria and evaluation checklist...)
----------------------------------------------------
```
*The calling Agent uses this rubric alongside `tm-assess` instructions to execute the conversation loop.*
