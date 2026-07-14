# Lint Wiki Tool Design Document (Inactive in Current Release)

**Tool Name**: `lint_wiki`  
**Type**: MCP Tool (Disabled in current release)

---

## 1. Core Objective
Scans the local vault to detect broken wikilinks, orphan pages (pages without incoming references), and syntax validation errors.

---

## 2. Design Philosophy
*   **Static Analysis**: Inspects markdown structures locally without altering file contents.
*   **Decoupled Action**: Reports issues to the Agent, allowing the Agent to prompt the user or run cross-linkers, rather than auto-modifying files blindly.

---

## 3. Tool Signature

```python
def lint_wiki() -> str:
    """
    Perform a static analysis check of the local wiki to detect broken double links,
    missing files, or isolated notes.
    """
```

---

## 4. Execution Logic
*   Iterates over all `.md` files in the vault.
*   Parses links `[[target]]` and checks if `target.md` exists on disk.
*   Maintains a set of referenced targets and detects orphan notes.
*   Returns a Markdown issues report.
