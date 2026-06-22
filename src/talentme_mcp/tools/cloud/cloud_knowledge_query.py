import requests
from mcp.server.fastmcp import FastMCP

def setup_cloud_knowledge_query(mcp: FastMCP, api_url: str, license_key: str):
    @mcp.tool()
    def cloud_knowledge_query(intent: str, lex_query: str, vec_query: str, top_k: int = 5) -> str:
        """
        Execute a Hybrid Search (Lexical + Vector QMD) against the TalentMe Cloud Knowledge Base.
        
        Args:
            intent: The high-level intent of the user's question.
            lex_query: Keyword-based query (e.g., exact names, errors). Prefer English keywords.
            vec_query: Semantic description of what you are looking for.
            top_k: Number of chunks to retrieve.
        """
        try:
            response = requests.post(
                f"{api_url.rstrip('/')}/api/kb/hybrid_search",
                json={
                    "intent": intent,
                    "lex_query": lex_query,
                    "vec_query": vec_query,
                    "top_k": top_k
                },
                headers={"Authorization": f"Bearer {license_key}"},
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("results"):
                    return f"No results found for '{lex_query}' or '{vec_query}'."
                return "\n\n".join(data["results"])
            elif response.status_code == 403:
                return "Error: You do not have access to this Snapshot version."
            else:
                return "Error: Cloud Hybrid Search Engine is temporarily unavailable."
        except Exception:
            return "Error: Failed to connect to the cloud knowledge base."
