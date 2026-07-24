<p align="center">
  <img src="docs/assets/talentme-logo.svg" alt="TalentMe Logo" width="320">
</p>



<p align="center">
  <strong>A Local-First Personal Career Memory & ML Interview Coach for AI Assistants</strong>
</p>

<p align="center">
  <a href="https://talentme.airsota.com/resources/blogs">Blog</a> | 
  <a href="docs/">Documentation</a> | 
  <a href="https://github.com/airsota/talentme-mcp/issues">Roadmap</a> | 
  <a href="https://github.com/airsota/talentme-mcp/issues">Community Discussion</a>
</p>

<p align="center">
  <a href="https://github.com/airsota/talentme-mcp/stargazers">
    <img src="https://img.shields.io/github/stars/airsota/talentme-mcp?style=flat-square&logo=github&color=F5A623" alt="GitHub Repo stars">
  </a>
  <a href="https://modelcontextprotocol.io">
    <img src="https://img.shields.io/badge/MCP-Server-orange?style=flat-square" alt="Model Context Protocol">
  </a>
  <a href="https://github.com/airsota/talentme-mcp/graphs/commit-activity">
    <img src="https://img.shields.io/github/commit-activity/m/airsota/talentme-mcp?style=flat-square&logo=git&color=8B5CF6" alt="GitHub commit activity">
  </a>
  <a href="https://github.com/airsota/talentme-mcp/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/airsota/talentme-mcp?style=flat-square&color=EF4444" alt="License">
  </a>
</p>

---

## 🌟 What is TalentMe MCP?

**TalentMe MCP** is a **Local-First** professional learning memory system designed for Machine Learning and Software Engineering interview preparation. Acting as a bridge between your local knowledge base and your AI assistant (Cursor, Claude Desktop, Trae, Antigravity, Kiro, Codex), it implements the [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern to track your learning journey, automate mock interviews, and structure your career growth. Learn more and manage your account at [TalentMe](https://talentme.airsota.com).

With TalentMe, your AI agent gains **long-term context** about your projects, skills, and areas of growth, enabling hyper-personalized coaching without leaking your notes to the public internet.

---

## 🚀 Key Features

*   **Local-First Privacy**: Your notes, practice logs, and templates are stored locally in Markdown and an Obsidian-compatible structure.
*   **Dual-Source Intelligence**: Connects to the [TalentMe Cloud Platform](https://talentme.airsota.com) to dynamically fetch specialized interview prompt steering files and expert evaluation workflows.
*   **Structured Vault & SQLite Engine**: Combines standard folders (`concepts/`, `journal/`, `resumes/`) with a local SQLite database for spaced repetition (Ebbinghaus curve) and mastery tracking.
*   **Zero-Sync Fast Startup**: Starting or refreshing the MCP server is 100% local and instantaneous, bypassing cloud requests to prevent delays.
*   **Auto IDE Registration**: One-click configuration registers the server with Cursor, Claude Desktop, Trae, Antigravity, Kiro, and Codex.

---

## 🛠️ CLI Commands

TalentMe comes with an intuitive command-line interface:

### 1. `talentme setup`
Your initial onboarding assistant.
*   Guides you to choose where to save your learning memory folder.
*   Connects your account details (Email, License Key).
*   Configures AI write mode behaviors (`auto`, `semi-auto`, or `manual`).
*   Configures and registers the MCP server inside your IDEs automatically.

### 2. `talentme start`
Starts the background Model Context Protocol (MCP) server.
*   **Automatic**: You rarely need to run this manually; your IDE launches it in the background when it boots.
*   **Fast**: Uses a local skeleton builder if a path is empty, completely avoiding blocking network calls.

### 3. `talentme update`
Upgrades the software package to the latest version.
*   Pulls latest code updates and re-installs dependencies in place.
*   Offers an optional, interactive cloud template synchronization loop.

### 4. `talentme sync`
Explicitly syncs templates and professional skills from the cloud on-demand.

---

## 📂 Vault Structure

TalentMe initializes an Obsidian-compatible local memory folder with the following layout:

```text
my_memory/
├── concepts/             # Atomic knowledge points (e.g., Transformers, PyTorch, Caching)
├── journal/              # Daily practice notes and study logs
├── projects/             # Deep dives into your past system implementations
├── resumes/              # LaTeX/PDF/Markdown resumes and version histories
├── roles/                # Job descriptions and match reports
├── plans/                # Spaced-repetition study paths and 14-day sprint plans
├── .skills/              # Local protocol prompting rules (e.g., llm-wiki, mock-interview)
├── template.json         # Bootstrapping metadata tracking
└── memory.db             # SQLite engine tracking knowledge decay and mastery levels
```

---

## 🎬 Getting Started

### Step 1: Install the Package
Install `talentme-mcp` into your preferred Python environment (we recommend creating a dedicated virtual environment):

```bash
python3 -m venv ~/.talentme_venv
source ~/.talentme_venv/bin/activate
pip install git+https://github.com/airsota/talentme-mcp.git
```

### Step 2: Run Setup
Initialize your memory directory and configure your IDEs:

```bash
talentme setup
```
*Follow the interactive prompt to set your memory directory, email, license key, and behavior configurations.*

> [!TIP]
> **Need a License Key?** Sign up on the [TalentMe](https://talentme.airsota.com) official website to generate your key, access premium knowledge bases, and activate your personal career vault.

### Step 3: Use with Your AI Assistant
Open your memory directory in Cursor/Claude/Antigravity and start building you own knowledge base!

> 💬 **Example Prompt**:
> *"Review my notes on Transformer self-attention. Ask me 3 hard questions about computational complexity, then log my responses to today's journal."*

---

## ⚙️ Advanced Integration

If the automatic IDE registration is skipped, you can manually register the MCP server by adding this JSON snippet to your IDE's MCP settings:

```json
{
  "mcpServers": {
    "talentme": {
      "command": "/Users/YOUR_USERNAME/.talentme_venv/bin/talentme",
      "args": ["start"]
    }
  }
}
```

### Configuration Locations
*   **Claude Code**: `~/.claude.json`
*   **Cursor**: `~/Library/Application Support/Cursor/User/globalStorage/mcpServers.json`
*   **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Antigravity / Gemini IDE**: `~/.gemini/config/mcp_config.json`

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.


