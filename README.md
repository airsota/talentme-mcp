<p align="center">
  <img src="https://raw.githubusercontent.com/airsota/talentme-mcp/main/docs/assets/talentme-logo.png" alt="TalentMe Logo" width="55%" onerror="this.src='https://img.shields.io/badge/TalentMe-MCP--Server-blue?style=for-the-badge&logo=appveyor'; this.width='30%';">
</p>

<p align="center">
  <strong>A Local-First Personal Career Memory & ML Interview Coach for AI Assistants</strong>
</p>

<p align="center">
  <a href="https://github.com/airsota/talentme-mcp/blob/main/README.md">Blog</a> | 
  <a href="https://github.com/airsota/talentme-mcp/blob/main/docs/">Documentation</a> | 
  <a href="https://github.com/airsota/talentme-mcp/issues">Roadmap</a> | 
  <a href="https://github.com/airsota/talentme-mcp/issues">Community Discussion</a>
</p>

<p align="center">
  <a href="https://github.com/airsota/talentme-mcp/stargazers">
    <img src="https://img.shields.io/github/stars/airsota/talentme-mcp?style=flat-square&logo=github&color=F5A623" alt="GitHub Repo stars">
  </a>
  <a href="https://pypi.org/project/talentme-mcp/">
    <img src="https://img.shields.io/pypi/v/talentme-mcp?style=flat-square&logo=pypi&logoColor=white&color=0073B7" alt="PyPI Version">
  </a>
  <a href="https://pypistats.org/packages/talentme-mcp">
    <img src="https://img.shields.io/pypi/dm/talentme-mcp?style=flat-square&logo=pypi&logoColor=white&color=10B981" alt="PyPI Downloads">
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

**TalentMe MCP** is a **Local-First** professional learning memory system designed for Machine Learning and Software Engineering interview preparation. Acting as a bridge between your local knowledge base and your AI assistant (Cursor, Claude Desktop, Windsurf, Trae, Antigravity), it implements the [LLM Wiki](https://github.com/karpathy/llm-wiki) pattern to track your learning journey, automate mock interviews, and structure your career growth.

With TalentMe, your AI agent gains **long-term context** about your projects, skills, and areas of growth, enabling hyper-personalized coaching without leaking your notes to the public internet.

---

## 🚀 Key Features

*   **Local-First Privacy**: Your notes, practice logs, and templates are stored locally in Markdown and an Obsidian-compatible structure.
*   **Dual-Source Intelligence**: Connects to the TalentMe Cloud API to dynamically fetch specialized interview prompt steering files and expert evaluation workflows.
*   **Structured Vault & SQLite Engine**: Combines standard folders (`concepts/`, `journal/`, `resumes/`) with a local SQLite database for spaced repetition (Ebbinghaus curve) and mastery tracking.
*   **Zero-Sync Fast Startup**: Starting or refreshing the MCP server is 100% local and instantaneous, bypassing cloud requests to prevent delays.
*   **Auto IDE Registration**: One-click configuration registers the server with Cursor, Claude Desktop, Windsurf, Trae, and Antigravity.

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

### Step 3: Use with Your AI Assistant
Open your memory directory in Cursor/Claude and start chatting!

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
*   **Cursor**: `~/Library/Application Support/Cursor/User/globalStorage/mcpServers.json`
*   **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Windsurf**: `~/.codeium/windsurf/mcp_config.json`

---

## ⚖️ License

We license TalentMe MCP under the **MIT License**. 

### Why MIT?
The Model Context Protocol (MCP) ecosystem thrives on open integration. The **MIT License** is the industry standard for client packages and developer plugins because:
*   It is **highly permissive**, allowing anyone to use, copy, modify, and integrate the tool into their workspaces or teams without restrictions.
*   It encourages community contributions and pull requests to build a robust ecosystem.
*   It protects the authors by including standard "no warranty" liability protections.

For more details, see the [LICENSE](file:///home/suiyaoc/TalentMe/talentme-mcp/LICENSE) file in the repository.

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=airsota/talentme-mcp&type=Date)](https://star-history.com/#airsota/talentme-mcp&Date)
