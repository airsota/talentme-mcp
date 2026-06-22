import os
from typing import Optional
from mcp.server.fastmcp import FastMCP

def _is_path_safe(memory_path: str, requested_path: str) -> bool:
    if not memory_path:
        return False
    real_allowed = os.path.realpath(memory_path)
    real_requested = os.path.realpath(requested_path)
    return real_requested.startswith(real_allowed)

def setup_list_local_wiki_pages(mcp: FastMCP, memory_path: str):
    @mcp.tool()
    def list_local_wiki_pages(category: Optional[str] = None) -> str:
        """
        List pages in the memory vault.
        """
        if not memory_path:
            return "Error: Vault path not set."
            
        pages = []
        valid_categories = ["concepts", "entities", "skills", "references", "synthesis", "journal", "projects"]
        target_dirs = [category] if (category and category in valid_categories) else valid_categories
        
        for d in target_dirs:
            d_path = os.path.join(memory_path, d)
            if os.path.exists(d_path) and _is_path_safe(memory_path, d_path):
                for file in os.listdir(d_path):
                    if file.endswith(".md"):
                        pages.append(f"- [[{d}/{file}]]")
                        
        return "\n".join(pages) if pages else "No accessible documents found."
