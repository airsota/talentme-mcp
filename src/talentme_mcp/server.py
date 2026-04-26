import os
from mcp.server.fastmcp import FastMCP
from .skills.kb_search import setup_kb_skills
from .skills.user_log import setup_user_log_skills
from .skills.agent_skills import setup_agent_skills
from .skills.wiki_engine import setup_wiki_engine_skills

def create_server(api_url: str, license_key: str, skills_path: str, memory_path: str = None) -> FastMCP:
    """Create and configure the FastMCP server."""
    mcp = FastMCP("TalentMe MCP")

    setup_kb_skills(mcp, api_url, license_key)
    
    if memory_path:
        setup_user_log_skills(mcp, memory_path)
        setup_wiki_engine_skills(mcp, memory_path)
        setup_agent_skills(mcp, skills_path, memory_path, api_url, license_key)
    else:
        setup_agent_skills(mcp, skills_path, api_url=api_url, license_key=license_key)

    return mcp
