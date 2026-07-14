# Interview Tool 设计文档

**Tool 名称**: `manage_interview`  
**类型**: MCP Tool  

---

## 1. 核心目标
管理本地 `memory.db` 数据库中 `interviews` 表的面试节点、时间线、阶段和录取进度，支撑求职管理面板（UX Feature 5）。

---

## 2. 哲学理念
*   **面试全流程追踪**：记录每一轮面试的具体公司、职级、轮次以及状态，同时追踪相关准备文件（`has_prep`）和复盘复盘日志（`has_debrief`）是否已生成。
*   **流程防漏预警**：列出面试进度时，检测到即将到来的轮次若缺失 PREP 突击文件，则向 Agent 输出预警提示，强力促使 Agent 引导用户完成准备。

---

## 3. 接口规范

```python
def manage_interview(
    action: str, 
    company: Optional[str] = None, 
    role: Optional[str] = None, 
    stage: Optional[str] = None, 
    status: Optional[str] = None, 
    date: Optional[str] = None,
    interview_id: Optional[int] = None
) -> str:
    """
    Manage interview timeline and states in memory.db.
    
    Args:
        action: 操作行为 ('add', 'update_status', 'mark_prep', 'mark_debrief', 'list')
        company: 公司名称 (e.g. 'Meta')
        role: 岗位名称 (e.g. 'ML Engineer')
        stage: 面试阶段/轮次 (e.g. 'Phone Screen', 'Onsite')
        status: 面试进度状态 (e.g. 'Scheduled', 'Passed', 'Rejected')
        date: 面试日期
        interview_id: 进行特定修改时的自增 ID
    """
```

---

## 4. 执行逻辑

### 4.1 SQL 数据维护
*   若数据表不存在，自动初始化包含 `has_prep` 与 `has_debrief` 状态的 `interviews` 数据表。
*   根据不同的 `action` 进行相应操作：
    *   `add`：登记新的面试信息。
    *   `update_status`：更新日期与录取状态。
    *   `mark_prep` / `mark_debrief`：标记面试准备或复盘日志完成状态为 True。
    *   `list`：列出最新的 10 条面试记录。

### 4.2 输出格式
列出数据时返回：
```text
[USER INTERVIEW TIMELINE START]
### Upcoming / Recent Interviews

| ID | Company | Role | Stage | Date | Status | PREP? | DEBRIEF? |
|---|---|---|---|---|---|---|---|
| 1 | Meta | ML Engineer | Phone Screen | 2026-07-20 | Scheduled | ❌ | ❌ |
[USER INTERVIEW TIMELINE END]
4. I notice they have upcoming interviews with `PREP?` marked as ❌. YOU MUST strongly suggest using the `tm-prep` skill or `search/learn` tools to generate a PREP document right now.
```
