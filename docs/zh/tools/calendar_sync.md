# Calendar Sync Tool Design Document

**Phase**: 2 (P2 Tools)
**Type**: MCP Tool

## 1. 核心目标
支持（UX Feature 10）的日程驱动逻辑，为 Agent 提供下发会议和日历的触手。

## 2. 接口规范
```python
def calendar_sync(title: str, date: str, description: str = "") -> str:
    """Sync a calendar event into the unified memory database."""
```

## 3. 核心逻辑
- **统一存储**：绝对复用现有的 `memory.db`，若不存在则动态创建 `events` 表（`id`, `title`, `event_date`, `description`, `created_at`）。
- **执行**：插入新记录，将所有打卡、面试提醒集中在这个中枢库内。
- **Prompt Injection**：写入成功后，要求 Agent 贴心地提醒用户已经设定好日程，并建议用户在临近日期时，再次调起平台。
