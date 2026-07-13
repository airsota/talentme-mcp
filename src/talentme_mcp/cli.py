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
LOCAL_CONFIG_FILE = Path(".") / ".talentme_config.json"

def save_config(memory_path, api_url, license_key, email=None, local=False):
    config = {}
    target_file = LOCAL_CONFIG_FILE if local else CONFIG_FILE
    if target_file.exists():
        with open(target_file, 'r') as f:
            try:
                config = json.load(f)
            except Exception:
                pass
                
    config.update({
        "memory_path": memory_path,
        "api_url": api_url,
        "license_key": license_key,
        "email": email
    })
    
    with open(target_file, 'w') as f:
        json.dump(config, f, indent=2)
    # SECURITY: Restrict file permissions to current user only (600)
    try:
        os.chmod(target_file, 0o600)
    except Exception:
        pass

def update_settings(key: str, value: str, local=False):
    config = {}
    target_file = LOCAL_CONFIG_FILE if local else CONFIG_FILE
    if target_file.exists():
        with open(target_file, 'r') as f:
            try:
                config = json.load(f)
            except Exception:
                pass
                
    if "settings" not in config:
        config["settings"] = {}
        
    config["settings"][key] = value
    
    with open(target_file, 'w') as f:
        json.dump(config, f, indent=2)
    try:
        os.chmod(target_file, 0o600)
    except Exception:
        pass

def load_config():
    # Priority: Environment variables -> Local Config file -> Global Config file
    config = {}
    
    # 1. Load from global config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception:
            pass
            
    # 2. Override with local config file if exists in current working directory
    local_path = Path(".") / ".talentme_config.json"
    if local_path.exists():
        try:
            with open(local_path, 'r') as f:
                local_cfg = json.load(f)
                config.update(local_cfg)
        except Exception:
            pass
    
    # Override with env vars if present for production safety
    if os.environ.get("TALENTME_LICENSE_KEY"):
        config["license_key"] = os.environ.get("TALENTME_LICENSE_KEY")
    if os.environ.get("TALENTME_API_URL"):
        config["api_url"] = os.environ.get("TALENTME_API_URL")
    if os.environ.get("TALENTME_MEMORY_PATH"):
        config["memory_path"] = os.environ.get("TALENTME_MEMORY_PATH")
    if os.environ.get("TALENTME_EMAIL"):
        config["email"] = os.environ.get("TALENTME_EMAIL")
        
    return config

def copy_template_tree(src: str, dst: str):
    """Recursively copy template files to dst without overwriting user-modified markdown files."""
    for root, dirs, files in os.walk(src):
        rel_dir = os.path.relpath(root, src)
        target_dir = dst if rel_dir == "." else os.path.join(dst, rel_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            # Determine if this file is a system configuration file or skill instruction
            # System files (.skills/*, _meta/*, template.json) are safe to overwrite.
            # Markdown pages and user readmes at the root are protected from overwriting.
            is_system_file = (
                file == "template.json" or 
                ".skills" in rel_dir.split(os.sep) or 
                "_meta" in rel_dir.split(os.sep)
            )
            
            if is_system_file or not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)

