import os
import requests
from mcp.server.fastmcp import FastMCP

def setup_agent_skills(mcp: FastMCP, skills_path: str, memory_path: str = None, api_url: str = None, license_key: str = None):
    
    local_skills_path = os.path.join(memory_path, ".skills") if memory_path else None

    @mcp.tool()
    def list_agent_skills() -> str:
        """
        List all available built-in, local, and cloud Agent Skills.
        """
        all_skills = []
        
        # 1. Check system skills
        if os.path.exists(skills_path):
            for item in os.listdir(skills_path):
                if os.path.isdir(os.path.join(skills_path, item)) and os.path.exists(os.path.join(skills_path, item, "SKILL.md")):
                    all_skills.append(f"System Skill: {item}")
        
        # 2. Check local memory skills
        if local_skills_path and os.path.exists(local_skills_path):
            for item in os.listdir(local_skills_path):
                if os.path.isdir(os.path.join(local_skills_path, item)) and os.path.exists(os.path.join(local_skills_path, item, "SKILL.md")):
                    all_skills.append(f"Local Skill: {item}")
                    
        # 3. Check cloud skills
        if api_url and license_key:
            try:
                headers = {"Authorization": f"Bearer {license_key}"}
                resp = requests.get(f"{api_url}/api/skills/list", headers=headers, timeout=5)
                if resp.status_code == 200:
                    cloud_skills = resp.json().get("skills", [])
                    for s in cloud_skills:
                        all_skills.append(f"Cloud Skill: {s}")
            except Exception as e:
                all_skills.append(f"Note: Could not fetch cloud skills ({e})")
        
        return "\n".join(all_skills) if all_skills else "No skills found."

    @mcp.tool()
    def read_agent_skill_instruction(skill_name: str, type: str = "system") -> str:
        """
        Read the detailed instructions for a specific Agent Skill.
        Args:
            skill_name: The name of the skill.
            type: One of 'system', 'local', or 'cloud'.
        """
        if type == "cloud":
            if not api_url or not license_key:
                return "Error: Cloud API not configured."
            try:
                headers = {"Authorization": f"Bearer {license_key}"}
                resp = requests.get(f"{api_url}/api/skills/get/{skill_name}", headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.json().get("content", "Empty skill.")
                return f"Error: Cloud skill not found (Status {resp.status_code})"
            except Exception as e:
                return f"Failed to fetch cloud skill: {str(e)}"
        
        base_path = local_skills_path if (type == "local" and local_skills_path) else skills_path
        if not os.path.exists(base_path):
            return f"Error: Skills path not found at {base_path}."
            
        skill_file = os.path.join(base_path, skill_name, "SKILL.md")
        if not os.path.exists(skill_file):
            return f"Error: {type.capitalize()} skill '{skill_name}' not found."
            
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Failed to read skill instruction: {str(e)}"
