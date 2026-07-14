# Assess Tool 设计文档

**Tool 名称**: `assess`  
**类型**: MCP Tool  

---

## 1. 核心目标
从云端获取标准的能力评估提纲，作为新用户冷启动评测的数据源（对应 **UX Feature 1: Onboarding Assessment**）。

---

## 2. Design Philosophy
*   **流程编排分离**：Python 工具仅负责数据抓取和格式化输出。互动评测的问答循环、打分以及最终的 `study-plan.md` 生成均交由 `tm-assess` Agent Skill 执行。

---

## 3. 接口规范

```python
def assess(domain: str, level: str) -> str:
    """
    Fetch an assessment rubric from the cloud for a specific domain and level,
    and prompt the Agent to conduct an interactive evaluation.
    
    Args:
        domain: 评测领域 (e.g., "Machine Learning", "System Design")
        level: 目标职级 (e.g., "Junior", "Senior", "L5")
    """
```

---

## 4. 执行逻辑

### 4.1 云端评测提纲获取
*   以 `domain` 和 `level` 为参数请求云端接口 `/api/kb/assessment`。
*   剥离无用元数据，提取大纲内容。

### 4.2 输出格式
以 Markdown 包装返回抓取的评测提纲：
```markdown
--- CLOUD ASSESSMENT RUBRIC ({domain} - {level}) ---
(评测点与打分参考标准...)
----------------------------------------------------
```
*调用该 Tool 的 Agent 会基于此提纲并结合 `tm-assess` 提示词展开问答。*
