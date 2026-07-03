import os
from mcp.server.fastmcp import FastMCP

from .tools.infrastructure import setup_infrastructure_tools
from .tools.cloud import setup_cloud_tools
from .tools.local import setup_local_tools
from .tools.search import setup_search_tool

def create_server(api_url: str, license_key: str, memory_path: str = None, email: str = None) -> FastMCP:
    """Create and configure the FastMCP server."""
    mcp = FastMCP("TalentMe (/tm)")

    # 1. Setup Infrastructure / Authorization Tools
    setup_infrastructure_tools(mcp, api_url, license_key, email)
    
    # 2. Setup Cloud Hybrid Search Engine Tools
    setup_cloud_tools(mcp, api_url, license_key, email)
    
    # 3. Setup Local Context & Wiki Management Tools (if memory path is provided)
    if memory_path:
        setup_local_tools(mcp, memory_path)

    # 4. Setup Unified Dual-Source Tools
    setup_search_tool(mcp, api_url, license_key, memory_path, email)

    return mcp
