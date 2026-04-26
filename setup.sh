#!/bin/bash
#
# TalentMe Setup — Configures MCP and AI Agent Bootstrap Files.
# Usage: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║          TalentMe — Agentic Setup                ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check if talentme CLI is installed
if ! command -v talentme &> /dev/null; then
    echo "[*] TalentMe CLI not found in PATH. Attempting to install in editable mode..."
    pip install -e .
fi

# Run the interactive setup
talentme setup

echo ""
echo "───────────────────────────────────────────────────"
echo " ✅ Setup Complete!"
echo ""
echo " Bootstrap files created in this directory:"
echo "   .cursorrules    → Instructions for Cursor"
echo "   AGENTS.md       → Instructions for Antigravity"
echo ""
echo " You can now use:"
echo "   /talentme <query>  in your AI chat"
echo "   /tm <query>        for quick lookup"
echo "───────────────────────────────────────────────────"
echo ""