def init_memory_structure(memory_path: str, template_name: str = None, license_key: str = None, email: str = None, force: bool = False):
    """Initialize the LLM Wiki structure using local template and upgrade DB schema."""
    # Check if the memory path is already bootstrapped (DB + core concepts directory exist)
    is_bootstrap_done = os.path.exists(os.path.join(memory_path, 'memory.db')) and os.path.exists(os.path.join(memory_path, 'concepts'))
    
    # Skip download/copying if bootstrap is already completed and force is False
    skip_download = is_bootstrap_done and not force and not template_name
    
    if skip_download:
        click.echo(f"Memory structure at {memory_path} already initialized, skipping template sync.", err=True)
    else:
        click.echo(f"Initializing/Syncing Memory at {memory_path}...", err=True)
        
        # 1. Clone local memory template (if exists)
        # SECURITY: Never hardcode absolute server paths in a public MCP package.
        # Use environment variable for local testing, fallback to basic dirs for public clients.
        cloud_env_path = os.environ.get("TALENTME_CLOUD_PATH")
        
        config = load_config()
        final_license = license_key or getattr(sys, '_talentme_license_key', None) or config.get("license_key")
        final_email = email or getattr(sys, '_talentme_email', None) or config.get("email")
        
        if cloud_env_path:
            base_template_dir = os.path.join(cloud_env_path, "templates", "local_memory")
            template_dir = None
            if os.path.exists(base_template_dir):
                try:
                    # 1. Try to read active_version from manifest.json at the template root
                    manifest_path = os.path.join(base_template_dir, "manifest.json")
                    active_version = None
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                manifest = json.load(f)
                                active_version = manifest.get("active_version")
                        except Exception:
                            pass
                    
                    # 2. If manifest specifies a valid version subdirectory, use it
                    if active_version and os.path.isdir(os.path.join(base_template_dir, active_version)):
                        template_dir = os.path.join(base_template_dir, active_version)
                    else:
                        # 3. Fallback: Dynamic SemVer Sorting
                        subdirs = [d for d in os.listdir(base_template_dir) if os.path.isdir(os.path.join(base_template_dir, d)) and d.startswith("v") and not d.startswith(".")]
                        if subdirs:
                            def parse_version(v_str):
                                parts = v_str.strip("v").split(".")
                                return [int(p) for p in parts if p.isdigit()]
                            subdirs.sort(key=parse_version, reverse=True)
                            template_dir = os.path.join(base_template_dir, subdirs[0])
                except Exception:
                    pass
                    
            if not template_dir or not os.path.exists(template_dir):
                template_dir = os.path.join(cloud_env_path, "templates", "local_memory", "v1.0.0")

            if os.path.exists(template_dir):
                copy_template_tree(template_dir, memory_path)
            else:
                dirs = ["concepts", "entities", "skills", "references", "synthesis", "journal", "projects", "_raw", "_meta", ".skills"]
                for d in dirs:
                    os.makedirs(os.path.join(memory_path, d), exist_ok=True)
        else:
            # Fetch local_memory structure from Cloud API if possible
            api_url = getattr(sys, '_talentme_api_url', None) or config.get("api_url")
            
            fetched = False
            if api_url and final_license:
                try:
                    import requests
                    headers = {"Authorization": f"Bearer {final_license}"}
                    if final_email:
                        headers["X-User-Email"] = final_email
                    resp = requests.get(f"{api_url}/api/templates/get/local_memory", headers=headers, timeout=10)
                    if resp.status_code == 200:
                        files = resp.json().get("files", {})
                        if files:
                            for rel_path, content in files.items():
                                # Strip any version prefix dynamically if returned (e.g. v1.0.0/ or v1.0.1/)
                                import re
                                rel_path = re.sub(r"^v\d+\.\d+\.\d+[/\\]", "", rel_path)
                                # SECURITY: Sanitize path to prevent traversal attacks
                                clean_path = os.path.normpath(rel_path).lstrip(os.sep)
                                if '..' in clean_path.split(os.sep):
                                    continue  # Skip malicious paths
                                full_dest = os.path.join(memory_path, clean_path)
                                if not os.path.realpath(full_dest).startswith(os.path.realpath(memory_path)):
                                    continue  # Skip paths that escape the vault
                                
                                # SECURITY & DATA INTEGRITY:
                                # Only overwrite system files (like template.json, .skills/*, _meta/*).
                                # Never overwrite user-modifiable markdown files or readmes.
                                is_system_file = (
                                    clean_path == "template.json" or 
                                    clean_path.startswith(".skills/") or 
                                    clean_path.startswith("_meta/")
                                )
                                
                                if is_system_file or not os.path.exists(full_dest):
                                    os.makedirs(os.path.dirname(full_dest), exist_ok=True)
                                    with open(full_dest, 'w', encoding='utf-8') as f:
                                        f.write(content)
                            fetched = True
                except Exception:
                    pass
                    
            if not fetched:
                dirs = ["concepts", "entities", "skills", "references", "synthesis", "journal", "projects", "_raw", "_meta", ".skills"]
                for d in dirs:
                    os.makedirs(os.path.join(memory_path, d), exist_ok=True)
            
    # 2. Initialize and Upgrade SQLite DB
    db_path = os.path.join(memory_path, 'memory.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table 1: Learning Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            topic TEXT,
            summary TEXT,
            mastery_level INTEGER,
            details TEXT
        )
    ''')
    
    # Table 2: User Config (for license tracking and system state)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # SECURITY: Do NOT store license_key in memory.db (CWE-312).
    # License key is only stored in ~/.talentme_config.json (mode 0o600).
    # Remove any previously stored license_key from older versions.
    cursor.execute("DELETE FROM user_config WHERE key = 'license_key'")
    if final_email:
        cursor.execute("INSERT OR REPLACE INTO user_config (key, value) VALUES ('email', ?)", (final_email,))
        
    conn.commit()
    conn.close()
            
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
            if final_email:
                headers["X-User-Email"] = final_email
            resp = requests.get(f"{api_url}/api/templates/get/{template_name}", headers=headers, timeout=10)
            if resp.status_code == 200:
                files = resp.json().get("files", {})
                if not files:
                    click.echo(f"Warning: Template '{template_name}' is empty or not found on server.", err=True)
                    return
                
                # If template already exists, we should probably warn or handle it in the caller
                # For simplicity here, we write files (overwrite individual files if they changed)
                for rel_path, content in files.items():
                    # SECURITY: Sanitize path to prevent traversal attacks
                    clean_path = os.path.normpath(rel_path).lstrip(os.sep)
                    if '..' in clean_path.split(os.sep):
                        continue
                    full_dest = os.path.join(dest_skill, clean_path)
                    if not os.path.realpath(full_dest).startswith(os.path.realpath(dest_skill)):
                        continue
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

def interactive_template_sync(memory_path: str, api_url: str, license_key: str, email: str = None):
    """Helper to list and sync templates interactively."""
    sys._talentme_api_url = api_url
    sys._talentme_license_key = license_key
    sys._talentme_email = email
    
    try:
        import requests
        click.echo(f"[*] Fetching available templates from {api_url}...", err=True)
        headers = {"Authorization": f"Bearer {license_key}"}
        if email:
            headers["X-User-Email"] = email
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
                init_memory_structure(memory_path, t, sys._talentme_license_key, email=sys._talentme_email)
        else:
            try:
                # Support comma separated numbers: "1,2"
                choices = [c.strip() for c in choice.split(",")]
                for c in choices:
                    idx = int(c) - 1
                    if 0 <= idx < len(templates):
                        init_memory_structure(memory_path, templates[idx], sys._talentme_license_key, email=sys._talentme_email)
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
        if (repo_dir / ".git").exists():
            click.echo(f"Pulling latest changes in {repo_dir}...")
            subprocess.run(["git", "pull"], cwd=repo_dir, check=True)
            
            click.echo("Re-installing dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], cwd=repo_dir, check=True)
        else:
            click.echo("Git repository not found. Assuming pip installation...")
            click.echo("Upgrading from official GitHub repository...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "git+https://github.com/airsota/talentme-mcp.git"], check=True)
            
        click.echo("\n✅ Software successfully updated!")
        click.echo("💡 PRO TIP: You can now use '/talentme' or '/tm' in your IDE to wake up the assistant.")
        
        # Now ask if they want to sync templates
        config = load_config()
        if config.get("memory_path") and click.confirm("\nWould you like to sync/update cloud templates as well?"):
            interactive_template_sync(config["memory_path"], config["api_url"], config["license_key"], config.get("email"))
            
        click.echo("\n[IMPORTANT] Please restart your MCP server/IDE to apply new instructions.")
    except Exception as e:
        click.echo(f"Update failed: {e}")

def link_native_skills(memory_path: str):
    """Symlink local skills to agent directories for native skill support."""
    click.echo("\n=== Installing Native Skills (Symlinking) ===", err=True)
    local_skills_path = os.path.join(memory_path, ".skills")
    
    agent_paths = [
        # Project local paths
        Path(".claude/skills"),
        Path(".cursor/skills"),
        Path(".windsurf/skills"),
        Path(".agents/skills"),
        Path(".pi/skills"),
        Path(".kiro/skills"),
        # Global paths
        Path.home() / ".claude/skills",
        Path.home() / ".gemini/skills",
        Path.home() / ".gemini/antigravity/skills",
        Path.home() / ".gemini/antigravity-ide/skills",
        Path.home() / ".codex/skills",
        Path.home() / ".hermes/skills",
        Path.home() / ".openclaw/skills",
        Path.home() / ".copilot/skills",
        Path.home() / ".trae/skills",
        Path.home() / ".trae-cn/skills",
        Path.home() / ".kiro/skills",
        Path.home() / ".pi/agent/skills",
        Path.home() / ".agents/skills"
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
                        os.symlink(os.path.abspath(src), dst)
                click.echo(f"✅ Linked skills to {agent_path}", err=True)
            except Exception as e:
                click.echo(f"⚠️  Could not link to {agent_path}: {e}", err=True)

@main.command()
@click.option('--memory', type=click.Path(), help='Path to your local memory directory.')
@click.option('--api-url', type=str, help='URL of the TalentMe Cloud API.')
@click.option('--license-key', type=str, help='Your TalentMe License Key.')
@click.option('--email', type=str, help='Your Account Email.')
@click.option('--force', is_flag=True, help='Force sync by clean re-initialization of core protocols.')
def sync(memory, api_url, license_key, email, force):
    """Sync core protocols and templates from cloud to local memory."""
    config = load_config()
    memory_path = memory or config.get("memory_path")
    if not memory_path:
        click.echo("Error: No memory path provided and none remembered. Please run 'setup' first.")
        return
    
    memory_path = os.path.abspath(os.path.expanduser(memory_path))
    api_url = api_url or config.get("api_url")
    license_key = license_key or config.get("license_key")
    email = email or config.get("email")
    
    # Store API info in sys for init_memory_structure to pick up
    sys._talentme_api_url = api_url
    sys._talentme_license_key = license_key
    sys._talentme_email = email
    
    if force:
        click.echo(f"=== Force Syncing templates for {memory_path} ===")
        dest_skill = os.path.join(memory_path, ".skills", "llm-wiki")
        if os.path.exists(dest_skill):
            shutil.rmtree(dest_skill)
        init_memory_structure(memory_path, license_key=license_key, email=email, force=True)
        click.echo("Done!")
    else:
        interactive_template_sync(memory_path, api_url, license_key, email)
        
    link_native_skills(memory_path)

@main.command()
@click.option('--init-memory', type=click.Path(), help='Initialize or connect to a local memory directory.')
@click.option('--api-url', type=str, help='URL of the TalentMe Cloud API.')
@click.option('--license-key', type=str, help='Your TalentMe License Key.')
@click.option('--email', type=str, help='Your Account Email.')
def start(init_memory, api_url, license_key, email):
    """Start the TalentMe MCP Server."""
    config = load_config()
    
    # Priority: Flag > Config > Default
    final_memory = init_memory or config.get("memory_path")
    final_api = api_url or config.get("api_url", "https://api-talentme.airsota.com")
    final_key = license_key or config.get("license_key")
    final_email = email or config.get("email")
    
    if not final_key:
        click.echo("Error: No license key configured. Please run 'talentme setup' first or set TALENTME_LICENSE_KEY.", err=True)
        return

    if not final_memory:
        click.echo("Error: No memory path provided. Please run 'setup' or use --init-memory.")
        return

    final_memory = os.path.abspath(os.path.expanduser(final_memory))

    # Store API info in sys for tools to pick up
    sys._talentme_api_url = final_api
    sys._talentme_license_key = final_key
    sys._talentme_email = final_email

    # 2. Handle Memory Initialization (Silent)
    init_memory_structure(final_memory, template_name=None, license_key=final_key, email=final_email)
    
    click.echo(f"[*] TalentMe MCP Server starting...", err=True)
    click.echo(f"[*] Memory: {final_memory}", err=True)
    
    mcp_server = create_server(final_api, final_key, final_memory, final_email)
    mcp_server.run()

@main.command()
@click.option('--local', is_flag=True, help='Save configuration locally in the current directory.')
def setup(local):
    """Interactive setup to configure TalentMe and register with IDEs."""
    click.echo("=== TalentMe Onboarding & Setup ===")
    
    # 0. Local vs Global config prompt
    is_local = local or click.confirm("Save configuration locally in the current project directory (instead of globally)?", default=False)

    # 1. Ask for Memory Path
    default_memory = str(Path(os.getcwd()) / "my_memory")
    memory_path = click.prompt("Where should your local learning memory be stored?", default=default_memory)
    memory_path = os.path.abspath(os.path.expanduser(memory_path))
    
    # 2. Ask for API details
    email = click.prompt("Your Account Email", default="test@talentme.com")
    license_key = click.prompt("Your License Key", default="test-key")
    api_url = "https://api-talentme.airsota.com"
    
    # 3. Ask for Memory Write Mode
    click.echo("\n--- Agent Behavior Configuration ---")
    click.echo("How would you like the AI to manage your local knowledge memory?")
    click.echo("  [auto]      - The AI proactively saves learnings in the background.")
    click.echo("  [semi-auto] - The AI will ask you for permission before saving. (Recommended)")
    click.echo("  [manual]    - The AI only reads memory and never writes unless you explicitly tell it to.")
    memory_write_mode = click.prompt("Select a mode", type=click.Choice(['auto', 'semi-auto', 'manual']), default="semi-auto")
    
    # Save config
    save_config(memory_path, api_url, license_key, email, local=is_local)
    update_settings("memory_write_mode", memory_write_mode, local=is_local)

    # 3. Create Memory Directory structure
    init_memory_structure(memory_path, template_name=None, license_key=license_key, email=email, force=True)
    
    # 4. Interactive Template Choice
    interactive_template_sync(memory_path, api_url, license_key, email)
    
    # 4. Configure IDEs
    venv_bin_dir = Path(sys.executable).parent
    talentme_exe = "talentme.exe" if platform.system() == "Windows" else "talentme"
    talentme_path = str(venv_bin_dir / talentme_exe)
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
        "Cursor": None,
        "Windsurf": None,
        "Trae": None,
        "Antigravity": None
    }
    
    if system == "Darwin": # Mac
        ide_paths["Claude Desktop"] = home / "Library/Application Support/Claude/claude_desktop_config.json"
        ide_paths["Cursor"] = home / "Library/Application Support/Cursor/User/globalStorage/mcpServers.json"
        ide_paths["Windsurf"] = home / ".codeium/windsurf/mcp_config.json"
        ide_paths["Trae"] = home / ".trae/mcp.json"
        ide_paths["Antigravity"] = home / ".gemini/config/mcp_config.json"
    elif system == "Windows":
        appdata = Path(os.environ.get("APPDATA", ""))
        userprofile = Path(os.environ.get("USERPROFILE", ""))
        ide_paths["Claude Desktop"] = appdata / "Claude/claude_desktop_config.json"
        ide_paths["Cursor"] = appdata / "Cursor/User/globalStorage/mcpServers.json"
        ide_paths["Windsurf"] = userprofile / ".codeium/windsurf/mcp_config.json"
        ide_paths["Trae"] = userprofile / ".trae/mcp.json"
        ide_paths["Antigravity"] = userprofile / ".gemini/config/mcp_config.json"
    elif system == "Linux":
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
        ide_paths["Claude Desktop"] = config_home / "Claude/claude_desktop_config.json"
        ide_paths["Cursor"] = config_home / "Cursor/User/globalStorage/mcpServers.json"
        ide_paths["Windsurf"] = home / ".codeium/windsurf/mcp_config.json"
        ide_paths["Trae"] = home / ".trae/mcp.json"
        ide_paths["Antigravity"] = home / ".gemini/config/mcp_config.json"

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

    # 5. Generate IDE Bootstrap Files
    click.echo("\n=== Generating AI Bootstrap Files ===")
    
    # Common rules instructions
    rules_text = f"""When interacting with the user, you act as the TalentMe Partner Agent. This workspace is integrated with the TalentMe Local and Cloud Knowledge Bases.
You have access to a set of dynamic skills. Depending on the scenario, you MUST first load and execute the appropriate skill before proceeding:

## ⚡ Dynamic Skill Dispatcher (CRITICAL)
Before responding or calling other tools, check if the current scenario matches any trigger below. If it does, you MUST call `read_agent_skill_instruction(skill_name: ...)` to fetch and follow its instructions:

1. **Daily Summary / Onboarding / "What should I do today?"**
   - Trigger: User asks for a daily summary, progress, status, or what tasks to do.
   - Skill: Call `read_agent_skill_instruction` with `skill_name: "tm-guide"`.

2. **Learning / Compiling Cloud Knowledge**
   - Trigger: User says "I want to learn X", "sync X from cloud", or "create notes for X".
   - Skill: Call `read_agent_skill_instruction` with `skill_name: "bridge-sync-and-digest"`.

3. **Handling Duplicate Concept Files**
   - Trigger: You are about to call `create_wiki_page` or write a new note, but a file for this topic already exists (always check first using `list_local_wiki_pages`).
   - Skill: Call `read_agent_skill_instruction` with `skill_name: "tm-merge"`.

4. **Information Conflicts / Logical Contradictions**
   - Trigger: During writing, editing, or merging, you notice new information conflicts with existing local records.
   - Skill: Call `read_agent_skill_instruction` with `skill_name: "tm-contradiction"`.

5. **Organizing Links / Weaving the Knowledge Graph**
   - Trigger: After writing a new file, importing content, or when explicitly asked to link/cross-reference.
   - Skill: Call `read_agent_skill_instruction` with `skill_name: "tm-cross-linker"`.

## 🛠️ General Guidelines
- Always prioritize local knowledge from this private memory workspace at {memory_path}.
- Avoid absolute paths in responses; use [[Wikilinks]] for page references.
- Private Memory Path: {memory_path}
"""
    
    # 5a. Project-local rule files
    # .cursorrules
    with open(".cursorrules", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe Cursor Rules\n{rules_text}")
    click.echo("    ✅ Generated .cursorrules")

    # CLAUDE.md
    with open("CLAUDE.md", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe CLAUDE Instructions\n{rules_text}")
    click.echo("    ✅ Generated CLAUDE.md")

    # GEMINI.md
    with open("GEMINI.md", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe GEMINI Instructions\n{rules_text}")
    click.echo("    ✅ Generated GEMINI.md")

    # AGENTS.md
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
    click.echo("    ✅ Generated AGENTS.md")

    # .hermes.md (symlink to AGENTS.md)
    try:
        if os.path.exists(".hermes.md") or os.path.islink(".hermes.md"):
            os.unlink(".hermes.md")
        os.symlink("AGENTS.md", ".hermes.md")
        click.echo("    ✅ Generated .hermes.md symlink")
    except Exception:
        pass

    # Ensure directories for specific rule files exist
    os.makedirs(".cursor/rules", exist_ok=True)
    os.makedirs(".windsurf/rules", exist_ok=True)
    os.makedirs(".agent/rules", exist_ok=True)
    os.makedirs(".agent/workflows", exist_ok=True)
    os.makedirs(".github", exist_ok=True)

    # .cursor/rules/talentme.mdc
    cursor_mdc_content = f"""---
description: Custom instructions for interacting with TalentMe Private Memory
globs: *
alwaysApply: true
---
# TalentMe Cursor Rules
{rules_text}"""
    with open(".cursor/rules/talentme.mdc", "w", encoding='utf-8') as f:
        f.write(cursor_mdc_content)
    click.echo("    ✅ Generated .cursor/rules/talentme.mdc")

    # .windsurf/rules/talentme.md
    with open(".windsurf/rules/talentme.md", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe Windsurf Rules\n{rules_text}")
    click.echo("    ✅ Generated .windsurf/rules/talentme.md")

    # .agent/rules/talentme.md
    with open(".agent/rules/talentme.md", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe Antigravity Rules\n{rules_text}")
    click.echo("    ✅ Generated .agent/rules/talentme.md")

    # .agent/workflows/talentme.md
    with open(".agent/workflows/talentme.md", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe Slash Commands\n- `/talentme <query>`: Search your private memory.\n- `/tm <query>`: Shorthand for /talentme.\n")
    click.echo("    ✅ Generated .agent/workflows/talentme.md")

    # .github/copilot-instructions.md
    with open(".github/copilot-instructions.md", "w", encoding='utf-8') as f:
        f.write(f"# TalentMe Copilot Instructions\n{rules_text}")
    click.echo("    ✅ Generated .github/copilot-instructions.md")

    # 6. Provide Manual Installation Guide
    click.echo("\n" + "="*50)
    click.echo("⚙️  MANUAL MCP CONFIGURATION GUIDE")
    click.echo("="*50)
    if not configured_any:
        click.echo("It looks like automatic IDE configuration was skipped or failed.")
    
    click.echo("If you need to manually install the TalentMe MCP server, add this JSON snippet:")
    click.echo(json.dumps(mcp_config, indent=2))
    
    click.echo("\n📌 Common MCP Configuration Paths:")
    if system == "Darwin":
        click.echo("  - Claude Desktop : ~/Library/Application Support/Claude/claude_desktop_config.json")
        click.echo("  - Cursor         : ~/Library/Application Support/Cursor/User/globalStorage/mcpServers.json")
        click.echo("  - Windsurf       : ~/.codeium/windsurf/mcp_config.json")
        click.echo("  - Trae           : ~/.trae/mcp.json")
        click.echo("  - Antigravity    : ~/.gemini/config/mcp_config.json")
        click.echo("  - Roo Code/Cline : ~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json")
    elif system == "Windows":
        click.echo("  - Claude Desktop : %APPDATA%\\Claude\\claude_desktop_config.json")
        click.echo("  - Cursor         : %APPDATA%\\Cursor\\User\\globalStorage\\mcpServers.json")
        click.echo("  - Windsurf       : %USERPROFILE%\\.codeium\\windsurf\\mcp_config.json")
        click.echo("  - Trae           : %USERPROFILE%\\.trae\\mcp.json")
        click.echo("  - Antigravity    : %USERPROFILE%\\.gemini\\config\\mcp_config.json")
        click.echo("  - Roo Code/Cline : %APPDATA%\\Code\\User\\globalStorage\\saoudrizwan.claude-dev\\settings\\cline_mcp_settings.json")
    elif system == "Linux":
        click.echo("  - Claude Desktop : ~/.config/Claude/claude_desktop_config.json")
        click.echo("  - Cursor         : ~/.config/Cursor/User/globalStorage/mcpServers.json")
        click.echo("  - Windsurf       : ~/.codeium/windsurf/mcp_config.json")
        click.echo("  - Trae           : ~/.trae/mcp.json")
        click.echo("  - Antigravity    : ~/.gemini/config/mcp_config.json")
        click.echo("  - Roo Code/Cline : ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json")
        
    click.echo("\n🤖 AI PROMPT (Copy-Paste this to your AI Assistant):")
    click.echo(f"Please help me update my MCP configuration to include the TalentMe server at the correct path for my IDE. My config should be:\n{json.dumps(mcp_config, indent=2)}")
    click.echo("="*50)

    # 7. Symlink skills to agent directories (Native Skill support)
    link_native_skills(memory_path)

    click.echo("\n=== Setup Complete! ===")
    if configured_any:
        click.echo("Please RESTART your IDE for the changes to take effect.")
    click.echo("You can now use '/talentme' or '/tm' in your IDE to dominate your ML interviews.")



@main.group()
def config():
    """Manage TalentMe configurations and agent settings."""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration setting (e.g. memory_write_mode auto)."""
    valid_settings = {
        "memory_write_mode": ["auto", "semi-auto", "manual"]
    }
    
    if key in valid_settings and value not in valid_settings[key]:
        click.echo(f"Error: Invalid value for {key}. Allowed values: {', '.join(valid_settings[key])}")
        return
        
    update_settings(key, value)
    click.echo(f"✅ Successfully set {key} = {value}")
    
if __name__ == '__main__':
    main()
