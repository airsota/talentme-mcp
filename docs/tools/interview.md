# Interview Tool Design Document

**Phase**: 2 (P1 Tools)
**Type**: MCP Tool

## 1. 核心目标
提供一个基于 `memory.db` 的面试时间线底层 CRUD 接口（支撑 UX Feature 5）。它将用户的投递和面试状态聚合在本地。

## 2. 接口规范
```python
def manage_interview(action: str, company: str=None, role: str=None, stage: str=None, status: str=None, date: str=None) -> str:
    """Manage interview timeline and states in memory.db."""
```

## 3. 核心逻辑
- **表结构**：如果 `interviews` 表不存在则自动创建，包含字段 `id`, `company`, `role`, `stage` (具体轮次), `status`, `interview_date`, `has_prep` (布尔值), `has_debrief` (布尔值), `created_at`。每经历一个新轮次，即新增一条该轮次的记录。
- **Action 分发**：
  - `add`: 插入新轮次记录。
  - `update_status`: 更新现有轮次的状态。
  - `mark_doc`: 标记某次面试已完成 PREP 或 DEBRIEF。
  - `list`: 列出近期所有的面试轮次及准备状态。
- **与状态的联动 (Readiness)**：当查询即将到来的面试时，工具本身只返回干瘪的面试信息，但通过 Prompt Injection 引导大模型去调用 `status` 工具。
- **Prompt Injection**：
  - 如果发现 `has_prep` 为 False，强制让 Agent 提醒用户：“您还没有为这场面试做 PREP，需要我现在为您生成吗？”
  - 强制让 Agent 调用 `status` 工具，结合用户的历史 Mastery 打分，给出一句对于“本场面试你准备得如何”的综合判定。
