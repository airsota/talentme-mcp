# Guide Tool 设计文档

**Tool 名称**: `guide`  
**Type**: MCP Tool  

---

## 1. 核心目标
聚合本地最新的学习日志与学习计划状态（Hot Context），并推送给大模型助手，以生成个性化的每日简报（Daily Digest，UX Feature 22）。

---

## 2. 哲学理念
*   **高效聚合**：底层的 Python 逻辑在一次调用中完成对 SQLite 和 Markdown 的扫描，防止大模型助手使用大量的独立读取工具而造成 Token 浪费与延迟。
*   **支持空白冷启动**：如果检测到本地数据库完全为空，会返回干净的冷启动状态提示，引导 AI 开展 Onboarding 问答。

---

## 3. 接口规范

```python
def guide() -> str:
    """
    Fetch the user's current Hot Context (recent logs, plans, review targets) 
    and prompt the Agent to deliver a Daily Digest.
    """
```

---

## 4. 执行逻辑

### 4.1 本地上下文聚合
*   读取 `memory.db` 中的 `learning_logs` 数据：
    *   获取最近更新的 3 条记录。
    *   获取 3 个最早学习且 mastery <= 2 的薄弱点作为推荐复习项。
*   读取 `study-plan.md` 的前 500 个字符。

### 4.2 输出格式
如果知识库为空：
```text
[USER HOT CONTEXT START]
- The user's memory database is completely empty.
- No recent topics, no weaknesses, no study plan.
[USER HOT CONTEXT END]
```

如果包含数据：
```text
[USER HOT CONTEXT START]
- Recent Topics:
  - Transformers (Mastery: 3)
- Weaknesses to Review:
  - Distributed Training (Mastery: 2)
- Current Plan Snapshot:
  # 14天学习规划...
[USER HOT CONTEXT END]
```
