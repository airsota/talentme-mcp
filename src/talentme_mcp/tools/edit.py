import os
from mcp.server.fastmcp import FastMCP

def _is_path_safe(memory_path: str, requested_path: str) -> bool:
    if not memory_path:
        return False
    real_allowed = os.path.realpath(memory_path)
    real_requested = os.path.realpath(requested_path)
    return real_requested.startswith(real_allowed)

def setup_edit_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def update_wiki_page(page_name: str, mode: str, new_content: str) -> str:
        """
        Modify an existing local wiki page by appending or overwriting.
        Args:
            page_name: Name of the page (without .md extension, or with it).
            mode: 'append' or 'overwrite'.
            new_content: The markdown content to inject.
        """
        if not memory_path:
            return "Error: Memory path not configured."
            
        if mode not in ["append", "overwrite"]:
            return "Error: mode must be 'append' or 'overwrite'."
            
        if not page_name.endswith('.md'):
            page_name += '.md'
            
        # Recursive search to find the file
        target_path = None
        for root, _, files in os.walk(memory_path):
            # SECURITY: Skip directories that resolve outside the vault
            if not _is_path_safe(memory_path, root):
                continue
            if page_name in files:
                target_path = os.path.join(root, page_name)
                break
                
        if not target_path:
            return f"Error: Page '{page_name}' does not exist. Use the create_wiki_page tool to create it first."
        
        # SECURITY: Validate resolved path is within memory vault
        if not _is_path_safe(memory_path, target_path):
            return "Error: Security violation. Path escapes the memory vault."
            
        try:
            write_mode = 'a' if mode == 'append' else 'w'
            with open(target_path, write_mode, encoding='utf-8') as f:
                if mode == 'append':
                    f.write("\n\n" + new_content)
                else:
                    f.write(new_content)
                    
            return f"Successfully {mode}ed page: {page_name}."
            
        except Exception as e:
            return f"Error updating page: {str(e)}"
