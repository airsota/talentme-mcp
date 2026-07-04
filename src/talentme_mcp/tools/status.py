import os
import sqlite3
from mcp.server.fastmcp import FastMCP

def setup_status_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def status() -> str:
        """
        Aggregate Mastery data into a Readiness Score and Topic Distribution.
        The Agent will use this to generate a radar chart or analytics report.
        """
        if not memory_path:
            return "Error: Memory path not configured."
            
        db_path = os.path.join(memory_path, 'memory.db')
        if not os.path.exists(db_path):
            return "No memory database found. Please use the `assess` tool first."
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learning_logs'")
            if not cursor.fetchone():
                return "Learning logs table is empty."
                
            cursor.execute("SELECT topic, mastery_level FROM learning_logs ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            latest_mastery = {}
            for row in rows:
                topic, mastery = row
                if topic not in latest_mastery:
                    latest_mastery[topic] = mastery
                    
            if not latest_mastery:
                return "No mastery data to aggregate."
                
            total_topics = len(latest_mastery)
            total_score = sum(latest_mastery.values())
            max_possible = total_topics * 5
            
            readiness_score = (total_score / max_possible) * 100 if max_possible > 0 else 0
            
            # Group topics
            mastered = []
            familiar = []
            struggling = []
            
            for topic, mastery in latest_mastery.items():
                if mastery >= 4:
                    mastered.append(topic)
                elif mastery == 3:
                    familiar.append(topic)
                else:
                    struggling.append(topic)
                    
            # Build markdown report
            report = f"### TalentMe Readiness Dashboard\n\n"
            report += f"**Overall Readiness Score**: {readiness_score:.1f}%\n"
            report += f"**Total Topics Tracked**: {total_topics}\n\n"
            
            report += "| Mastery Level | Count | Topics |\n"
            report += "|---|---|---|\n"
            report += f"| 🟢 Mastered (4-5) | {len(mastered)} | {', '.join(mastered) if mastered else 'None'} |\n"
            report += f"| 🟡 Familiar (3) | {len(familiar)} | {', '.join(familiar) if familiar else 'None'} |\n"
            report += f"| 🔴 Struggling (1-2) | {len(struggling)} | {', '.join(struggling) if struggling else 'None'} |\n"
            
            return f"""
[USER MASTERY STATUS START]
{report}
[USER MASTERY STATUS END]

🛑 [SYSTEM INSTRUCTION FOR AGENT]:
You are a Data Analyst for the user's career preparation.
YOUR IMMEDIATE ACTIONS:
1. Present the Readiness Dashboard markdown table to the user.
2. Provide a 2-sentence encouraging analysis of their current Readiness Score.
3. If they have 'Struggling' topics, strongly suggest using the `review` tool to reinforce them.
"""
        except Exception as e:
            return f"Error generating status report: {str(e)}"
