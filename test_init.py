import os
import sys
from unittest.mock import MagicMock

# Mock click and other things that might cause issues in a script
sys.modules['click'] = MagicMock()
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

# Add the src directory to sys.path
sys.path.insert(0, os.path.abspath('src'))

# We need to import init_memory_structure but its parent module imports .server
# So we mock .server before importing cli
sys.modules['talentme_mcp.server'] = MagicMock()

import talentme_mcp.cli as cli

test_path = 'test_memory_scratch'
if os.path.exists(test_path):
    import shutil
    shutil.rmtree(test_path)

cli.init_memory_structure(test_path)

print("\nStructure created:")
for root, dirs, files in os.walk(test_path):
    level = root.replace(test_path, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 4 * (level + 1)
    for f in files:
        print(f"{subindent}{f}")
