import os
import sqlite3
from typing import Optional
from mcp.server.fastmcp import FastMCP

def setup_interview_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def manage_interview(
        action: str, 
        company: Optional[str] = None, 
        role: Optional[str] = None, 
        stage: Optional[str] = None, 
        status: Optional[str] = None, 
        date: Optional[str] = None,
        interview_id: Optional[int] = None
    ) -> str:
        """
        Manage interview timeline and states in memory.db.
        Args:
            action: 'add', 'update_status', 'mark_prep', 'mark_debrief', or 'list'
            company: Company name (e.g. 'Meta')
            role: Role applied for (e.g. 'ML Engineer')
            stage: Interview stage (e.g. 'Phone Screen', 'Onsite')
            status: Status (e.g. 'Scheduled', 'Passed', 'Rejected')
            date: Date of interview
            interview_id: Required for 'update_status', 'mark_prep', 'mark_debrief' if company/role/stage not uniquely identifying.
        """
        if not memory_path:
            return "Error: Memory path not configured."
            
        db_path = os.path.join(memory_path, 'memory.db')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Auto-create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT,
                    role TEXT,
                    stage TEXT,
                    status TEXT,
                    interview_date TEXT,
                    has_prep BOOLEAN DEFAULT 0,
                    has_debrief BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            if action == "add":
                if not all([company, role, stage]):
                    return "Error: 'company', 'role', and 'stage' are required for 'add' action."
                cursor.execute(
                    "INSERT INTO interviews (company, role, stage, status, interview_date) VALUES (?, ?, ?, ?, ?)",
                    (company, role, stage, status or "Scheduled", date)
                )
                conn.commit()
                row_id = cursor.lastrowid
                return f"Successfully added interview round (ID: {row_id}): {company} - {role} ({stage})."
                
            elif action == "update_status":
                if not interview_id and not (company and role and stage):
                     return "Error: Must provide 'interview_id' or ('company', 'role', 'stage') to update."
                
                if interview_id:
                     cursor.execute("UPDATE interviews SET status = ?, interview_date = COALESCE(?, interview_date) WHERE id = ?", (status, date, interview_id))
                else:
                     cursor.execute("UPDATE interviews SET status = ?, interview_date = COALESCE(?, interview_date) WHERE company = ? AND role = ? AND stage = ?", (status, date, company, role, stage))
                conn.commit()
                return "Successfully updated interview status."
                
            elif action in ["mark_prep", "mark_debrief"]:
                field = "has_prep" if action == "mark_prep" else "has_debrief"
                if interview_id:
                     cursor.execute(f"UPDATE interviews SET {field} = 1 WHERE id = ?", (interview_id,))
                else:
                     cursor.execute(f"UPDATE interviews SET {field} = 1 WHERE company = ? AND role = ? AND stage = ?", (company, role, stage))
                conn.commit()
                return f"Successfully marked {field} as True."
                
            elif action == "list":
                cursor.execute("SELECT id, company, role, stage, status, interview_date, has_prep, has_debrief FROM interviews ORDER BY interview_date ASC, created_at DESC LIMIT 10")
                rows = cursor.fetchall()
                if not rows:
                    return "No interviews found in the database."
                    
                report = "### Upcoming / Recent Interviews\n\n"
                report += "| ID | Company | Role | Stage | Date | Status | PREP? | DEBRIEF? |\n"
                report += "|---|---|---|---|---|---|---|---|\n"
                
                needs_prep_alert = False
                for row in rows:
                    r_id, r_comp, r_role, r_stage, r_stat, r_date, r_prep, r_deb = row
                    prep_str = "✅" if r_prep else "❌"
                    deb_str = "✅" if r_deb else "❌"
                    if not r_prep and r_stat != "Rejected" and r_stat != "Passed":
                        needs_prep_alert = True
                    report += f"| {r_id} | {r_comp} | {r_role} | {r_stage} | {r_date or 'TBD'} | {r_stat} | {prep_str} | {deb_str} |\n"
                
                injection = f"""
[USER INTERVIEW TIMELINE START]
{report}
[USER INTERVIEW TIMELINE END]
"""
                if needs_prep_alert:
                    injection += '4. I notice they have upcoming interviews with `PREP?` marked as ❌. YOU MUST strongly suggest using the `tm-prep` skill or `search/learn` tools to generate a PREP document right now.\n'
                
                return injection
                
            else:
                return f"Error: Unknown action '{action}'"
                
        except Exception as e:
            return f"Database error in manage_interview: {str(e)}"
        finally:
            conn.close()
