import os
import re
from mcp.server.fastmcp import FastMCP

def _is_path_safe(memory_path: str, requested_path: str) -> bool:
    if not memory_path:
        return False
    real_allowed = os.path.realpath(memory_path)
    real_requested = os.path.realpath(requested_path)
    return real_requested.startswith(real_allowed)

def setup_search_local_wiki(mcp: FastMCP, memory_path: str):
    @mcp.tool()
    def search_local_wiki(query: str) -> str:
        """
        Search the user's local memory vault.
        """
        if not memory_path:
            return "Error: Memory path not found."
            
        results = []
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
                                results.append(f"### [[{rel_path}]]")
        except Exception:
            return "Error: Search failed due to a security restriction."
        
        return "\n".join(results[:10]) if results else "No matches found."
