# TalentMe Development Master List

This document lists all **MCP Tools** and **Agent Skills** that form the TalentMe ecosystem.

---

## 1. MCP Tools (Backend APIs)
MCP Tools are Python-implemented primitives (`@mcp.tool()`) that execute file modifications, database queries, and make authenticated Cloud API requests.

| Tool Name | Core Capability | Supported UX Feature | Status |
|-----------|-----------------|----------------------|--------|
| **`search`** | Parallel hybrid local/cloud search. | Core Search | Completed |
| **`learn`** | Retrieves verified concepts from Cloud API. | Deep Learning (F2) | Completed |
| **`assess`** | Downloads structured quizzes for evaluation. | Level Assessment (F1) | Completed |
| **`guide`** | Generates recommendations for daily study tasks. | Daily Digest (F22) | Completed |
| **`review`** | Fetches decayed notes using spaced repetition. | Spaced Repetition | Completed |
| **`status`** | Aggregates mastery and prints readiness metrics. | Readiness Evaluation (F19) | Completed |
| **`log_learning_progress`** | Updates knowledge mastery levels in `memory.db`. | Mastery Lifecycle | Completed |
| **`manage_interview`** | Logs and updates the job application timeline. | Interview Timeline (F5) | Completed |
| **`import_expert_feedback`** | Calibrates local mastery using tutor feedback. | Expert Feedback (F12) | Completed |
| **`check_user_auth_status`** | Verifies license key and subscription tiers. | Auth & Gating | Completed |
| **`get_user_memory_summary`** | Fetches general stats of the local Obsidian vault. | Status Overview | Completed |
| **`list_agent_skills`** | Lists dynamic cloud steering instructions. | Skill Index | Completed |
| **`read_agent_skill_instruction`** | Dynamically injects specialized SOP prompts. | Skill Injection | Completed |
| **`create_wiki_page`** | Creates a new markdown file in local Obsidian. | Vault Write | Completed |
| **`read_wiki_page`** | Reads local markdown notes. | Vault Read | Completed |
| **`update_wiki_page`** | Appends or overrides contents in local notes. | Vault Edit | Completed |
| **`list_local_wiki_pages`** | Scans relative files in memory directories. | Vault Index | Completed |
| **`rebuild_wiki_graph`** | Syncs backlink relations and updates DB states. | Vault Graph Sync | Completed |
| **`get_session_context`** | Returns active IDE workspace environment details. | Session Context | Completed |

---

## 2. Agent Skills (Orchestration Instructions)
Agent Skills are Markdown-formatted Standard Operating Procedures (SOPs). They guide the AI to chain MCP Tools to accomplish complex user tasks.

| Skill Name | Orchestration Behavior | Supported UX Feature | Status |
|------------|------------------------|----------------------|--------|
| `tm-guide` | Orchestrates daily review and study priorities. | Guide & Route | Completed |
| `tm-review` | Drives Socratic active recall testing for weak points. | Spaced Repetition | Completed |
| `tm-cross-linker` | Scans notes to automatically insert `[[wikilinks]]`. | Vault Link Sync | Completed |
| `tm-provenance` | Traces and tags note sources (local vs. cloud). | Data Provenance | Completed |
| `tm-contradiction` | Identifies logical conflicts between new and old files. | Quality Control | Completed |
| `tm-merge` | Smart-merges imported files instead of duplicating. | Info Ingestion (F24) | Completed |
| `tm-tag-taxonomy` | Enforces tag consistency and standard formatting. | Tag Standards | Completed |
| `tm-assess` | Guides interactive定级 (level) evaluation quizzes. | Level Assessment (F1) | Completed |
| `tm-mock` | Conducts realistic pressure mock-interviews (Bar Raiser). | Mock Interview (F6) | Completed |
| `tm-plan` | Compiles a custom 14-day study roadmap (`study-plan.md`). | Roadmap Gen (F3) | Completed |
| `tm-prep` | Forecasts target company questions (`PREP.md`). | Interview Prep (F4) | Completed |
| `tm-debrief` | Leads structured post-interview loop reviews (`debrief.md`). | Interview Debrief (F4) | Completed |
| `tm-summary` | Summarizes interview logs and extracts new topics. | Interview Summary (F4) | Completed |
| `tm-question` | Parses forum questions and matches them to concepts. | Question Parser (F25) | Completed |
| `tm-brief-for-expert` | Strips private info to prepare briefing files for experts. | Mentor Brief (F11) | Completed |
| `tm-coaching-capture` | Updates study plans based on career advice. | Decision Capture (F14)| Completed |
| `tm-import-review` | Merges tutor edits directly into local resumes. | Resume Review (F16) | Completed |
| `tm-articulate` | Trains structural answer techniques (STAR method). | Answer Structure (F17)| Completed |
| `tm-session-save` | Selectively harvests key insights from chat histories. | Chat Ingestion | Completed |
| `tm-history-learn` | Scans chat history folder to extract interview Q&As. | History Mining | Completed |
| `tm-insight` | Uses LLM clustering to spot high-frequency patterns. | Pattern Spot (F7) | Completed |
| `tm-resume` | Rewrites CV markdown bullet points using mastery scores. | Resume Opt (F16) | Completed |
| `tm-offer` | Simulates salary negotiation and offer evaluation. | Negotiation (F20) | Completed |

---

## 3. Global Product Feature Mapping
These tools and skills interweave to power the overall TalentMe experience:

1.  **Zero-Friction Cold Start**:
    *   `tm-assess` (Skill) invokes `assess` (MCP Tool) to run the baseline test.
    *   `tm-resume` (Skill) parses user resumes to initialize Mastery levels.
    *   `tm-plan` (Skill) compiles `study-plan.md` to map out the next 14 days.
2.  **Unobtrusive Learning Loop**:
    *   Daily digest powered by `guide` (MCP).
    *   Local graph updates invoke `rebuild_wiki_graph` to sync Markdown changes back to `memory.db` without data drift.
3.  **Interview Campaign Suite**:
    *   `manage_interview` (MCP) registers dates and milestones.
    *   `tm-prep`, `tm-debrief`, and `tm-summary` generate target templates automatically.
4.  **Tutor Bridge (Premium)**:
    *   `tm-brief-for-expert` formats data for human review.
    *   `import_expert_feedback` merges tutor corrections back to local databases.
