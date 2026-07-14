# Status Tool 设计文档

**Tool 名称**: `status`  
**类型**: MCP Tool  

---

## 1. 核心目标
聚合本地 `memory.db` 数据库中的 mastery 掌握度分值，计算出百分制的就绪度评分（Readiness Score），并输出各知识点的层级分布，为 Agent 绘制技能雷达图和能力评估报告提供数据支撑（UX Feature 19）。

---

## 2. 哲学理念
*   **指标封装**：将底层的复杂聚合算法封装为极简的 Markdown 面板报告，减少大模型解析原始 SQL 的计算成本。
*   **按需聚焦**：清晰分类熟练度等级（1-5），使 Agent 在做计划和复习指引时能够立刻抓取薄弱点。

---

## 3. 接口规范

```python
def status() -> str:
    """
    Aggregate Mastery data into a Readiness Score and Topic Distribution.
    The Agent will use this to generate a radar chart or analytics report.
    """
```

---

## 4. 执行逻辑

### 4.1 SQLite 数据统计
*   读取 `learning_logs`，获取每个 topic 最近一次登记的 mastery 分数。
*   计算已掌握的总分并与最大可能得分做比例折算，输出百分制的 Readiness Score。

### 4.2 熟练度分层
将知识点划分为三层结构：
*   🟢 **已掌握 (Mastered)**：Mastery level >= 4
*   🟡 **已熟悉 (Familiar)**：Mastery level == 3
*   🔴 **待提高 (Struggling)**：Mastery level <= 2

### 4.3 输出格式
返回 Markdown 就绪度报表面板：
```text
[USER MASTERY STATUS START]
### TalentMe Readiness Dashboard

**Overall Readiness Score**: 78.5%
**Total Topics Tracked**: 12

| Mastery Level | Count | Topics |
|---|---|---|
| 🟢 Mastered (4-5) | 4 | Transformers, Self-Attention, CNNs |
| 🟡 Familiar (3) | 5 | PyTorch, Backpropagation, SGD |
| 🔴 Struggling (1-2) | 3 | Distributed Training, Flash Attention |
[USER MASTERY STATUS END]
```
