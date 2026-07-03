# Learn Tool Design Document

**Tool Name**: `learn`
**Phase**: 2
**Type**: MCP Tool

## 1. 核心目标 (Core Objective)
将原有的 `read_cloud_document`、`create_wiki_page` 和 `log_learning_progress` 聚合为一个高内聚的工作流入口。
解决的核心痛点：在旧架构中，Agent 需要分三次调用不同的工具（读云端 -> 写本地 -> 记进度），容易中途由于 Context 中断或 Token 限制导致失败。

## 2. 哲学理念 (Design Philosophy)
- **Agent 是“大脑”，Tool 是“四肢”**：由于 MCP Server 本身不直连大模型（即它不是一个独立的 RAG 服务），“个性化编译（Synthesis）”这部分最消耗智能的工作必须交由调度此 Tool 的 LLM (Agent) 来完成。
- **Tool 的原子性**：`learn` Tool 作为一个“握手协议”。Agent 调用 `learn` 宣告：“我要开始学习这个知识点了。” Tool 则负责在底层打通云与端的管道。

## 3. 接口规范 (Tool Signature)

```python
def learn(cloud_doc_id: str, user_intent: str) -> str:
    """
    Start a personalized learning session for a cloud document.
    
    Args:
        cloud_doc_id: The identifier of the cloud document to fetch.
        user_intent: The specific angle or role the user wants to learn this from (e.g., "MLE interview prep").
    """
```

## 4. 执行逻辑 (Execution Logic)

### 4.1 云端数据获取
1. 使用 `api_url` 和 `license_key` 从云端拉取 `cloud_doc_id` 对应的完整纯净内容 (Pure Knowledge)。

### 4.2 本地状态写入 (Log Progress)
2. 在本地知识库的隐藏状态表（或 SQLite `memory.db`）中，插入一条记录：标记当前用户正在学习 `cloud_doc_id`，并打上时间戳。这可以用于后续的 `review` 和 `status` 雷达图。

### 4.3 组装返回，强制引导 Agent (Prompt Injection)
3. 这是一个架构上的巧思：`learn` Tool 的返回值不是简单的 JSON，而是一段**带有系统指令的 Markdown**。
它将纯净知识和后续指令一并喂给 Agent 的 Context 中，从而实现一键工作流的闭环。

**期望的返回值样例：**
```markdown
✅ Successfully logged learning progress for: {cloud_doc_id}.

--- CLOUD KNOWLEDGE CONTENT ---
(云端完整纯净内容...)
-------------------------------

🛑 **SYSTEM INSTRUCTION FOR AGENT**:
You have successfully fetched the pure knowledge from the cloud.
YOUR NEXT IMMEDIATE ACTION:
1. Synthesize the above content based on the user's local context and intent (`{user_intent}`).
2. Create a new local wiki page in `concepts/` or `questions/` using standard markdown frontmatter.
3. Use the `write_to_file` tool to save your synthesis directly to the local vault.
4. Notify the user that the knowledge has been successfully internalized.
```

## 5. 为什么不直接在 Tool 里完成“写入本地”？
如果在 `learn` Tool 内部直接通过代码调用 LLM API 并写文件，这会导致：
1. 双倍 Token 计费（Agent 思考一次，MCP 内部再发一次请求）。
2. Agent 丢失了对文件生成过程的感知，无法进行实时的 `cross-link` (补全双向链接) 等精细化操作。
通过将“知识+强制指令”返回给 Agent，我们完美保留了 Agent 的自主智能，同时简化了操作路径。
