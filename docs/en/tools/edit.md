# Edit Tool Design Document

**Tool Name**: `update_wiki_page`  
**Type**: MCP Tool  

---

## 1. Core Objective
Safely appends or overwrites content in an existing local Markdown page in the memory vault.

---

## 2. Design Philosophy
*   **Path Traversal Defense (CWE-22)**: Ensures all write operations resolve to a canonical path strictly within the bounds of the configured `memory_path`. Any attempts to use `..` to escape are rejected.
*   **Encapsulation of Writes**: Restricts edits to existing files, requiring the agent to use `create_wiki_page` for new creations.

---

## 3. Tool Signature

```python
def update_wiki_page(page_name: str, mode: str, new_content: str) -> str:
    """
    Modify an existing local wiki page by appending or overwriting.
    
    Args:
        page_name: Name of the target page (with or without .md extension).
        mode: 'append' (appends content to end of file) or 'overwrite' (replaces contents).
        new_content: The markdown text to inject.
    """
```

---

## 4. Execution Logic

### 4.1 Safe Path Resolution
*   Recursively walks `memory_path` to locate the target `page_name`.
*   Sanitizes and compares absolute paths via `os.path.realpath` to confirm boundaries.

### 4.2 Append vs Overwrite
*   `append` mode: Opens file in `'a'` mode and appends two newlines followed by the new content.
*   `overwrite` mode: Opens file in `'w'` mode and overwrites all text.

### 4.3 Output Format
Returns write status:
`Successfully appended page: Transformer.md.`
