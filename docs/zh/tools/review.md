# Review Tool 设计文档

**Tool 名称**: `review`  
**类型**: MCP Tool  

---

## 1. Core Objective
根据艾宾浩斯遗忘曲线模型，计算并拉取本地知识库中已经超过遗忘临界值、迫切需要复习的知识点。

---

## 2. Design Philosophy
*   **熟练度衰减判定**：复习周期的触发门槛与熟练度挂钩，低熟练度知识点衰减极快（1 天即达临界点），需要更频繁地抽查。
*   **防认知过载**：每次召回上限为 5 项，防止大模型一次性推送过多复习任务导致用户疲劳。

---

## 3. 接口规范

```python
def review() -> str:
    """
    Fetch topics that need spaced repetition based on the Ebbinghaus forgetting curve.
    The Agent will receive these topics and act as a Spaced Repetition Coach.
    """
```

---

## 4. 执行逻辑

### 4.1 遗忘度计算
*   扫描 `learning_logs` 中所有记录，找出每个 topic 对应的最新登记时间及 `mastery_level`。
*   计算当前时间与上次登记时间的日期间隔 `days_elapsed`。
*   匹配艾宾浩斯临界周期门槛：
    *   `mastery_level <= 2`：复习间隔为 1 天。
    *   `mastery_level == 3`：复习间隔为 3 天。
    *   `mastery_level >= 4`：复习间隔为 7 天。
*   判定 `days_elapsed >= threshold` 的知识点为过期，加入复习队列。

### 4.2 输出格式
若没有过期的复习点：
```text
[USER REVIEW CONTEXT]
No topics currently meet the threshold for spaced repetition. The user's memory is fresh!
[USER REVIEW END]
```

若存在待复习项：
```text
[USER REVIEW CONTEXT START]
The following topics have crossed their forgetting curve thresholds and desperately need review:
- **Distributed Training** (Mastery: 2, Days elapsed: 4, Threshold: 1)
- **Flash Attention** (Mastery: 3, Days elapsed: 6, Threshold: 3)
[USER REVIEW CONTEXT END]
```
