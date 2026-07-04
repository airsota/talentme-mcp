import os
from mcp.server.fastmcp import FastMCP

from .tools.infrastructure import setup_infrastructure_tools

from .tools.local import setup_local_tools
from .tools.guide import setup_guide_tool
from .tools.review import setup_review_tool
from .tools.status import setup_status_tool
from .tools.interview import setup_interview_tool
from .tools.import_feedback import setup_import_feedback_tool
from .tools.lint import setup_lint_tool
from .tools.edit import setup_edit_tool
from .tools.p2_tools import setup_calendar_tool, setup_report_issue_tool
from .tools.search import setup_search_tool
from .tools.learn import setup_learn_tool
from .tools.assess import setup_assess_tool

def create_server(api_url: str, license_key: str, memory_path: str = None, email: str = None) -> FastMCP:
    """Create and configure the FastMCP server."""
    mcp = FastMCP("TalentMe (/tm)")

    # 1. Setup Infrastructure / Authorization Tools
    setup_infrastructure_tools(mcp, api_url, license_key, email)
    
    
    
    # 3. Setup Local Context & Wiki Management Tools (if memory path is provided)
    if memory_path:
        setup_local_tools(mcp, memory_path)
        setup_guide_tool(mcp, memory_path)
        setup_review_tool(mcp, memory_path)
        setup_status_tool(mcp, memory_path)
        setup_interview_tool(mcp, memory_path)
        setup_import_feedback_tool(mcp, memory_path)
        setup_lint_tool(mcp, memory_path)
        setup_edit_tool(mcp, memory_path)
        setup_calendar_tool(mcp, memory_path)
        
    setup_report_issue_tool(mcp, api_url, email)

    # 4. Setup Unified Dual-Source Tools
    setup_search_tool(mcp, api_url, license_key, memory_path, email)
    setup_learn_tool(mcp, api_url, license_key, memory_path, email)
    setup_assess_tool(mcp, api_url, license_key, email)

    return mcp
