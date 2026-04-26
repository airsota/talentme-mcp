import click
import os
import sqlite3
import json
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from .server import create_server

CONFIG_FILE = Path.home() / ".talentme_config.json"

def save_config(memory_path, api_url, license_key):
    config = {
        "memory_path": memory_path,
        "api_url": api_url,
        "license_key": license_key
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    # SECURITY: Restrict file permissions to current user only (600)
    os.chmod(CONFIG_FILE, 0o600)

def load_config():
    # Priority: Environment variables -> Config file
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    # Override with env vars if present for production safety
    if os.environ.get("TALENTME_LICENSE_KEY"):
        config["license_key"] = os.environ.get("TALENTME_LICENSE_KEY")
    if os.environ.get("TALENTME_API_URL"):
        config["api_url"] = os.environ.get("TALENTME_API_URL")
    if os.environ.get("TALENTME_MEMORY_PATH"):
        config["memory_path"] = os.environ.get("TALENTME_MEMORY_PATH")
        
    return config

def init_memory_structure(memory_path: str, template_name: str = None):
    """Initialize the LLM Wiki structure and optionally fetch a specific template."""
    click.echo(f"Initializing/Syncing Memory at {memory_path}...", err=True)
    
    # Core directories based on LLM Wiki pattern
    dirs = [
        "concepts", "entities", "skills", "references", 
        "synthesis", "journal", "projects", "_raw", "_meta", ".skills"
    ]
    for d in dirs:
        os.makedirs(os.path.join(memory_path, d), exist_ok=True)
        
    # Initialize SQLite DB for structured logging
    db_path = os.path.join(memory_path, 'memory.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            topic TEXT,
            summary TEXT,
            mastery_level INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    
    # Initialize index.md
    index_path = os.path.join(memory_path, 'index.md')
    if not os.path.exists(index_path):
        with open(index_path, 'w') as f:
            f.write("# Wiki Index\n\n## Concepts\n\n## Entities\n\n## Skills\n")
            
    # Initialize log.md
    log_path = os.path.join(memory_path, 'log.md')
    if not os.path.exists(log_path):
        with open(log_path, 'w') as f:
            f.write("## Log\n\n")
            
    # Try to fetch specified template from Cloud API (ONLY if requested)
    if not template_name:
        return

    dest_skill = os.path.join(memory_path, ".skills", template_name)
    
    api_url = getattr(sys, '_talentme_api_url', None)
    license_key = getattr(sys, '_talentme_license_key', None)

    if api_url and license_key:
        try:
            import requests
            click.echo(f"[*] Fetching template '{template_name}' from cloud...", err=True)
            headers = {"Authorization": f"Bearer {license_key}"}
            resp = requests.get(f"{api_url}/api/templates/get/{template_name}", headers=headers, timeout=10)
            if resp.status_code == 200:
                files = resp.json().get("files", {})
                if not files:
                    click.echo(f"Warning: Template '{template_name}' is empty or not found on server.", err=True)
                    return
                
                # If template already exists, we should probably warn or handle it in the caller
                # For simplicity here, we write files (overwrite individual files if they changed)
                for rel_path, content in files.items():
                    full_dest = os.path.join(dest_skill, rel_path)
                    os.makedirs(os.path.dirname(full_dest), exist_ok=True)
                    with open(full_dest, 'w', encoding='utf-8') as f:
                        f.write(content)
                click.echo(f"✅ Successfully installed/updated '{template_name}' from cloud.", err=True)
        except Exception as e:
            click.echo(f"Warning: Could not fetch cloud template: {e}", err=True)

@click.group()
def main():
    """TalentMe - Your Agentic Interview Prep Companion.
    
    In your IDE (Cursor/Claude), use the prefix '/talentme' or '/tm' 
    to trigger your private memory assistant.
    """
    pass

def interactive_template_sync(memory_path: str, api_url: str, license_key: str):
    """Helper to list and sync templates interactively."""
    sys._talentme_api_url = api_url
    sys._talentme_license_key = license_key
    
    try:
        import requests
        click.echo(f"[*] Fetching available templates from {api_url}...", err=True)
        headers = {"Authorization": f"Bearer {license_key}"}
        resp = requests.get(f"{api_url}/api/templates/list", headers=headers, timeout=10)
        if resp.status_code != 200:
            click.echo(f"Error: Could not list templates ({resp.status_code})")
            return
            
        templates = resp.json().get("templates", [])
        if not templates:
            click.echo("No templates found on cloud.")
            return
            
        click.echo("\nAvailable Cloud Templates:")
        for i, t in enumerate(templates):
            status = " [installed]" if os.path.exists(os.path.join(memory_path, ".skills", t)) else ""
            click.echo(f" {i+1}. {t}{status}")
            
        choice = click.prompt("\nWhich template(s) would you like to install? (Number, 'all', or 'none')", default="none")
        
        if choice == "none":
            return
        elif choice == "all":
            for t in templates:
                init_memory_structure(memory_path, t)
        else:
            try:
                # Support comma separated numbers: "1,2"
                choices = [c.strip() for c in choice.split(",")]
                for c in choices:
                    idx = int(c) - 1
                    if 0 <= idx < len(templates):
                        init_memory_structure(memory_path, templates[idx])
            except ValueError:
                click.echo("Invalid input. Skipping template installation.")
                
    except Exception as e:
        click.echo(f"Template sync failed: {e}")

@main.command()
def update():
    """Update TalentMe to the latest version via git."""
    click.echo("=== Updating TalentMe ===")
    try:
        repo_dir = Path(__file__).parent.parent.parent
        if not (repo_dir / ".git").exists():
            click.echo("Error: This installation does not appear to be a git repository. Please install via 'git clone'.")
            return

        click.echo(f"Pulling latest changes in {repo_dir}...")
        subprocess.run(["git", "pull"], cwd=repo_dir, check=True)
        
        click.echo("Re-installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_dir, check=True)
        
        click.echo("\n✅ Software successfully updated!")
        click.echo("💡 PRO TIP: You can now use '/talentme' or '/tm' in your IDE to wake up the assistant.")
        
        # Now ask if they want to sync templates
        config = load_config()
        if config.get("memory_path") and click.confirm("\nWould you like to sync/update cloud templates as well?"):
            interactive_template_sync(config["memory_path"], config["api_url"], config["license_key"])
            
        click.echo("\n[IMPORTANT] Please restart your MCP server/IDE to apply new instructions.")
    except Exception as e:
        click.echo(f"Update failed: {e}")

@main.command()
@click.option('--memory', type=click.Path(), help='Path to your local memory directory.')
@click.option('--api-url', type=str, help='URL of the TalentMe Cloud API.')
@click.option('--license-key', type=str, help='Your TalentMe License Key.')
def sync(memory, api_url, license_key):
    """Interactively sync core protocols and templates from cloud to local memory."""
    config = load_config()
    memory_path = memory or config.get("memory_path")
    if not memory_path:
        click.echo("Error: No memory path provided and none remembered. Please run 'setup' first.")
        return
    
    memory_path = os.path.abspath(os.path.expanduser(memory_path))
    api_url = api_url or config.get("api_url")
    license_key = license_key or config.get("license_key")
    
    interactive_template_sync(memory_path, api_url, license_key)

@main.command()
@click.option('--init-memory', type=click.Path(), help='Initialize or connect to a local memory directory.')
@click.option('--api-url', type=str, help='URL of the TalentMe Cloud API.')
@click.option('--license-key', type=str, help='Your TalentMe License Key.')
def start(init_memory, api_url, license_key):
    """Start the TalentMe MCP Server."""
    config = load_config()
    
    # Priority: Flag > Config > Default
    final_memory = init_memory or config.get("memory_path")
    final_api = api_url or config.get("api_url", "https://api-talentme.airsota.com")
    final_key = license_key or config.get("license_key", "test-key")

    if not final_memory:
        click.echo("Error: No memory path provided. Please run 'setup' or use --init-memory.")
        return

    final_memory = os.path.abspath(os.path.expanduser(final_memory))

    # 1. Resolve internal skills path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    skills_path = os.path.join(base_dir, 'data', 'skills')
    
    # Store API info in sys for tools to pick up
    sys._talentme_api_url = final_api
    sys._talentme_license_key = final_key

    # 2. Handle Memory Initialization (Silent)
    init_memory_structure(final_memory, template_name=None)
    
    click.echo(f"[*] TalentMe MCP Server starting...", err=True)
    click.echo(f"[*] Memory: {final_memory}", err=True)
    
    mcp_server = create_server(final_api, final_key, skills_path, final_memory)
    mcp_server.run()

@main.command()
def setup():
    """Interactive setup to configure TalentMe and register with IDEs."""
    click.echo("=== TalentMe Onboarding & Setup ===")
    
    # 1. Ask for Memory Path
    default_memory = str(Path(os.getcwd()).parent / "my_memory")
    memory_path = click.prompt("Where should your local learning memory be stored?", default=default_memory)
    memory_path = os.path.abspath(os.path.expanduser(memory_path))
    
    # 2. Ask for API details
    api_url = click.prompt("Cloud API URL", default="https://api-talentme.airsota.com")
    license_key = click.prompt("Your License Key", default="test-key")
    
    # Save config
    save_config(memory_path, api_url, license_key)

    # 3. Create Memory Directory structure
    init_memory_structure(memory_path, template_name=None)
    
    # 4. Interactive Template Choice
    interactive_template_sync(memory_path, api_url, license_key)
    
    # 4. Configure IDEs
    talentme_path = sys.executable.replace("python", "talentme") # Heuristic for venv bin
    if not os.path.exists(talentme_path):
        talentme_path = "talentme" # Fallback to naked command
        
    mcp_config = {
        "talentme": {
            "command": talentme_path,
            "args": ["start"] # SECURE: No sensitive arguments passed here
        }
    }
    
    system = platform.system()
    home = Path.home()
    
    # Define possible IDE config paths
    ide_paths = {
        "Claude Desktop": None,
        "Cursor": None
    }
    
    if system == "Darwin": # Mac
        ide_paths["Claude Desktop"] = home / "Library/Application Support/Claude/claude_desktop_config.json"
        ide_paths["Cursor"] = home / "Library/Application Support/Cursor/User/globalStorage/mcpServers.json"
    elif system == "Windows":
        appdata = Path(os.environ.get("APPDATA", ""))
        ide_paths["Claude Desktop"] = appdata / "Claude/claude_desktop_config.json"
        ide_paths["Cursor"] = appdata / "Cursor/User/globalStorage/mcpServers.json"
    elif system == "Linux":
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
        ide_paths["Claude Desktop"] = config_home / "Claude/claude_desktop_config.json"
        ide_paths["Cursor"] = config_home / "Cursor/User/globalStorage/mcpServers.json"

    click.echo("\n=== IDE Integration ===")
    
    configured_any = False
    for ide_name, config_path in ide_paths.items():
        if config_path and (config_path.exists() or click.confirm(f"Do you want to configure {ide_name}?")):
            try:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        data = json.load(f)
                else:
                    data = {}
                
                if "mcpServers" not in data:
                    data["mcpServers"] = {}
                
                data["mcpServers"]["talentme"] = mcp_config["talentme"]
                
                # Ensure directory exists
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(data, f, indent=2)
                click.echo(f"✅ Successfully updated {ide_name} configuration!")
                configured_any = True
            except Exception as e:
                click.echo(f"❌ Failed to update {ide_name} config: {e}")

    # 5. Generate IDE Bootstrap Files (.cursorrules, AGENTS.md)
    click.echo("\n=== Generating AI Bootstrap Files ===")
    
    # .cursorrules for Cursor
    cursor_rules_content = f"""# TalentMe Cursor Rules
When the user uses the prefix '/talentme' or '/tm', you MUST:
1. Call the 'list_agent_skills' tool to see available memory skills.
2. Read the appropriate skill instructions (usually 'wiki-query').
3. Use the local wiki tools to search the user's private memory at {memory_path}.
4. Provide an answer based ONLY on the private memory content.
5. NEVER return absolute file paths. Use [[Page Name]] instead.
"""
    with open(".cursorrules", "w", encoding='utf-8') as f:
        f.write(cursor_rules_content)
    click.echo("✅ Generated .cursorrules")

    # AGENTS.md for Antigravity / Gemini
    agents_md_content = f"""# TalentMe Agent Protocol
This project is connected to a TalentMe Private Memory Vault.

## Commands
- `/talentme <query>`: Search your private memory for answers.
- `/tm <query>`: Shorthand for /talentme.

## Guidelines
- Prioritize local knowledge over general training data for these commands.
- Use [[wikilinks]] for page references.
- Private Memory Path: {memory_path}
"""
    with open("AGENTS.md", "w", encoding='utf-8') as f:
        f.write(agents_md_content)
    click.echo("✅ Generated AGENTS.md")

    # 6. Provide AI Prompt for Copy-Paste
    click.echo("\n" + "="*40)
    click.echo("🤖 AI PROMPT (Copy-Paste this to your AI Assistant):")
    click.echo("="*40)
    prompt = f"""
Please help me update my MCP configuration to include the TalentMe server. 
I am using {system}. My config should look like this:

{json.dumps(mcp_config, indent=2)}

Also, please acknowledge that you have read .cursorrules and AGENTS.md, and you are ready to handle '/talentme' commands.
"""
    click.echo(prompt)
    click.echo("="*40)

    # 7. Symlink skills to agent directories (Native Skill support)
    click.echo("\n=== Installing Native Skills (Symlinking) ===")
    local_skills_path = os.path.join(memory_path, ".skills")
    
    agent_paths = [
        Path.home() / ".gemini/antigravity/skills",
        Path.home() / ".claude/skills",
        Path.home() / ".cursor/skills"
    ]
    
    if os.path.exists(local_skills_path):
        for agent_path in agent_paths:
            try:
                agent_path.mkdir(parents=True, exist_ok=True)
                for skill_name in os.listdir(local_skills_path):
                    src = os.path.join(local_skills_path, skill_name)
                    if os.path.isdir(src):
                        dst = agent_path / skill_name
                        if dst.exists() or dst.is_symlink():
                            if dst.is_symlink():
                                dst.unlink()
                            else:
                                continue # Skip real dirs to be safe
                        os.symlink(src, dst)
                click.echo(f"✅ Linked skills to {agent_path}")
            except Exception as e:
                click.echo(f"⚠️  Could not link to {agent_path}: {e}")

    click.echo("\n=== Setup Complete! ===")
    if configured_any:
        click.echo("Please RESTART your IDE for the changes to take effect.")
    click.echo("You can now use '/talentme' or '/tm' in your IDE to dominate your ML interviews.")

@main.command()
@click.option('--memory', type=click.Path(), required=True, help='Path to your local memory directory.')
@click.option('--api-url', type=str, default='https://api-talentme.airsota.com', help='URL of the TalentMe Cloud API.')
@click.option('--license-key', type=str, default='test-key', help='Your TalentMe License Key.')
def sync(memory, api_url, license_key):
    """Force sync core protocols and templates from cloud to local memory."""
    memory_path = os.path.abspath(os.path.expanduser(memory))
    if not os.path.exists(memory_path):
        click.echo(f"Error: Memory path {memory_path} does not exist. Please run 'setup' first.")
        return

    # Store API info in sys for init_memory_structure to pick up
    sys._talentme_api_url = api_url
    sys._talentme_license_key = license_key
    
    click.echo(f"=== Syncing templates for {memory_path} ===")
    
    # We want to force sync, so we temporarily remove the local llm-wiki if it exists
    # but only if it's a protocol (we don't want to delete user data, but .skills/llm-wiki is a protocol)
    dest_skill = os.path.join(memory_path, ".skills", "llm-wiki")
    if os.path.exists(dest_skill):
        shutil.rmtree(dest_skill)
        
    init_memory_structure(memory_path)
    click.echo("Done!")

if __name__ == "__main__":
    main()
