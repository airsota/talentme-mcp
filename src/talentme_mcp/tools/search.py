import os
import re
import json
import requests
from typing import Literal
from mcp.server.fastmcp import FastMCP

def _is_path_safe(memory_path: str, requested_path: str) -> bool:
    if not memory_path:
        return False
    real_allowed = os.path.realpath(memory_path)
    real_requested = os.path.realpath(requested_path)
    return real_requested.startswith(real_allowed)

def _extract_snippet(content: str, query: str, context_chars: int = 100) -> str:
    """Extract a context snippet around a query match."""
    if not content:
        return "(empty)"
    
    # Try to find case-insensitive match
    lower_content = content.lower()
    lower_query = query.lower()
    idx = lower_content.find(lower_query)
    
    if idx < 0:
        return content[:context_chars * 2].strip() + "..."
        
    start = max(0, idx - context_chars)
    end = min(len(content), idx + len(query) + context_chars)
    snippet = content[start:end].strip()
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
        
    # Remove newlines for cleaner single-line snippet formatting
    snippet = snippet.replace('\n', ' ')
    return snippet

def _strip_qmd_metadata(chunk: str) -> str:
    """
    QMD hybrid search returns chunks that might have headers like:
    # filename.md
    or
    ## title
    
    We want to strip out any lines that look like file metadata and just return the pure text.
    For simplicity, if it's a markdown header that ends in .md, we strip it.
    """
    lines = chunk.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') and stripped.lower().endswith('.md'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip()

def setup_search_tool(mcp: FastMCP, api_url: str, license_key: str, memory_path: str = None, email: str = None):
    @mcp.tool()
    def search(query: str, scope: Literal["local", "cloud", "all"] = "all", lex_query: str = None, vec_query: str = None, top_k: int = 5) -> str:
        """
        Execute a Hybrid Dual-Source Search against both Local and Cloud Knowledge Bases.
        
        Args:
            query: Main search string. Used to scan the local vault. 
                   Will be used as default for lex_query/vec_query if they are not provided.
            scope: "local" (save tokens, local only), "cloud" (cloud only), or "all" (hybrid dual-source).
            lex_query: Keyword-based query for cloud (e.g. exact names).
            vec_query: Semantic query for cloud QMD search.
            top_k: Number of chunks to retrieve from cloud.
        """
        result_dict = {}

        # 1. Local Search
        if scope in ["local", "all"]:
            local_results = []
            if memory_path:
                try:
                    for root, _, files in os.walk(memory_path):
                        if not _is_path_safe(memory_path, root):
                            continue
                        if any(x in root for x in [".skills", "_meta", "_raw"]):
                            continue
                        for file in files:
                            if file.endswith(".md"):
                                path = os.path.join(root, file)
                                with open(path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if re.search(query, content, re.IGNORECASE):
                                        rel_path = os.path.relpath(path, memory_path)
                                        snippet = _extract_snippet(content, query)
                                        local_results.append({
                                            "path": rel_path,
                                            "snippet": snippet
                                        })
                except Exception as e:
                    local_results = [{"error": f"Search failed due to a local exception: {str(e)}"}]
            else:
                local_results = [{"error": "Memory path not configured."}]
            
            result_dict["local_results"] = local_results[:10]

        # 2. Cloud Search
        if scope in ["cloud", "all"]:
            cloud_results = []
            try:
                headers = {"Authorization": f"Bearer {license_key}"}
                if email:
                    headers["X-User-Email"] = email
                
                req_lex = lex_query if lex_query else query
                req_vec = vec_query if vec_query else query
                
                # Use --no-rerank equivalent if needed, but since it's via API, we assume API handles it fast.
                response = requests.post(
                    f"{api_url.rstrip('/')}/api/kb/hybrid_search",
                    json={
                        "intent": "knowledge_retrieval",
                        "lex_query": req_lex,
                        "vec_query": req_vec,
                        "top_k": top_k
                    },
                    headers=headers,
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    chunks = data.get("results", [])
                    for chunk in chunks:
                        pure_chunk = _strip_qmd_metadata(chunk)
                        if pure_chunk:
                            cloud_results.append(pure_chunk)
                    if not cloud_results:
                        cloud_results = [f"No cloud results found for '{req_lex}' or '{req_vec}'."]
                elif response.status_code == 403:
                    cloud_results = ["Error: You do not have access to this Snapshot version."]
                else:
                    cloud_results = [f"Error: Cloud Search API returned {response.status_code}."]
            except Exception as e:
                cloud_results = [f"Error: Failed to connect to cloud knowledge base. {str(e)}"]
                
            result_dict["cloud_pure_knowledge"] = cloud_results

        return json.dumps(result_dict, indent=2, ensure_ascii=False)
