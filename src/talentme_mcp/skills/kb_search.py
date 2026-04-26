import requests
from mcp.server.fastmcp import FastMCP

def setup_kb_skills(mcp: FastMCP, api_url: str, license_key: str):
    
    @mcp.tool()
    def search_knowledge_base(query: str, max_results: int = 5) -> str:
        """
        Search the TalentMe Cloud Knowledge Base for ML/DS interview concepts.
        
        GUIDANCE: Prefer English keywords (e.g., 'Decision Tree' instead of '什么是决策树') for higher accuracy.
        SECURITY RULE: This tool only provides distilled knowledge.
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
                    return f"No results found for '{query}' in the cloud knowledge base. Try searching with English keywords."
                return "\n".join(data["results"])
            elif response.status_code == 401:
                return "Error: Secure access unauthorized. Please verify your license key."
            else:
                return "Error: The cloud knowledge base is temporarily unreachable."
        except Exception:
            return "Error: Failed to connect to the cloud knowledge base due to a secure network restriction."

    @mcp.tool()
    def list_kb_topics() -> str:
        """
        List available high-level topics in the cloud knowledge base.
        """
        try:
            response = requests.get(
                f"{api_url.rstrip('/')}/api/kb/topics",
                headers={"Authorization": f"Bearer {license_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return "\n".join(data.get("topics", []))
            elif response.status_code == 401:
                return "Error: Secure access unauthorized."
            else:
                return "Error: Cloud topics are temporarily unavailable."
        except Exception:
            return "Error: Failed to fetch cloud metadata."
