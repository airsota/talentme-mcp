# Rebuild Wiki Graph Tool Design Document

**Tool Name**: `rebuild_wiki_graph`  
**Type**: MCP Tool  

---

## 1. Core Objective
Performs a global scan of the local vault to build a dictionary of concepts, insert double backlinks (`[[wikilinks]]`) across markdown files safely, append Cross-Reference blocks, and generate a consolidated knowledge glossary.

---

## 2. Design Philosophy
*   **AST Token Protection**: Uses regular expression groups to ignore code blocks, inline code, header lines, and existing wikilinks, preventing corruption of markdown syntax.
*   **Anti-Data Drift**: Re-evaluates links dynamically and maps relationships. Generates a global glossary file `glossary.md` summarizing what topics are covered.

---

## 3. Tool Signature

```python
def rebuild_wiki_graph(target_dir: str = None) -> str:
    """
    Rebuild the Knowledge Base graph. Cleans legacy formats, generates a global glossary.md,
    injects safe semantic wikilinks across all markdown files, and auto-appends Cross-References.
    
    Args:
        target_dir: The directory to rebuild. Uses the default memory vault if not provided.
    """
```

---

## 4. Execution Logic

### 4.1 Indexing
*   Scans all `.md` files in the vault (skipping indexes, README, glossary, changelogs).
*   Extracts YAML title frontmatter and first body paragraph for descriptions.
*   Builds a dictionary of terms to match.

### 4.2 Pattern Matching & Wikilinking
*   Sorts terms by length descending to match longer multi-word concepts first.
*   Uses a regex tokenizer to substitute matching words with wikilink references `[[target|word]]` ONLY in plain-text segments (ignoring code blocks, existing links).
*   Appends a `## 🔗 Cross-References` section detailing prerequisites (incoming links), comparisons, and next steps at the bottom of modified files.

### 4.3 Glossary Compilation
Generates `glossary.md` with alphabetical headings, detailing:
*   Concept name.
*   Auto-extracted description ("What is it?").
*   Clickable link.

### 4.3 Output Format
Returns compilation statistics:
```text
[REBUILD WIKI GRAPH SUCCESS]
Processed Target Directory: /Users/suiyaochen/Desktop/Memory/Suiyao/obsidian-memory/my_memory
Execution Time: 0.45 seconds
Extracted Concepts: 32
Modified Files (Links/MOC/References updated): 5
Total Cross-References Mapped: 23
Global Glossary Generated: glossary.md
```
