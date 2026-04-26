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

def init_memory_structure(memory_path: str):
    """Initialize the LLM Wiki structure in the specified path."""
    click.echo(f"Initializing Memory at {memory_path}...", err=True)
    
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
            
    # Copy core llm-wiki skill from package data to user memory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    package_skill = os.path.join(base_dir, 'data', 'skills', 'llm-wiki')
    dest_skill = os.path.join(memory_path, ".skills", "llm-wiki")
    
    if os.path.exists(package_skill) and not os.path.exists(dest_skill):
        try:
            shutil.copytree(package_skill, dest_skill)
            click.echo(f"Installed core llm-wiki protocol to {dest_skill}", err=True)
        except Exception as e:
            click.echo(f"Warning: Could not install llm-wiki skill: {e}", err=True)

@click.group()
def main():
    """TalentMe - Your Agentic Interview Prep Companion"""
    pass

@main.command()
def update():
    """Update TalentMe to the latest version via git."""
    click.echo("=== Updating TalentMe ===")
    try:
        # Check if the current directory or parent is a git repo
        # We assume the user is in the repo root or the package is installed in editable mode
        # from a git repo.
        repo_dir = Path(__file__).parent.parent.parent
        if not (repo_dir / ".git").exists():
            click.echo("Error: This installation does not appear to be a git repository. Please install via 'git clone'.")
            return

        click.echo(f"Pulling latest changes in {repo_dir}...")
        subprocess.run(["git", "pull"], cwd=repo_dir, check=True)
        
        click.echo("Re-installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_dir, check=True)
        
        click.echo("\nSuccessfully updated! Please restart your MCP server/IDE.")
    except Exception as e:
        click.echo(f"Update failed: {e}")
        click.echo("Please ensure 'git' is installed and you have network access.")

@main.command()
@click.option('--init-memory', type=click.Path(), help='Initialize or connect to a local memory directory.')
@click.option('--api-url', type=str, default='http://localhost:8000', help='URL of the TalentMe Cloud API.')
@click.option('--license-key', type=str, default='test-key', help='Your TalentMe License Key.')
def start(init_memory, api_url, license_key):
    """Start the TalentMe MCP Server."""
    # Resolve internal skills path automatically
    base_dir = os.path.dirname(os.path.abspath(__file__))
    skills_path = os.path.join(base_dir, 'data', 'skills')
    
    if init_memory:
        init_memory_structure(init_memory)
        click.echo("Memory initialized successfully.", err=True)

    click.echo(f"Starting TalentMe MCP Server connected to Cloud API: {api_url}", err=True)
    mcp_server = create_server(api_url, license_key, skills_path, init_memory)
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
    api_url = click.prompt("Cloud API URL", default="http://localhost:8000")
    license_key = click.prompt("Your License Key", default="test-key")
    
    # 3. Create Memory Directory and Wiki Structure
    init_memory_structure(memory_path)
    
    # 4. Configure IDEs
    talentme_path = sys.executable.replace("python", "talentme") # Heuristic for venv bin
    if not os.path.exists(talentme_path):
        talentme_path = "talentme" # Fallback to naked command
        
    mcp_config = {
        "talentme": {
            "command": talentme_path,
            "args": [
                "start",
                "--init-memory", memory_path,
                "--api-url", api_url,
                "--license-key", license_key
            ]
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

    # 5. Provide AI Prompt for Copy-Paste
    click.echo("\n" + "="*40)
    click.echo("🤖 AI PROMPT (Copy-Paste this to your AI Assistant):")
    click.echo("="*40)
    prompt = f"""
Please help me update my MCP configuration to include the TalentMe server. 
I am using {system}. My config should look like this:

{json.dumps(mcp_config, indent=2)}

Please find my MCP configuration file (e.g., in Claude Desktop or Cursor) and add the 'talentme' server to the 'mcpServers' section.
"""
    click.echo(prompt)
    click.echo("="*40)

    click.echo("\n=== Setup Complete! ===")
    if configured_any:
        click.echo("Please RESTART your IDE for the changes to take effect.")
    click.echo("You can now use TalentMe to dominate your ML interviews.")
