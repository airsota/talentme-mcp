import os
import sys
import shutil
from pathlib import Path
from click.testing import CliRunner

# Add the src directory to sys.path
sys.path.insert(0, os.path.abspath('src'))

# Mock the mcp server module imports that might fail in a script
from unittest.mock import MagicMock
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()
sys.modules['talentme_mcp.server'] = MagicMock()

import talentme_mcp.cli as cli

def test_setup():
    runner = CliRunner()
    
    # 1. Prepare clean directories
    test_workspace = os.path.abspath("test_workspace")
    if os.path.exists(test_workspace):
        shutil.rmtree(test_workspace)
    os.makedirs(test_workspace)
    
    # Save current directory to revert later
    old_cwd = os.getcwd()
    os.chdir(test_workspace)
    
    try:
        # Create a mock home directory to test global symlinks
        mock_home = os.path.join(test_workspace, "mock_home")
        os.makedirs(mock_home)
        # Mock Path.home() using patch
        from unittest.mock import patch
        with patch.object(Path, 'home', return_value=Path(mock_home)):
            # Mock click.prompt inputs:
            # 1. memory path: ./mock_memory
            # 2. api url: http://localhost:8000
            # 3. license key: test-key
            # Note: During mock setup, interactive template choice prompt gets called.
            # We supply inputs to answer all prompts.
            inputs = "./mock_memory\nhttp://localhost:8000\ntest-key\nall\ny\ny\n"
            
            # Pre-create mock_memory and its .skills directory
            os.makedirs("mock_memory/.skills/some-skill", exist_ok=True)
            with open("mock_memory/.skills/some-skill/SKILL.md", "w") as f:
                f.write("# Mock Skill\n")
            
            # Run the command
            result = runner.invoke(cli.main, ['setup'], input=inputs)
            print(result.output)
            assert result.exit_code == 0, f"Setup command failed with error: {result.exception}"
            
            # 2. Verify IDE Bootstrap files
            rule_files = [
                ".cursorrules",
                "CLAUDE.md",
                "GEMINI.md",
                "AGENTS.md",
                ".hermes.md",
                ".cursor/rules/talentme.mdc",
                ".windsurf/rules/talentme.md",
                ".agent/rules/talentme.md",
                ".agent/workflows/talentme.md",
                ".github/copilot-instructions.md"
            ]
            for f in rule_files:
                assert os.path.exists(f) or os.path.islink(f), f"Missing steering file: {f}"
            print("✅ All 10 steering rule files generated successfully.")
            
            # 3. Verify symlinks
            local_paths = [
                ".claude/skills",
                ".cursor/skills",
                ".windsurf/skills",
                ".agents/skills",
                ".pi/skills",
                ".kiro/skills"
            ]
            for p in local_paths:
                skill_link = os.path.join(p, "some-skill")
                assert os.path.islink(skill_link), f"Missing local symlink: {skill_link}"
                
            global_paths = [
                "mock_home/.claude/skills",
                "mock_home/.gemini/skills",
                "mock_home/.gemini/antigravity/skills",
                "mock_home/.gemini/antigravity-ide/skills",
                "mock_home/.codex/skills",
                "mock_home/.hermes/skills",
                "mock_home/.openclaw/skills",
                "mock_home/.copilot/skills",
                "mock_home/.trae/skills",
                "mock_home/.trae-cn/skills",
                "mock_home/.kiro/skills",
                "mock_home/.pi/agent/skills",
                "mock_home/.agents/skills"
            ]
            for p in global_paths:
                skill_link = os.path.join(p, "some-skill")
                assert os.path.islink(skill_link), f"Missing global symlink: {skill_link}"
            print("✅ All local and global symlinks created successfully.")
            
    finally:
        os.chdir(old_cwd)
        print("Test complete.")

if __name__ == "__main__":
    test_setup()
