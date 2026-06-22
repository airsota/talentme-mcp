import requests
from mcp.server.fastmcp import FastMCP

def setup_read_cloud_document(mcp: FastMCP, api_url: str, license_key: str, email: str = None):
    @mcp.tool()
    def read_cloud_document(file_path: str) -> str:
        """
        Read the full content of a specific knowledge document from the TalentMe cloud.
        Call this if the hybrid search results indicate a document that you need to read in full.
        
        Args:
            file_path: The specific document path returned by the search engine.
        """
        try:
            headers = {"Authorization": f"Bearer {license_key}"}
            if email:
                headers["X-User-Email"] = email
            response = requests.post(
                f"{api_url.rstrip('/')}/api/kb/document",
                json={"file_path": file_path},
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("content", "Empty document.")
            elif response.status_code == 403:
                return "Error: Unauthorized access to this document."
            return f"Error: Could not find cloud document [[{file_path}]]."
        except Exception:
            return "Error: Secure cloud connection failed."
