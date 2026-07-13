import requests
from mcp.server.fastmcp import FastMCP

def setup_read_agent_skill_instruction(mcp: FastMCP, api_url: str, license_key: str, email: str = None):
    @mcp.tool()
    def read_agent_skill_instruction(skill_name: str, type: str = "system") -> str:
        """
        Dynamically fetch the instruction prompt for a specific skill from the cloud.
        IMPORTANT: This is an implicit invocation tool. The fetched instructions MUST be
        injected into your context and strictly followed for subsequent tasks.
        
        Args:
            skill_name: The name of the skill to fetch (e.g., 'talentme-mock-interviewer').
            type: Currently defaults to 'system'.
        """
        try:
            headers = {"Authorization": f"Bearer {license_key}"}
            if email:
                headers["X-User-Email"] = email
            params = {}
            if type and type != "system":
                params["role"] = type
                
            response = requests.get(
                f"{api_url.rstrip('/')}/api/skills/get/{skill_name}",
                params=params,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                if content:
                    return f"<details>\n<summary>🤖 Injected system instructions for skill '{skill_name}'</summary>\n\n{content}\n</details>"
                return f"Error: Skill '{skill_name}' returned empty content."
            elif response.status_code == 403:
                return "Error: You do not have the required subscription tier to access this premium skill."
            elif response.status_code == 404:
                return f"Error: Skill '{skill_name}' not found."
            else:
                return "Error: Failed to fetch skill instruction."
        except Exception:
            return "Error: Network failure while fetching skill."
