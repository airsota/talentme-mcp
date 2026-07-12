import os
import sqlite3
from datetime import datetime
from mcp.server.fastmcp import FastMCP

def setup_log_learning_progress(mcp: FastMCP, memory_path: str):
    @mcp.tool()
    def log_learning_progress(topic: str, summary: str, mastery_level: int, details: str = None) -> str:
        """
        Log the user's learning progress or mock interview performance to their local memory.
        This must be called at the end of learning or interview sessions.
        
        Args:
            topic: The specific topic or question practiced.
            summary: A brief summary of what the user learned, strengths, and weaknesses.
            mastery_level: An integer from 1 to 5 indicating the user's mastery level (1=novice, 5=expert).
            details: Optional. The complete raw Q&A logs or transcript containing all user responses.
        """
        if not memory_path:
            return "Error: Memory path is not configured."
            
        db_path = os.path.join(memory_path, 'memory.db')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Ensure details column exists (Migration fallback for existing DBs)
            try:
                cursor.execute("ALTER TABLE learning_logs ADD COLUMN details TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass # Column already exists
                
            cursor.execute(
                "INSERT INTO learning_logs (topic, summary, mastery_level, details) VALUES (?, ?, ?, ?)",
                (topic, summary, mastery_level, details)
            )
            conn.commit()
            conn.close()
            
            # Also append to the LLM Wiki journal for human readability
            today = datetime.now().strftime('%Y-%m-%d')
            journal_dir = os.path.join(memory_path, "journal")
            os.makedirs(journal_dir, exist_ok=True)
            journal_path = os.path.join(journal_dir, f"{today}.md")
            
            is_new = not os.path.exists(journal_path)
            with open(journal_path, "a", encoding='utf-8') as f:
                if is_new:
                    f.write(f"---\ntitle: {today}\ncategory: journal\ntags: [daily, learning]\n---\n\n# {today}\n")
                f.write(f"\n## {datetime.now().strftime('%H:%M:%S')} - {topic}\n")
                f.write(f"**Mastery Level**: {mastery_level}/5\n\n")
                f.write(f"**Summary**:\n{summary}\n\n")
                if details:
                    f.write("### 💬 Detailed Q&A Transcript\n")
                    f.write("<details>\n")
                    f.write("<summary>点击展开查看原始问答记录 (Click to view raw Q&A logs)</summary>\n\n")
                    f.write(f"{details}\n\n")
                    f.write("</details>\n\n")
                    
            return f"Successfully logged learning progress for topic '{topic}' (including raw transcripts) to local memory (DB + Wiki Journal)."
        except Exception as e:
            return f"Error: Failed to log progress to local memory: {str(e)}"
