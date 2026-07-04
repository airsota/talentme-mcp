import sys
sys.path.append('src')
from talentme_mcp.tools.learn import setup_learn_tool
from mcp.server.fastmcp import FastMCP
import inspect

mcp = FastMCP("Test")
setup_learn_tool(mcp, "http://example.com", "dummy_key", "/home/suiyaoc/TalentMe_Studio/self/memory_research", "test@test.com")

# Get the tool function directly
tool_func = None
for name, func in mcp._tool_manager.tools.items():
    if name == 'learn':
        tool_func = func.func
        break

if tool_func:
    res = tool_func("Flash Attention", "Deep technical dive")
    print(res)
