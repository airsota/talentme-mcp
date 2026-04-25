# TalentMe MCP Server

TalentMe is your agentic interview prep companion. This MCP server allows AI assistants (like Claude, Cursor, or Antigravity) to access your specialized knowledge base and track your learning progress in a local LLM Wiki.

## 🚀 Features

- **Cloud Knowledge Base**: Securely search a remote ML/Tech interview knowledge base.
- **LLM Wiki Memory**: Automatically initializes a professional Obsidian-style wiki structure for your local notes.
- **Learning Logs**: Track your mastery level and keep a daily learning journal.
- **Interactive Setup**: Simple CLI to configure your IDE and memory path.
- **Git Updates**: Keep your server up-to-date with a single command.

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ericchen12377/talentme-mcp.git
   cd talentme-mcp
   ```

2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## 🛠️ Setup (Recommended)

Run the interactive setup to configure your memory path and IDE integration automatically:

```bash
talentme setup
```

Follow the prompts to:
- Choose your local memory directory.
- Enter your Cloud API URL and License Key.
- Automatically register the tool in **Cursor**, **Claude Desktop**, or get a prompt for other AI IDEs.

## 🔄 Updating

To get the latest features and interview questions:

```bash
talentme update
```

## 📝 License

Proprietary. All rights reserved.
