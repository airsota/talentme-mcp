# Learn Tool Design Document

**Tool Name**: `learn`  
**Type**: MCP Tool  

---

## 1. Core Objective
Initiates a personalized learning session (the "Handshake Protocol") for a specified cloud document. It fetches verified knowledge blocks from the cloud, injects safety watermarks, and logs a baseline learning entry into `memory.db`.

---

## 2. Design Philosophy
*   **Separation of Data and Intent**: The `learn` tool retrieves raw content, but leaves the synthesis and writing to the calling Agent.
*   **Prompt Decoupling**: Rather than returning complex system steering rules directly from the python tool, instructions are driven by the `bridge-sync-and-digest` Agent Skill. The tool focuses strictly on data assembly and progress logging.

---

## 3. Tool Signature

```python
def learn(cloud_doc_id: str, user_intent: str) -> str:
    """
    Start a personalized learning session for a cloud document (The Handshake Protocol).
    
    Args:
        cloud_doc_id: The identifier of the cloud document to fetch.
        user_intent: The specific angle, role, or style the user wants to learn this from (e.g., "MLE interview prep").
    """
```

---

## 4. Execution Logic

### 4.1 Cloud Ingestion
*   Queries the Cloud Search API for `cloud_doc_id`.
*   Assembles returned segments, removing QMD metadata headers.
*   Appends a hashed license signature watermark for data security.

### 4.2 SQLite Logging
Inserts a learning record into `learning_logs` table:
*   Sets `topic = cloud_doc_id`
*   Sets `summary = "Initiated learning via Handshake Protocol. Intent: {user_intent}"`
*   Initializes `mastery_level = 1`

### 4.3 Output Format
Returns a confirmation status together with the cloud knowledge content:
```markdown
✅ Successfully logged learning progress to memory.db for: {cloud_doc_id}.

--- CLOUD KNOWLEDGE CONTENT ---
### [Knowledge Chunk #1]
(Fetched content snippets...)
---
*本笔记为 TalentMe (https://talentme.airsota.com) 专属定制编译 (License: tm-hash)*
-------------------------------
```
