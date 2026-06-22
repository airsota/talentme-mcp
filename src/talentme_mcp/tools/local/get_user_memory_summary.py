import os
import sqlite3
from mcp.server.fastmcp import FastMCP

def setup_get_user_memory_summary(mcp: FastMCP, memory_path: str):
    @mcp.tool()
    def get_user_memory_summary() -> str:
        """
        Retrieve a summary of the user's past learning logs to personalize the experience.
        SECURITY RULE: This tool returns a sanitized summary. It does NOT provide raw database access.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        db_path = os.path.join(memory_path, 'memory.db')
        if not os.path.exists(db_path):
            return "User has no memory logs yet."
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, topic, summary, mastery_level FROM learning_logs ORDER BY timestamp DESC LIMIT 5")
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "User has no learning logs yet."
                
            result = ["### Recent Learning Summary (Logical View):"]
            for row in rows:
                result.append(f"- **{row[1]}**: {row[2]} (Mastery: {row[3]}/5)")
                
            return "\n".join(result)
        except Exception:
            return "Error: Failed to retrieve memory summary due to a secure database restriction."
