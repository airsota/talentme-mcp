# 🚀 TalentMe MCP - Your Agentic Interview Coach

TalentMe is a **Local-First** professional learning memory system designed for ML/AI interview preparation. It follows the [LLM Wiki](https://github.com/karpathy/llm-wiki) pattern to help you build a persistent, structured, and searchable knowledge base of your own progress.

## 🌟 Core Philosophy

- **Local-First Privacy**: Your notes, journals, and progress are stored locally in Markdown.
- **Cloud-Powered Intelligence**: Specialized interview coaching skills are delivered dynamically via the TalentMe Cloud API.
- **Agentic Automation**: AI assistants (Cursor/Claude) use TalentMe as their "long-term memory" to track your mastery level.

---

## 🛠️ CLI Commands

The `talentme` command-line tool is your management console.

### 1. `talentme setup` (Onboarding)
Run this first to initialize your environment.
- Sets up the standard folder structure (`concepts/`, `journal/`, etc.)
- Connects to the Cloud API.
- **IDE Integration**: Automatically configures **Cursor** and **Claude Desktop**.
- **Interactive Templates**: Allows you to choose which professional protocols (like `llm-wiki`) to install from the cloud.

### 2. `talentme start` (The Engine)
This is the **MCP Server**.
- **Role**: It bridges your local memory with your AI assistant.
- **Usage**: You typically **don't** need to run this manually. Your IDE (Cursor) will start it automatically in the background.
- **Tools**: It provides tools like `search_local_wiki`, `create_wiki_page`, and `user_log` to the AI.

### 3. `talentme update` (Software Upgrader)
Keep your TalentMe engine up to date.
- Pulls the latest code from GitHub.
- **Smart Linkage**: After updating the code, it will ask if you'd like to sync your local templates with the latest cloud versions.

### 4. `talentme sync` (Template Manager)
Explicitly manage your local protocol templates.
- Fetches a live menu of templates from the cloud.
- Allows selective installation/update of skills like `llm-wiki` or specialized `interview-skills`.
- **Safe**: It never touches your actual notes or journals.

---

## 📂 Memory Structure

When you initialize TalentMe, it creates a structured Obsidian-compatible vault:

- `.skills/`: Local instruction templates (Protocols).
- `journal/`: Daily logs of what you learned.
- `concepts/`: Atomic notes on ML/AI topics.
- `entities/`: Structured data about companies/projects.
- `references/`: Raw sources and papers.
- `memory.db`: SQLite database for tracking mastery levels.

---

## 🤖 How to Use with Cursor

1. Run `talentme setup`.
2. Open your memory directory in Cursor.
3. Check the MCP tab in Cursor settings — `talentme` should be **Green**.
4. Start talking to the AI: *"Analyze my progress on Transformers and log today's practice."*

---

## 🌍 Cloud API Integration

The server at `api-talentme.airsota.com` provides:
- **Cloud Skills**: Specialized prompts that AI can use without taking up local space.
- **Template Distribution**: A library of protocols you can download on demand.
- **Developer Insights**: Anonymous metrics to help the TalentMe team improve the coaching experience.

---

## 📄 License
MIT License. Created by Suiyao.
