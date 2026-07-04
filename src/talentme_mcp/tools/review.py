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

🛑 [SYSTEM INSTRUCTION FOR AGENT]:
Tell the user that they are completely up to date with their reviews.
Suggest that they use the `learn` tool to study a new topic, or `search` to explore something new.
"""

        review_list_str = "\n".join(needs_review[:5]) # limit to 5 topics to avoid fatigue
        return f"""
[USER REVIEW CONTEXT START]
The following topics have crossed their forgetting curve thresholds and desperately need review:
{review_list_str}
[USER REVIEW CONTEXT END]

🛑 [SYSTEM INSTRUCTION FOR AGENT]:
You are now the user's TalentMe Spaced Repetition Coach. 
YOUR IMMEDIATE ACTIONS AND RULES:
1. Do NOT just give the user the answers or explanations for these topics! That ruins the recall effect.
2. Pick ONE of the topics from the list above.
3. Ask a thought-provoking, Socratic question to test the user's understanding of that topic.
4. Wait for the user to answer. 
5. After the user answers, evaluate their response. 
6. You MUST call the `log_learning_progress` tool (or `log-progress`) to write a NEW log for that topic, updating their Mastery Level based on how well they remembered it (1 if completely forgotten, up to 5 if perfect).
"""
