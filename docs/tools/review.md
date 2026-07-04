# Review Tool Design Document

**Phase**: 2 (P1 Tools)
**Type**: MCP Tool

## 1. 核心目标 (Core Objective)
作为间隔重复引擎，通过计算遗忘曲线（Ebbinghaus），抓取亟需复习的知识点，并强控 Agent 化身“抽查教练”。

## 2. 接口规范
```python
def review() -> str:
    """Fetch topics that need spaced repetition based on forgetting curve."""
```

## 3. 底层逻辑
1. 提取各个 `topic` 最新的 `mastery_level` 和 `created_at`。
2. 基础间隔算法：
   - Mastery <= 2: 1 天后需复习。
   - Mastery == 3: 3 天后需复习。
   - Mastery >= 4: 7 天后需复习。
3. 如果满足复习条件，则提取为目标。
4. **Prompt Injection**：要求 Agent 一次抛出一个问题来考察用户，不要直接给答案。复习结束后调用 `log_learning_progress` 写入新熟练度。
