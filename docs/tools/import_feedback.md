# Import Feedback Tool Design Document

**Phase**: 2 (P1 Tools)
**Type**: MCP Tool

## 1. 核心目标
承接 1v1 专家服务（UX Feature 12）。当用户获得专家发回的 JSON 格式结构化打分后，此工具负责将其解析并作为“绝对真理”校准本地知识库的熟练度。

## 2. 接口规范
```python
def import_expert_feedback(feedback_json: str) -> str:
    """Parse JSON feedback from expert and calibrate local memory.db."""
```

## 3. 核心逻辑
- **输入要求**：期望接收形如 `{"System Design": 4, "A/B Testing": 2, "SQL": 5}` 的 JSON 字符串。
- **数据校准**：复用现有的 `learning_logs` 表，将专家的评分直接作为最新的一条记录追加进去，并附带特殊的摘要标记（如 `Source: Expert Calibration`）。这会立刻影响 `review` 工具在明天的遗忘曲线抽取权重。
- **Prompt Injection**：工具返回后，要求 Agent 用“专家顾问”的口吻，恭喜高分项，并督促用户立刻对低分项（例如 A/B Testing）启动突击学习计划。
