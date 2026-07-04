# Guide Tool Design Document

**Tool Name**: `guide`
**Phase**: 2
**Type**: MCP Tool

## 1. 核心目标 (Core Objective)
`guide` 工具作为用户每天打开 TalentMe 时的“第一站”。它的核心目标是抓取本地所有学习上下文（Hot Context），并通过 **Prompt Injection** 强引导 Agent 扮演 "Study Buddy"，主动向用户推送一份个性化的 **Daily Digest（每日简报 / F22）**。

## 2. 哲学理念 (Design Philosophy)
- **主动式关怀 (Proactive Guidance)**：传统 AI 助手是“一问一答”，而 `guide` 旨在让 Agent 做到“无问也答”。
- **上下文聚合 (Context Aggregation)**：Agent 自身无法每次对话前遍历整个数据库和文件系统。`guide` 工具用底层代码一次性聚合 SQLite 历史记录和关键规划文件，把“用户现在该干嘛”的线索精准送给 Agent。
- **与 `get_user_memory_summary` 的区别**：现有的 `get_user_memory_summary` 是一个被动的、干巴巴的取数器。`guide` 则是它的上位替代，加入了业务逻辑（计算复习目标）和强引导指令。

## 3. 接口规范 (Tool Signature)
```python
def guide() -> str:
    """
    Fetch the user's current Hot Context (recent logs, plans, review targets) 
    and prompt the Agent to deliver a Daily Digest.
    """
```

## 4. 执行逻辑 (Execution Logic)

### 4.1 本地状态聚合
1. **读取 `memory.db`**：
   - 提取最近 3-5 条学习记录。
   - 提取 Mastery 偏低（如 <= 2）且最近几天没看的薄弱点，作为**复习推荐**。
2. **读取 `study-plan.md` (如果存在)**：
   - 尝试读取用户知识库中的 `study-plan.md`，提取一小段当前的重点目标。

### 4.2 组装返回，强制引导 (Prompt Injection)
组装聚合的数据，并附加一段强有力的系统指令，要求 Agent 直接对用户说话。

**期望的返回值样例：**
```text
[USER HOT CONTEXT START]
- Recent Topics: Flash Attention (Mastery: 2)
- Weaknesses to Review: Model Parallelism (Mastery: 1)
- Current Plan: Finish Distributed Training module this week.
[USER HOT CONTEXT END]

🛑 [SYSTEM INSTRUCTION FOR AGENT]:
You are the user's TalentMe Study Buddy. 
Based on the HOT CONTEXT above, YOUR IMMEDIATE NEXT ACTION IS:
1. Greet the user warmly based on the time of day.
2. Present a short, encouraging "Daily Digest" (Feature 22).
3. Suggest 2 highly actionable next steps for today (e.g., "Would you like to review Model Parallelism, or learn a new topic?").
Do NOT wait for the user to ask. Speak directly to them now.
```
