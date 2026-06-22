import os
from mcp.server.fastmcp import FastMCP

def _is_path_safe(memory_path: str, requested_path: str) -> bool:
    if not memory_path:
        return False
    real_allowed = os.path.realpath(memory_path)
    real_requested = os.path.realpath(requested_path)
    return real_requested.startswith(real_allowed)

def setup_read_wiki_page(mcp: FastMCP, memory_path: str):
    @mcp.tool()
    def read_wiki_page(category: str, filename: str) -> str:
        """
        Read the content of a wiki page from local memory.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        target_path = os.path.join(memory_path, category, filename)
        
        if not _is_path_safe(memory_path, target_path):
            return "Error: Access denied. Path is outside of the allowed memory vault."
            
        if not os.path.exists(target_path):
            return f"Error: Page [[{category}/{filename}]] not found."
            
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "Error: Failed to read page due to a secure file access restriction."
