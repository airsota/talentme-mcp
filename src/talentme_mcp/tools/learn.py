import os
import sqlite3
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

def setup_learn_tool(mcp: FastMCP, api_url: str, license_key: str, memory_path: str = None, email: str = None):
    @mcp.tool()
    def learn(cloud_doc_id: str, user_intent: str) -> str:
        """
        Start a personalized learning session for a cloud document (The Handshake Protocol).
        
        Args:
            cloud_doc_id: The identifier of the cloud document to fetch.
            user_intent: The specific angle, role, or style the user wants to learn this from (e.g., "MLE interview prep", "Socratic style").
        """
        cloud_content = ""
        try:
            # 1. Fetch pure knowledge from cloud
            headers = {"Authorization": f"Bearer {license_key}"}
            if email:
                headers["X-User-Email"] = email
            
            # Using hybrid_search as a proxy to fetch document content (Fragment Assembly)
            response = requests.post(
                f"{api_url.rstrip('/')}/api/kb/hybrid_search",
                json={
                    "intent": "knowledge_retrieval",
                    "lex_query": cloud_doc_id,
                    "vec_query": cloud_doc_id,
                    "top_k": 5
                },
                headers=headers,
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                chunks = data.get("results", [])
                if chunks:
                    cleaned_chunks = []
                    for idx, chunk in enumerate(chunks):
                        pure_chunk = _strip_qmd_metadata(chunk)
                        if pure_chunk:
                            cleaned_chunks.append(f"### [Knowledge Chunk #{idx+1}]\n{pure_chunk}")
                    cloud_content = "\n\n---\n\n".join(cleaned_chunks)
                    
                    # 4. Append Dynamic Watermark (4th Line of Defense)
                    lic_suffix = license_key[:8] if license_key else "unknown"
                    watermark = f"\n\n---\n*本笔记为 TalentMe (https://talentme.airsota.com) 专属定制编译 (License: tm-{lic_suffix})。*"
                    cloud_content += watermark
                else:
                    cloud_content = f"Error: No content found in cloud for '{cloud_doc_id}'."
            else:
                cloud_content = f"Error: Cloud API returned {response.status_code}."
        except Exception as e:
            cloud_content = f"Error: Failed to fetch from cloud. {str(e)}"
            
        # 2. Local State Logging to memory.db
        log_msg = ""
        if memory_path:
            db_path = os.path.join(memory_path, 'memory.db')
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS learning_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT,
                        summary TEXT,
                        mastery_level INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        details TEXT
                    )
                ''')
                cursor.execute(
                    "INSERT INTO learning_logs (topic, summary, mastery_level) VALUES (?, ?, ?)",
                    (cloud_doc_id, f"Initiated learning via Handshake Protocol. Intent: {user_intent}", 1)
                )
                conn.commit()
                conn.close()
                log_msg = f"✅ Successfully logged learning progress to memory.db for: {cloud_doc_id}."
            except Exception as e:
                log_msg = f"⚠️ Failed to log to memory.db: {str(e)}"
        else:
            log_msg = "⚠️ Memory path not configured, skipped local logging."
            
        # 3. Prompt Injection
        injection = f"""{log_msg}

--- CLOUD KNOWLEDGE CONTENT ---
{cloud_content}
-------------------------------
"""
        return injection
