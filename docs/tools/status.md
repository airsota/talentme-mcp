# Status Tool Design Document

**Phase**: 2 (P1 Tools)
**Type**: MCP Tool

## 1. 核心目标 (Core Objective)
将干瘪的数据库打分聚合成可视化的“面试就绪度 (Readiness Score)”和能力分布矩阵。

## 2. 接口规范
```python
def status() -> str:
    """Aggregate Mastery data into a Readiness Score and Topic Distribution."""
```

## 3. 底层逻辑
1. 提取所有独立 `topic` 的最高 `mastery_level`。
2. 计算 **Readiness Score** = (当前总 Mastery / 目标总 Mastery(Topic数*5)) * 100%。
3. 将数据格式化为 Markdown 表格，以便 Agent 在前端渲染。
4. **Prompt Injection**：要求 Agent 以数据分析师的口吻，为用户总结强项和弱项，并给出下一步建议。
