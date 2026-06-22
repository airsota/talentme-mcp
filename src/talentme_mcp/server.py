import os
from mcp.server.fastmcp import FastMCP

from .tools.infrastructure import setup_infrastructure_tools
from .tools.cloud import setup_cloud_tools
from .tools.local import setup_local_tools

def create_server(api_url: str, license_key: str, memory_path: str = None) -> FastMCP:
    """Create and configure the FastMCP server."""
    mcp = FastMCP("TalentMe (/tm)")

    # 1. Setup Infrastructure / Authorization Tools
    setup_infrastructure_tools(mcp, api_url, license_key)
    
    # 2. Setup Cloud Hybrid Search Engine Tools
    setup_cloud_tools(mcp, api_url, license_key)
    
    # 3. Setup Local Context & Wiki Management Tools (if memory path is provided)
    if memory_path:
        setup_local_tools(mcp, memory_path)

    return mcp
