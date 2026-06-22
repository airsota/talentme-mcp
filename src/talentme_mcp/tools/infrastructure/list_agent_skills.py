import requests
from mcp.server.fastmcp import FastMCP

def setup_list_agent_skills(mcp: FastMCP, api_url: str, license_key: str):
    @mcp.tool()
    def list_agent_skills() -> str:
        """
        List all available cloud agent skills that the user has access to.
        These skills are dynamic sets of instructions tailored for specific tasks.
        """
        try:
            response = requests.get(
                f"{api_url.rstrip('/')}/api/skills/list",
                headers={"Authorization": f"Bearer {license_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("skills"):
                    return "No cloud skills are currently available for your account tier."
                return "\n".join(data["skills"])
            elif response.status_code == 401:
                return "Error: Secure access unauthorized. Please verify your license key or subscription status."
            else:
                return "Error: Cloud skills server is temporarily unreachable."
        except Exception:
            return "Error: Failed to connect to the cloud skills service."
