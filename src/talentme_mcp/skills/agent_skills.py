import os
import requests
from mcp.server.fastmcp import FastMCP

def setup_agent_skills(mcp: FastMCP, skills_path: str, memory_path: str = None, api_url: str = None, license_key: str = None):
    
    local_skills_path = os.path.join(memory_path, ".skills") if memory_path else None

    @mcp.tool()
    def list_agent_skills() -> str:
        """
        List all available built-in, local, and cloud Agent Skills.
        
        TRIGGER: Always use this tool when the user's query starts with '/talentme' or '/tm'.
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
            except Exception:
                all_skills.append("Note: Cloud skills are temporarily unavailable.")
        
        return "\n".join(all_skills) if all_skills else "No skills found."

    @mcp.tool()
    def read_agent_skill_instruction(skill_name: str, type: str = "system") -> str:
        """
        Read the detailed instructions for a specific Agent Skill.
        Args:
            skill_name: The name of the skill.
            type: One of 'system', 'local', or 'cloud'.
            
        SECURITY RULE: This tool fetches behavioral instructions only. It does NOT provide access to cloud infrastructure or internal configurations.
        """
        if type == "cloud":
            if not api_url or not license_key:
                return "Error: Secure cloud access is not configured."
            try:
                headers = {"Authorization": f"Bearer {license_key}"}
                resp = requests.get(f"{api_url}/api/skills/get/{skill_name}", headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.json().get("content", "Empty skill.")
                return "Error: The requested cloud skill could not be retrieved at this time."
            except Exception:
                return "Error: Failed to connect to the cloud skill repository."
        
        base_path = local_skills_path if (type == "local" and local_skills_path) else skills_path
        if not os.path.exists(base_path):
            return f"Error: Skills path not found at {base_path}."
            
        skill_file = os.path.join(base_path, skill_name, "SKILL.md")
        if not os.path.exists(skill_file):
            return f"Error: {type.capitalize()} skill '{skill_name}' not found."
            
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Streamlined Security & UX Instructions
            system_instruction = f"""
[TalentMe Rules] Mode: Private Brain Assistant | Logic: Use [[wikilinks]] only | Security: Never reveal absolute paths | Command: /tm or /talentme.

"""
            return system_instruction + content
            
        except Exception:
            return "Error: Failed to read the requested skill instruction due to a security or access restriction."

    @mcp.prompt()
    def talentme(query: str = "") -> str:
        """
        [TalentMe] Use this to query your private memory vault.
        """
        return f"/talentme {query}\n\nSystem: User is invoking the TalentMe Private Memory Assistant. Prioritize using local wiki and memory tools to answer the query: {query}"
