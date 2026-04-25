import os
import sqlite3
from datetime import datetime
from mcp.server.fastmcp import FastMCP

def setup_user_log_skills(mcp: FastMCP, memory_path: str):
    
    @mcp.tool()
    def log_learning_progress(topic: str, summary: str, mastery_level: int) -> str:
        """
        Log the user's learning progress or mock interview performance to their local memory.
        This must be called at the end of learning or interview sessions.
        
        Args:
            topic: The specific topic or question practiced (e.g., "Transformers", "LeetCode 1")
            summary: A brief summary of what the user learned, their strengths, and weaknesses.
            mastery_level: An integer from 1 to 5 indicating the user's mastery level (1=novice, 5=expert).
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        db_path = os.path.join(memory_path, 'memory.db')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO learning_logs (topic, summary, mastery_level) VALUES (?, ?, ?)",
                (topic, summary, mastery_level)
            )
            conn.commit()
            conn.close()
            
            # Also append to the LLM Wiki journal for human readability
            today = datetime.now().strftime('%Y-%m-%d')
            journal_dir = os.path.join(memory_path, "journal")
            os.makedirs(journal_dir, exist_ok=True)
            journal_path = os.path.join(journal_dir, f"{today}.md")
            
            # Write with Obsidian-style header if file is new
            is_new = not os.path.exists(journal_path)
            with open(journal_path, "a", encoding='utf-8') as f:
                if is_new:
                    f.write(f"---\ntitle: {today}\ncategory: journal\ntags: [daily, learning]\n---\n\n# {today}\n")
                f.write(f"\n## {datetime.now().strftime('%H:%M:%S')} - {topic}\n")
                f.write(f"**Mastery Level**: {mastery_level}/5\n\n")
                f.write(f"**Summary**:\n{summary}\n\n")
                
            return f"Successfully logged learning progress for topic '{topic}' to local memory (DB + Wiki Journal)."
        except Exception as e:
            return f"Failed to log progress: {str(e)}"

    @mcp.tool()
    def get_user_memory_summary() -> str:
        """
        Retrieve a summary of the user's past learning logs to understand their context and weaknesses.
        Call this at the beginning of an interview or learning session to personalize the experience.
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
                
            result = ["Recent Learning History:"]
            for row in rows:
                result.append(f"- [{row[0]}] Topic: {row[1]} (Mastery: {row[3]}/5) | Note: {row[2]}")
                
            return "\\n".join(result)
        except Exception as e:
            return f"Failed to retrieve memory: {str(e)}"
