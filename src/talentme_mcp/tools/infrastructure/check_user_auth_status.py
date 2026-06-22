import requests
from mcp.server.fastmcp import FastMCP

def setup_check_user_auth_status(mcp: FastMCP, api_url: str, license_key: str, email: str = None):
    @mcp.tool()
    def check_user_auth_status() -> str:
        """
        Check the user's current subscription tier and access level to TalentMe Cloud.
        """
        try:
            headers = {"Authorization": f"Bearer {license_key}"}
            if email:
                headers["X-User-Email"] = email
            response = requests.get(
                f"{api_url.rstrip('/')}/api/auth/status",
                headers=headers,
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
