import os
import json
import sqlite3
from mcp.server.fastmcp import FastMCP

def setup_import_feedback_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def import_expert_feedback(feedback_json: str) -> str:
        """
        Parse JSON feedback from an expert and calibrate the local memory.db.
        Args:
            feedback_json: A JSON string mapping topics to scores (1-5), e.g. '{"System Design": 2, "A/B Testing": 4}'
        """
        if not memory_path:
            return "Error: Memory path not configured."
            
        db_path = os.path.join(memory_path, 'memory.db')
        
        try:
            feedback_data = json.loads(feedback_json)
        except json.JSONDecodeError:
            return "Error: Invalid JSON format provided."
            
        if not isinstance(feedback_data, dict):
            return "Error: Feedback JSON must be a key-value object (topic -> score)."
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learning_logs'")
            if not cursor.fetchone():
                return "Error: learning_logs table does not exist. The user has no memory footprint yet."
                
            updated_topics = []
            for topic, score in feedback_data.items():
                try:
                    score_val = int(score)
                    if not (1 <= score_val <= 5):
                        continue # Skip invalid scores
                except ValueError:
                    continue
                    
                # Insert the calibration record
                cursor.execute(
                    "INSERT INTO learning_logs (topic, summary, mastery_level) VALUES (?, ?, ?)",
                    (topic, "[EXPERT CALIBRATION] 专家真实反馈强制覆写", score_val)
                )
                updated_topics.append(f"- **{topic}**: {score_val}/5")
                
            conn.commit()
            
            if not updated_topics:
                return "Error: No valid topics and scores found in the JSON."
                
            report = "\n".join(updated_topics)
            
            return f"""
[EXPERT FEEDBACK CALIBRATION SUCCESS]
The following expert scores have been forcibly written into the user's memory core, overwriting their subjective self-assessment:
{report}
[CALIBRATION END]

🛑 [SYSTEM INSTRUCTION FOR AGENT]:
You are now acting as the user's strict Technical Advisor.
YOUR IMMEDIATE ACTIONS:
1. Present the calibrated scores to the user.
2. Acknowledge and congratulate them on any topics scoring 4 or 5.
3. If there are topics scoring 1, 2, or 3, you MUST point out the danger (the "Delta" between their expectations and reality).
4. YOU MUST trigger the `tm-plan` or `tm-coaching-capture` logic: Propose generating a new `study-plan.md` to patch these exact weak spots immediately. Do not proceed until the user agrees.
"""
        except Exception as e:
            return f"Database error in import_expert_feedback: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()
