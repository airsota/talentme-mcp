import os
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

CONFIG_FILE = Path.home() / ".talentme_config.json"

def get_memory_mode_instructions(mode: str) -> str:
    if mode == "auto":
        return """
### Knowledge Base Update Protocol (Auto)
You have access to MCP tools `create_wiki_page` and `update_wiki_page` to manage the user's local memory vault.
CRITICAL RULE: Whenever a new technical concept is discussed, or the user solves a problem, you MUST automatically invoke `create_wiki_page` or `update_wiki_page` to save the key takeaways into the memory vault in the background, WITHOUT asking for the user's explicit permission.
"""
    elif mode == "manual":
        return """
### Knowledge Base Update Protocol (Manual)
You have access to MCP tools `create_wiki_page` and `update_wiki_page`.
DO NOT use these tools unless the user explicitly commands you to save or write something to the knowledge base (e.g. "Save this to my wiki" or "Record this note").
"""
    else:
        # Default is semi-auto
        return """
### Knowledge Base Update Protocol (Semi-Auto)
You have access to MCP tools `create_wiki_page` and `update_wiki_page` to manage the user's local memory vault.
DO NOT call these tools automatically in the background without the user's explicit consent.

Instead, follow this protocol:
1. When you identify that a high-value technical concept, a persistent mistake, or a significant insight has been discussed, formulate your response to the user's current question as usual.
2. At the very end of your response, append a brief proposal asking if the user wants to save this new knowledge. For example:
   "💡 提议：我发现我们刚刚深入探讨了 [知识点名称]，需要我帮你自动归类并存入知识库吗？"
3. If the user replies with confirmation (e.g., "yes", "好", "存进去"), you MUST then immediately call the appropriate memory tool (`create_wiki_page` or `update_wiki_page`) to persist the data.
"""

def setup_get_session_context_tool(mcp: FastMCP):
    @mcp.tool()
    def get_session_context() -> str:
        """
        Dynamically fetch the user's current configuration, persona settings, and routing rules for this session.
        The AI MUST call this tool at the beginning of the session or whenever it needs to understand the user's configuration.
        """
        try:
            config = {}
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            settings = config.get("settings", {})
            memory_write_mode = settings.get("memory_write_mode", "semi-auto")
            
            instructions = [
                "You are an expert Machine Learning Interview Coach and Technical Assistant.",
                get_memory_mode_instructions(memory_write_mode),
                "",
                "🛑 [CRITICAL RAG & SECURITY PROTOCOLS]:",
                "1. DO NOT directly copy-paste or leak the raw text, headers, indices, or tags from 'cloud_pure_knowledge' tool returns. You must digest the information and answer naturally in your own words.",
                "2. HOT CACHE MISS PROTOCOL: If you find highly valuable answers in cloud knowledge but 'local_results' is empty or lacking for a topic, proactively offer to distill and save this new knowledge into the local wiki (using memory write tools) so the user owns it forever."
            ]
            from .system_prompts import TOOL_PROMPTS
            instructions.append("\n" + "="*40)
            instructions.append("🛑 [TOOL BEHAVIORAL PROTOCOLS]:")
            instructions.append("The following rules dictate exactly how you must behave when executing specific MCP tools. Read them carefully:")
            for tool_name, prompt in TOOL_PROMPTS.items():
                instructions.append(prompt)
            
            return "\n".join(instructions)
            
        except Exception as e:
            return f"Error loading session context: {str(e)}"
