# TalentMe Antigravity Rules
When the user uses the prefix '/talentme' or '/tm', you MUST:
1. Call the 'list_agent_skills' tool to see available memory skills.
2. Read the appropriate skill instructions (usually 'wiki-query').
3. Use the local wiki tools to search the user's private memory at /home/suiyaoc/TalentMe/talentme-mcp/test_workspace/mock_memory.
4. Provide an answer based ONLY on the private memory content.
5. NEVER return absolute file paths. Use [[Page Name]] instead.
