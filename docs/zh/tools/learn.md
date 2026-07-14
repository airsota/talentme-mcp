# Learn Tool 设计文档

**Tool 名称**: `learn`  
**类型**: MCP Tool  

---

## 1. 核心目标
启动针对特定云端文档的个性化伴学进程（“握手协议”）。它负责从云端获取标准知识要点，在本地添加安全水印，并向 `memory.db` 写入初始的学习进度日志。

---

## 2. 哲学理念
*   **数据与逻辑分离**：`learn` 工具只负责提取数据并写入进度日志，具体的知识提炼和本地写文件流程交由调用此工具的 Agent Skill（`bridge-sync-and-digest`）完成。
*   **提示词解耦**：不在 Python 端直接返回复杂的系统引导指令，保持接口的简洁，将决策逻辑置于 SOP 文件中。

---

## 3. 接口规范

```python
def learn(cloud_doc_id: str, user_intent: str) -> str:
    """
    Start a personalized learning session for a cloud document (The Handshake Protocol).
    
    Args:
        cloud_doc_id: 待获取的云端文档标识符。
        user_intent: 用户学习该知识点的具体目的或视角（如 "MLE 面试准备"）。
    """
```

---

## 4. Execution Logic

### 4.1 云端数据抓取与防伪
*   使用关键字通过云端混合检索接口拉取 `cloud_doc_id` 对应的分块数据。
*   合并数据，剥离 QMD 文件头信息。
*   在段落末尾注入由 license key 经 SHA-256 签名生成的八位十六进制防伪水印。

### 4.2 SQLite 进度登记
在本地 `memory.db` 的 `learning_logs` 表中插入一条记录：
*   设定 `topic = cloud_doc_id`
*   设定 `summary = "Initiated learning via Handshake Protocol. Intent: {user_intent}"`
*   初始化 `mastery_level = 1`

### 4.3 输出格式
返回本地写入状态与获取的知识文本：
```markdown
✅ Successfully logged learning progress to memory.db for: {cloud_doc_id}.

--- CLOUD KNOWLEDGE CONTENT ---
### [Knowledge Chunk #1]
(知识要点...)
---
*本笔记为 TalentMe (https://talentme.airsota.com) 专属定制编译 (License: tm-hash)*
-------------------------------
```
