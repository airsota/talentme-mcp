# Edit Tool Design Document

**Phase**: 2 (P1 Tools)
**Type**: MCP Tool (Local Context)

## 1. 核心目标
补齐本地知识库的精细化修改能力，与现有的 `create_wiki_page` 和 `read_wiki_page` 共同构成完整的本地 CRUD 闭环。

## 2. 接口规范
```python
def update_wiki_page(page_name: str, mode: str, new_content: str) -> str:
    """Modify an existing local wiki page by appending or overwriting."""
```

## 3. 核心逻辑
- **参数约束**：`mode` 只允许为 `append` 或 `overwrite`。
- **安全检查**：如果 `page_name` 文件不存在，提示 Agent 应该使用 `create_wiki_page` 工具。
- **执行**：依据 `mode` 在原文件末尾追加，或者完全清空覆写。
- **反馈**：执行成功后，返回简单的确认信息，无须强求复杂的 Prompt Injection（交由通用的 `guide` 或者调用的 Agent Skill 来兜底即可）。
