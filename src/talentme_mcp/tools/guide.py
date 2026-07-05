import os
import sqlite3
from mcp.server.fastmcp import FastMCP

def setup_guide_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def guide() -> str:
        """
        Fetch the user's current Hot Context (recent logs, plans, review targets) 
        and prompt the Agent to deliver a Daily Digest.
        """
        if not memory_path:
            return "Error: Memory path not configured. Cannot aggregate Hot Context."
            
        recent_topics = []
        weaknesses = []
        
        db_path = os.path.join(memory_path, 'memory.db')
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if learning_logs exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learning_logs'")
                if cursor.fetchone():
                    # Get recent topics (limit 3)
                    cursor.execute("SELECT topic, mastery_level FROM learning_logs ORDER BY created_at DESC LIMIT 3")
                    for row in cursor.fetchall():
                        recent_topics.append(f"{row[0]} (Mastery: {row[1]})")
                        
                    # Get weaknesses (mastery <= 2, distinct, limit 3)
                    cursor.execute("SELECT DISTINCT topic, mastery_level FROM learning_logs WHERE mastery_level <= 2 ORDER BY created_at ASC LIMIT 3")
                    for row in cursor.fetchall():
                        weaknesses.append(f"{row[0]} (Mastery: {row[1]})")
                        
                conn.close()
            except Exception as e:
                return f"Error connecting to Hot Cache: {str(e)}"
                
        # Read study-plan.md if exists
        study_plan_snippet = "No active study plan found."
        plan_path = os.path.join(memory_path, 'study-plan.md')
        if os.path.exists(plan_path):
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    content = f.read(500) # Read first 500 chars to save context
                    study_plan_snippet = content.strip() + ("..." if len(content) == 500 else "")
            except Exception:
                pass

        # Cold Start / Empty State Routing
        if not recent_topics and study_plan_snippet == "No active study plan found.":
            return """
[USER HOT CONTEXT START]
- The user's memory database is completely empty.
- No recent topics, no weaknesses, no study plan.
[USER HOT CONTEXT END]
"""
            
        # Normal Context
        recent_str = "\n".join([f"  - {t}" for t in recent_topics]) if recent_topics else "  - None"
        weak_str = "\n".join([f"  - {w}" for w in weaknesses]) if weaknesses else "  - None"
        
        return f"""
[USER HOT CONTEXT START]
- Recent Topics:
{recent_str}
- Weaknesses to Review:
{weak_str}
- Current Plan Snapshot:
  {study_plan_snippet}
[USER HOT CONTEXT END]
"""
