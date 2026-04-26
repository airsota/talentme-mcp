import os
import re
from datetime import datetime
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

def setup_wiki_engine_skills(mcp: FastMCP, memory_path: str):
    
    def _is_path_safe(requested_path: str) -> bool:
        """Hard security check: Ensure the requested path is within memory_path."""
        if not memory_path:
            return False
        real_allowed = os.path.realpath(memory_path)
        real_requested = os.path.realpath(requested_path)
        return real_requested.startswith(real_allowed)

    @mcp.tool()
    def read_wiki_page(category: str, filename: str) -> str:
        """
        Read the content of a wiki page from local memory.
        
        Args:
            category: The category (concepts, entities, etc.)
            filename: The filename (e.g., "transformer.md")
            
        SECURITY RULE: Access is restricted to the memory vault. Absolute paths are forbidden.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        # Hard construction of the path to prevent injection
        target_path = os.path.join(memory_path, category, filename)
        
        if not _is_path_safe(target_path):
            return "Error: Access denied. Path is outside of the allowed memory vault."
            
        if not os.path.exists(target_path):
            return f"Error: Page [[{category}/{filename}]] not found."
            
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "Error: Failed to read page due to a secure file access restriction."

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
            
        # Sanitize filename
        filename = title.lower().replace(" ", "-").replace("/", "-") + ".md"
        target_dir = os.path.join(memory_path, category)
        file_path = os.path.join(target_dir, filename)
        
        if not _is_path_safe(file_path):
            return "Error: Security violation. Attempted to escape the memory vault."
            
        if os.path.exists(file_path):
            return "Error: This document already exists."
            
        # Build frontmatter
        tags_str = f"[{', '.join(tags)}]" if tags else "[]"
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        frontmatter = f"""---
title: {title}
category: {category}
tags: {tags_str}
summary: "{summary}"
created: {now}
updated: {now}
---

# {title}

{content}
"""
        try:
            os.makedirs(target_dir, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
            return f"Successfully created wiki page [[{category}/{filename}]]."
        except Exception:
            return "Error: Failed to write file."

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
                if not _is_path_safe(root):
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
            if os.path.exists(d_path) and _is_path_safe(d_path):
                for file in os.listdir(d_path):
                    if file.endswith(".md"):
                        pages.append(f"- [[{d}/{file}]]")
                        
        return "\n".join(pages) if pages else "No accessible documents found."
