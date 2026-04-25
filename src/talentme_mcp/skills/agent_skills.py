import os
from mcp.server.fastmcp import FastMCP

def setup_agent_skills(mcp: FastMCP, skills_path: str):
    
    @mcp.tool()
    def list_agent_skills() -> str:
        """
        List all available built-in Agent Skills.
        These skills are system-provided prompts/instructions for learning and interviewing.
        """
        if not os.path.exists(skills_path):
            return "Error: System Skills path not found."
            
        skills = []
        for item in os.listdir(skills_path):
            item_path = os.path.join(skills_path, item)
            if os.path.isdir(item_path):
                # Check if it has a SKILL.md
                if os.path.exists(os.path.join(item_path, "SKILL.md")):
                    skills.append(f"Skill: {item}")
        
        return "\\n".join(skills) if skills else "No built-in skills found."

    @mcp.tool()
    def read_agent_skill_instruction(skill_name: str) -> str:
        """
        Read the detailed instructions for a specific Agent Skill.
        Call this tool when you need to execute a specific skill to understand how to do it.
        """
        if not os.path.exists(skills_path):
            return "Error: System Skills path not found."
            
        skill_file = os.path.join(skills_path, skill_name, "SKILL.md")
        if not os.path.exists(skill_file):
            return f"Error: Skill '{skill_name}' not found."
            
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Failed to read skill instruction: {str(e)}"
