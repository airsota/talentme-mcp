#!/bin/bash
#
# TalentMe Setup — Always installs/upgrades latest version from Git & configures MCP and AI Agent Bootstrap Files.
# Usage: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║          TalentMe — Agentic Setup                ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Always fetch & install latest package version from Git (matching 'talentme update')
echo "[*] Fetching and installing latest TalentMe MCP package..."

if [ -d "$SCRIPT_DIR/.git" ]; then
    echo "[*] Local Git repository detected at $SCRIPT_DIR."
    echo "[*] Pulling latest commits..."
    git -C "$SCRIPT_DIR" pull || true
    echo "[*] Re-installing package from local repository..."
    python3 -m pip install --no-build-isolation -e "$SCRIPT_DIR"
else
    echo "[*] Upgrading package directly from official GitHub repository..."
    python3 -m pip install --upgrade --force-reinstall git+https://github.com/airsota/talentme-mcp.git
fi

echo "[+] TalentMe CLI package successfully installed/updated!"
echo ""

# Run the interactive setup
talentme setup

echo ""
echo "───────────────────────────────────────────────────"
echo " ✅ Setup Complete!"
echo ""
echo " Bootstrap files & MCP configs updated:"
echo "   CLAUDE.md       → Instructions for Claude Code & Claude Desktop"
echo "   .cursorrules    → Instructions for Cursor"
echo "   AGENTS.md       → Instructions for Antigravity & AI Agents"
echo "   ~/.claude.json  → Global MCP config for Claude Code CLI"
echo ""
echo " You can now use:"
echo "   /talentme <query>  in your AI chat"
echo "   /tm <query>        for quick lookup"
echo "───────────────────────────────────────────────────"
echo ""
