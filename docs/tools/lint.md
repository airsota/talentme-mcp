# Lint Tool Design Document

**Phase**: 2 (P1 Tools)
**Type**: MCP Tool

## 1. 核心目标
作为本地 Markdown 知识库的健康检查器，主要任务是嗅探“死链”与“悬空链接”，防止本地图谱断层。

## 2. 接口规范
```python
def lint_wiki() -> str:
    """Scan local wiki for broken wikilinks."""
```

## 3. 核心逻辑
- **遍历扫描**：读取 `memory_path` 下所有的 `.md` 文件。
- **正则匹配**：利用 `\[\[(.*?)\]\]` 正则提取所有双括号引用的目标知识点。
- **交叉对比**：列举出现有的 Markdown 文件清单（例如 `[[A/B Testing]]` 期望存在 `A/B Testing.md`）。对比抓取到的链接，如果目标文件不存在，则计入“孤儿死链 (Orphan Links)”。
- **Prompt Injection**：将死链清单交给 Agent，强制指令其向用户警告知识断层，并推荐使用 `search` 工具去补全这些缺失概念的文档。
