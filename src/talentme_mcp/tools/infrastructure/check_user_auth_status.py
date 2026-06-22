import requests
from mcp.server.fastmcp import FastMCP

def setup_check_user_auth_status(mcp: FastMCP, api_url: str, license_key: str):
    @mcp.tool()
    def check_user_auth_status() -> str:
        """
        Check the user's current subscription tier and access level to TalentMe Cloud.
        """
        try:
            response = requests.get(
                f"{api_url.rstrip('/')}/api/auth/status",
                headers={"Authorization": f"Bearer {license_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                tier = data.get("tier", "unknown")
                status = data.get("status", "unknown")
                return f"User Auth Status:\nTier: {tier}\nSubscription Status: {status}"
            else:
                return "Error: Failed to fetch auth status."
        except Exception:
            return "Error: Network failure."
