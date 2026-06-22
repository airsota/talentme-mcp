# TalentMe MCP Reference Architecture & Checklist

This document serves as the master source of truth for the TalentMe MCP Architecture, detailing the strict boundary between MCP Tools (Atomic APIs) and Agent Skills (Orchestration Prompts).

## 1. MCP Tools (Atomic Primitives) Checklist

**Analysis of Existing Tools in `talentme-mcp`:**
- **Keep (Local/Memory)**: `log_learning_progress`, `get_user_memory_summary`, `create_wiki_page`, `read_wiki_page`, `search_local_wiki`, `list_local_wiki_pages`. These are perfect atomic primitives for local file/DB manipulation.
- **Keep (Skill Management)**: `list_agent_skills`, `read_agent_skill_instruction`. These are the core engines for dynamic skill injection.
- **Consolidate/Upgrade (Cloud)**: `search_knowledge_base` and `list_kb_topics` must be refactored/upgraded into `cloud_knowledge_query` (Hybrid Search). `read_cloud_knowledge` is kept but its backend implementation needs strict license gating.

### Infrastructure & Authorization
- [x] `list_agent_skills()`: Returns available skills based on user license. (Already exists, needs payload alignment)
- [x] `read_agent_skill_instruction(skill_name)`: Injects SOP into context. (Already exists)
- [x] `check_user_auth_status()`: Returns current subscription tier. (To be added)

### Cloud Knowledge Engine (Upgraded)
- [x] `cloud_knowledge_query(intent, lex_query, vec_query, top_k)`: The new Hybrid QMD Search (replaces `search_knowledge_base`).
- [x] `read_cloud_document(file_path)`: Fetches full markdown. (Currently exists as `read_cloud_knowledge`, needs backend mapping).

### Local Context & Wiki Management (Existing)
- [x] `read_local_memory_stats()`: Maps to existing `get_user_memory_summary()`.
- [x] `log_learning_progress(topic, summary, mastery)`: Writes to `memory.db`.
- [x] `create_wiki_page(title, category, content, tags)`: Writes to local Obsidian.
- [x] `read_wiki_page(category, filename)`: Reads local Obsidian.
- [x] `search_local_wiki(query)`: Greps local vault.
- [x] `list_local_wiki_pages(category)`: Lists local files.

---

## 2. Tri-Partite Agent Skills Checklist

These will be drafted as Markdown SOPs and stored in the `cloud/skills/` directory on the server.

### Category 1: Cloud Synthesis Skills (Server-side, Read-only)
- [x] `cloud-jd-matcher`: Matches JD with cloud content.
- [x] `cloud-style-framer`: Formats output to BLUF/TalentMe styles.
- [x] `cloud-mock-interviewer`: Simulates strict 1v1 interviews using case banks.

### Category 2: Local Management Skills (Client-side, Read/Write)
- [x] `local-cross-linker`: Scans vault and creates `[[]]` wikilinks automatically.
- [x] `local-timeline-updater`: Manages the user's interview pipeline logs.
- [x] `local-review-prompter`: Reminds user to review concepts based on Ebbinghaus curve.

### Category 3: Bridge Orchestrators (Workflow Controllers)
- [x] `bridge-sync-and-digest`: The ultimate ETL workflow. Instructs AI to:
  1. Use `read_agent_skill_instruction` for `cloud-jd-matcher`
  2. Use `cloud_knowledge_query` to fetch facts
  3. Synthesize and use `create_wiki_page` to save locally
  4. Use `log_learning_progress` to record the study session.

---

## 3. Development Workflow

For all future capability expansions, follow this SOP:
1. **Discover**: Identify the user pain point.
2. **Evaluate Tooling**: If the AI lacks the *mechanical ability* to read/write specific data, build a new `MCP Tool` (Python function with `@mcp.tool()`).
3. **Draft Skill SOP**: If the AI has the tools but lacks the *brain/logic* to use them correctly, write a new `Agent Skill` (Markdown file).
4. **Deploy**: Push the new tool/skill to the MCP package or cloud backend.
