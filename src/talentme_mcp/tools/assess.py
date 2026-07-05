import requests
import json
from mcp.server.fastmcp import FastMCP

def _strip_qmd_metadata(chunk: str) -> str:
    """Strip QMD headers that look like filenames."""
    lines = chunk.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') and stripped.lower().endswith('.md'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip()

def setup_assess_tool(mcp: FastMCP, api_url: str, license_key: str, email: str = None):
    @mcp.tool()
    def assess(domain: str, level: str) -> str:
        """
        Fetch an assessment rubric from the cloud for a specific domain and level,
        and prompt the Agent to conduct an interactive evaluation.
        
        Args:
            domain: The domain to assess (e.g., "Machine Learning", "System Design")
            level: The target level (e.g., "Junior", "Senior", "L5")
        """
        cloud_content = ""
        try:
            # 1. Fetch pure assessment rubric from cloud
            headers = {"Authorization": f"Bearer {license_key}"}
            if email:
                headers["X-User-Email"] = email
            
            # Use hybrid_search to fetch the relevant assessment rubric
            query = f"Assessment Rubric Syllabus Interview Questions for {domain} {level}"
            response = requests.post(
                f"{api_url.rstrip('/')}/api/kb/hybrid_search",
                json={
                    "intent": "knowledge_retrieval",
                    "lex_query": query,
                    "vec_query": query,
                    "top_k": 1
                },
                headers=headers,
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                chunks = data.get("results", [])
                if chunks:
                    cloud_content = _strip_qmd_metadata(chunks[0])
                else:
                    cloud_content = f"Fallback Standard Rubric: Please evaluate the user on 1. Fundamentals of {domain}, 2. Real-world application, 3. Trade-offs typical for {level} level."
            else:
                cloud_content = f"Error: Cloud API returned {response.status_code}."
        except Exception as e:
            cloud_content = f"Error: Failed to fetch from cloud. {str(e)}"
            
        # 2. Prompt Injection (The Script)
        injection = f"""
--- CLOUD ASSESSMENT RUBRIC ({domain} - {level}) ---
{cloud_content}
----------------------------------------------------
"""
        return injection
