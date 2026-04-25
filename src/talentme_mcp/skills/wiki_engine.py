import os
import re
from datetime import datetime
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

def setup_wiki_engine_skills(mcp: FastMCP, memory_path: str):
    
    @mcp.tool()
    def create_wiki_page(title: str, category: str, content: str, tags: List[str] = None, summary: str = "") -> str:
        """
        Create a new wiki page in the local memory.
        
        Args:
            title: The title of the page (e.g., "Transformer Architecture")
            category: The category (concepts, entities, skills, references, synthesis)
            content: The main markdown content.
            tags: List of tags for the page.
            summary: A brief 1-2 sentence summary for the frontmatter.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        valid_categories = ["concepts", "entities", "skills", "references", "synthesis", "journal", "projects"]
        if category not in valid_categories:
            return f"Error: Invalid category '{category}'. Valid categories are: {', '.join(valid_categories)}"
            
        # Sanitize filename
        filename = title.lower().replace(" ", "-").replace("/", "-") + ".md"
        
        # Determine path
        target_dir = os.path.join(memory_path, category)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)
        
        if os.path.exists(file_path):
            return f"Error: Page '{title}' already exists in category '{category}'."
            
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
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
                
            # Log to wiki log.md
            log_path = os.path.join(memory_path, "log.md")
            with open(log_path, "a", encoding='utf-8') as f:
                f.write(f"- [{now}] CREATE page=\"{category}/{filename}\" title=\"{title}\"\n")
                
            return f"Successfully created wiki page '{title}' at {category}/{filename}."
        except Exception as e:
            return f"Failed to create wiki page: {str(e)}"

    @mcp.tool()
    def search_local_wiki(query: str) -> str:
        """
        Search the user's local memory wiki for specific content using regex.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        results = []
        for root, _, files in os.walk(memory_path):
            if ".skills" in root or "_meta" in root or "_raw" in root:
                continue
            for file in files:
                if file.endswith(".md") and file != "log.md":
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if re.search(query, content, re.IGNORECASE):
                                rel_path = os.path.relpath(path, memory_path)
                                # Extract a small snippet
                                match = re.search(query, content, re.IGNORECASE)
                                start = max(0, match.start() - 100)
                                end = min(len(content), match.end() + 100)
                                snippet = content[start:end].replace("\n", " ")
                                results.append(f"### {rel_path}\n...{snippet}...\n")
                    except:
                        continue
        
        if not results:
            return f"No matches found for '{query}' in local memory."
            
        return f"Found {len(results)} matches in local memory:\n\n" + "\n".join(results[:10])

    @mcp.tool()
    def list_local_wiki_pages(category: Optional[str] = None) -> str:
        """
        List all pages in the user's local wiki memory, optionally filtered by category.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        pages = []
        target_dirs = [category] if category else ["concepts", "entities", "skills", "references", "synthesis", "journal", "projects"]
        
        for d in target_dirs:
            d_path = os.path.join(memory_path, d)
            if os.path.exists(d_path):
                for file in os.listdir(d_path):
                    if file.endswith(".md"):
                        pages.append(f"- [[{d}/{file}]]")
                        
        return f"Local Wiki Pages:\n\n" + "\n".join(pages) if pages else "No local wiki pages found yet."
