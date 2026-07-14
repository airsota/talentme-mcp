# Search Tool Design Document

**Tool Name**: `search`  
**Type**: MCP Tool  

---

## 1. Core Objective
Merges local vault querying with cloud knowledge retrieval into a single, high-performance hybrid search interface. It provides the AI agent with a "global perspective" of what is already internalized locally and what exists on the server.

---

## 2. Design Philosophy
*   **Cloud as the "Platonic World of Concepts"**: Cloud results return pure knowledge snippets, stripped of filenames and metadata to prevent architecture bias.
*   **Local as the "Personalized World of Practice"**: Local results contain relative file paths and local snippets, allowing the Agent to cross-link and reference existing notes.
*   **Separation of Concerns**: When the Agent discovers relevant knowledge in the cloud but not in the local vault, it must trigger the `learn` workflow to internalize and personalize the knowledge.

---

## 3. Tool Signature

```python
def search(query: str, scope: Literal["local", "cloud", "all"] = "all", lex_query: str = None, vec_query: str = None, top_k: int = 5) -> str:
    """
    Execute a Hybrid Dual-Source Search against both Local and Cloud Knowledge Bases.
    
    Args:
        query: Main search string. Used to scan the local vault. 
               Will be used as default for lex_query/vec_query if they are not provided.
        scope: "local" (local only), "cloud" (cloud only), or "all" (hybrid dual-source).
        lex_query: Keyword-based query for cloud (e.g. exact terms).
        vec_query: Semantic query for cloud QMD search.
        top_k: Number of chunks to retrieve from cloud.
    """
```

---

## 4. Execution Logic

### 4.0 Routing
*   `scope == "local"`: Scans the local Obsidian workspace (skipping `.skills`, `_meta`, `_raw`).
*   `scope == "cloud"`: Calls the Cloud API `api/kb/hybrid_search`.
*   `scope == "all"`: Parallel dual-source execution, assembling both local and cloud outputs.

### 4.1 Local Grep
*   Walks the `memory_path` using regular expression matching over `.md` files.
*   Extracts relative paths and snippets (~200 characters) around matching terms.

### 4.2 Cloud Hybrid Query
*   Sends a POST request to `/api/kb/hybrid_search` with authorization headers.
*   Strips any QMD file titles or headers from returned segments to deliver pure text.

### 4.3 Output Format
Returns a formatted JSON string containing results:
```json
{
  "local_results": [
    {
      "path": "concepts/Transformer.md",
      "snippet": "...Transformer architecture relies on self-attention mechanisms to..."
    }
  ],
  "cloud_pure_knowledge": [
    "KV Cache is an optimization technique used to accelerate inference in generative models..."
  ]
}
```
