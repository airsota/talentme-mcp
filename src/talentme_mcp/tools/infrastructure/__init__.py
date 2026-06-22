from .list_agent_skills import setup_list_agent_skills
from .read_agent_skill_instruction import setup_read_agent_skill_instruction
from .check_user_auth_status import setup_check_user_auth_status

def setup_infrastructure_tools(mcp, api_url: str, license_key: str, email: str = None):
    setup_list_agent_skills(mcp, api_url, license_key, email)
    setup_read_agent_skill_instruction(mcp, api_url, license_key, email)
    setup_check_user_auth_status(mcp, api_url, license_key, email)
