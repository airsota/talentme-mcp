import os
import sqlite3
from datetime import datetime
from mcp.server.fastmcp import FastMCP

def setup_review_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def review() -> str:
        """
        Fetch topics that need spaced repetition based on the Ebbinghaus forgetting curve.
        The Agent will receive these topics and act as a Spaced Repetition Coach.
        """
        if not memory_path:
            return "Error: Memory path not configured. Cannot aggregate review targets."
            
        db_path = os.path.join(memory_path, 'memory.db')
        if not os.path.exists(db_path):
            return "No memory database found. Please use the `assess` or `learn` tools first."
            
        needs_review = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learning_logs'")
            if not cursor.fetchone():
                return "Learning logs table is empty. Nothing to review."
                
            # Fetch all logs ordered by timestamp DESC
            cursor.execute("SELECT topic, mastery_level, created_at FROM learning_logs ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            # Keep only the latest log per topic
            latest_logs = {}
            for row in rows:
                topic, mastery_level, created_at_str = row
                if topic not in latest_logs:
                    latest_logs[topic] = {
                        "mastery": mastery_level,
                        "created_at": created_at_str
                    }
                    
            # Calculate forgetting curve
            now = datetime.now()
            for topic, data in latest_logs.items():
                mastery = data["mastery"]
                created_at_dt = datetime.fromisoformat(data["created_at"])
                days_elapsed = (now - created_at_dt).days
                
                # Ebbinghaus thresholds
                threshold = 7
                if mastery <= 2:
                    threshold = 1
                elif mastery == 3:
                    threshold = 3
                    
                if days_elapsed >= threshold:
                    needs_review.append(f"- **{topic}** (Mastery: {mastery}, Days elapsed: {days_elapsed}, Threshold: {threshold})")
                    
        except Exception as e:
            return f"Error connecting to Hot Cache: {str(e)}"
            
        if not needs_review:
            return """
[USER REVIEW CONTEXT]
No topics currently meet the threshold for spaced repetition. The user's memory is fresh!
[USER REVIEW END]
"""

        review_list_str = "\n".join(needs_review[:5]) # limit to 5 topics to avoid fatigue
        return f"""
[USER REVIEW CONTEXT START]
The following topics have crossed their forgetting curve thresholds and desperately need review:
{review_list_str}
[USER REVIEW CONTEXT END]
"""
