import requests
from mcp.server.fastmcp import FastMCP

def setup_kb_skills(mcp: FastMCP, api_url: str, license_key: str):
    
    @mcp.tool()
    def search_knowledge_base(query: str, max_results: int = 5) -> str:
        """
        Search the ML interview system knowledge base for a specific concept or topic.
        Provide a specific query.
        """
        try:
            response = requests.post(
                f"{api_url.rstrip('/')}/api/kb/search",
                json={"query": query, "max_results": max_results},
                headers={"Authorization": f"Bearer {license_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("results"):
                    return f"No results found for '{query}' in the cloud knowledge base."
                return "\\n".join(data["results"])
            elif response.status_code == 401:
                return "Error: Invalid or expired License Key."
            else:
                return f"Error from Cloud API: {response.text}"
        except Exception as e:
            return f"Failed to connect to Cloud API: {str(e)}"

    @mcp.tool()
    def list_kb_topics() -> str:
        """
        List the main topics/directories available in the ML interview knowledge base.
        """
        try:
            response = requests.get(
                f"{api_url.rstrip('/')}/api/kb/topics",
                headers={"Authorization": f"Bearer {license_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return "\\n".join(data.get("topics", []))
            elif response.status_code == 401:
                return "Error: Invalid or expired License Key."
            else:
                return f"Error from Cloud API: {response.text}"
        except Exception as e:
            return f"Failed to connect to Cloud API: {str(e)}"
