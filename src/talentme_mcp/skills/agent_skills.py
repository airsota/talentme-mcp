import os
from mcp.server.fastmcp import FastMCP

def setup_agent_skills(mcp: FastMCP, skills_path: str, memory_path: str = None):
    
    local_skills_path = os.path.join(memory_path, ".skills") if memory_path else None

    @mcp.tool()
    def list_agent_skills() -> str:
        """
        List all available built-in and local Agent Skills.
        Built-in skills are system-provided, while local skills are in your memory vault.
        """
        all_skills = []
        
        # Check system skills
        if os.path.exists(skills_path):
            for item in os.listdir(skills_path):
                if os.path.isdir(os.path.join(skills_path, item)):
                    if os.path.exists(os.path.join(skills_path, item, "SKILL.md")):
                        all_skills.append(f"System Skill: {item}")
        
        # Check local skills
        if local_skills_path and os.path.exists(local_skills_path):
            for item in os.listdir(local_skills_path):
                if os.path.isdir(os.path.join(local_skills_path, item)):
                    if os.path.exists(os.path.join(local_skills_path, item, "SKILL.md")):
                        all_skills.append(f"Local Skill: {item}")
        
        return "\n".join(all_skills) if all_skills else "No skills found."

    @mcp.tool()
    def read_agent_skill_instruction(skill_name: str, is_local: bool = False) -> str:
        """
        Read the detailed instructions for a specific Agent Skill.
        Args:
            skill_name: The name of the skill (e.g., "llm-wiki")
            is_local: Set to True if this is a local skill from the memory vault.
        """
        base_path = local_skills_path if (is_local and local_skills_path) else skills_path
        
        if not os.path.exists(base_path):
            return f"Error: Skills path not found at {base_path}."
            
        skill_file = os.path.join(base_path, skill_name, "SKILL.md")
        if not os.path.exists(skill_file):
            return f"Error: Skill '{skill_name}' not found."
            
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Failed to read skill instruction: {str(e)}"
