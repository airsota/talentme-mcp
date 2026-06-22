import os
from datetime import datetime
from typing import List
from mcp.server.fastmcp import FastMCP

def _is_path_safe(memory_path: str, requested_path: str) -> bool:
    if not memory_path:
        return False
    real_allowed = os.path.realpath(memory_path)
    real_requested = os.path.realpath(requested_path)
    return real_requested.startswith(real_allowed)

def setup_create_wiki_page(mcp: FastMCP, memory_path: str):
    @mcp.tool()
    def create_wiki_page(title: str, category: str, content: str, tags: List[str] = None, summary: str = "") -> str:
        """
        Create a new wiki page in the local memory vault.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        valid_categories = ["concepts", "entities", "skills", "references", "synthesis", "journal", "projects"]
        if category not in valid_categories:
            return "Error: Access to this category is restricted."
            
        filename = title.lower().replace(" ", "-").replace("/", "-") + ".md"
        target_dir = os.path.join(memory_path, category)
        file_path = os.path.join(target_dir, filename)
        
        if not _is_path_safe(memory_path, file_path):
            return "Error: Security violation. Attempted to escape the memory vault."
            
        if os.path.exists(file_path):
            return "Error: This document already exists."
            
        tags_str = f"[{', '.join(tags)}]" if tags else "[]"
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        frontmatter = f"---\ntitle: {title}\ncategory: {category}\ntags: {tags_str}\nsummary: \"{summary}\"\ncreated: {now}\nupdated: {now}\n---\n\n# {title}\n\n{content}\n"
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
            return f"Successfully created wiki page [[{category}/{filename}]]."
        except Exception:
            return "Error: Failed to write file."
