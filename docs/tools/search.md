# Search Tool Design Document

**Tool Name**: `search`
**Phase**: 2
**Type**: MCP Tool

## 1. 核心目标 (Core Objective)
将原有的 `search_local_wiki` 与 `cloud_knowledge_query` 合并为一个统一的双源混合检索工具。
为 Agent 提供一个具备“全局视角”的数据接口，使其能瞬间判断知识是仅存在于云端、还是已经内化到本地。

## 2. 哲学理念 (Design Philosophy)
- **云端作为“柏拉图理念世界”**：云端知识库通过 QMD 提供纯粹的“知识块”（Pure Knowledge Content）。返回的云端数据将被强制剥离一切诸如 `filename`、`path` 等可能带来信息架构偏见的 Meta 数据。
- **本地作为“个性化具象世界”**：本地知识库保留用户的特定结构。返回的本地数据将包含具体的 `path` 和 `snippet`，方便 Agent 定位、链接甚至重构。
- 这种分离强制了 `learn` 工作流的发生：当 Agent 发现云端有纯净知识而本地没有时，它必须基于用户的语境对其进行重组和“实例化命名”。

## 3. 接口规范 (Tool Signature)

```python
def search(query: str, scope: Literal["local", "cloud", "all"] = "all", lex_query: str = None, vec_query: str = None, top_k: int = 5) -> str:
    """
    Execute a search against Local, Cloud, or Both Knowledge Bases.
    
    Args:
        query: Main search string. Used to scan the local vault. 
               Will be used as default for lex_query/vec_query if they are not provided.
        scope: "local" (save tokens, local only), "cloud" (cloud only), or "all" (hybrid dual-source).
        lex_query: Keyword-based query for cloud (e.g. exact names).
        vec_query: Semantic query for cloud QMD search.
        top_k: Number of chunks to retrieve from cloud.
    """
```

## 4. 执行逻辑 (Execution Logic)

### 4.0 路由分发 (Routing by Scope)
- 如果 `scope == "local"`，直接短路返回本地结果（节省 Token 消耗，且响应极快）。
- 如果 `scope == "cloud"`，仅调用云端检索。
- 如果 `scope == "all"`，并行执行双源检索，并拼装对比视图。

### 4.1 本地检索 (Local Search)
1. 遍历用户设定的 `memory_path`。
2. 过滤掉安全路径以及特殊系统目录（如 `.skills`, `_meta`）。
3. 使用正则（未来可拓展为 sqlite FTS）匹配 `.md` 文件内容。
4. 提取匹配处前后的 Snippet（约 100 字符），附带上文件的相对路径（以 `[[path]]` 形式呈现）。

### 4.2 云端检索 (Cloud Search)
1. 根据环境变量 `api_url` 和 `license_key`，发送请求至 `api/kb/hybrid_search`。
2. 获取云端 QMD 引擎返回的检索块。
3. **净化处理 (Purification)**：通过正则表达式或预定义的截断规则，清洗掉返回块中自带的可能代表文件路径或标题的头信息，只保留纯粹的段落和知识主体。

### 4.3 组装返回 (Formatting)
将结果转化为 JSON (或清晰的 Markdown 块) 返回给调用此 Tool 的 Agent。

**期望的返回值样例：**
```json
{
  "local_results": [
    {
      "path": "ML/Transformer.md",
      "snippet": "...Transformer 依赖于自注意力机制，通过..."
    }
  ],
  "cloud_pure_knowledge": [
    "注意力机制通过计算 Query 和 Key 的点积来分配权重，从而使得模型能够关注到序列中不同位置的输入...",
    "KV Cache 是一种在生成式模型的推理阶段被广泛采用的加速技术..."
  ]
}
```

## 5. 对已有实现的改进
- 摒弃了参考项目中 `llm-wiki-agent/tools/query.py` 将检索与生成强绑定的做法，严格保持 `search` 作为纯粹的 DataSource Tool。
- 保留了 `llmwiki/mcp/tools/search.py` 中对 Snippet 提取的优秀体验，并拓展了它的搜索边界（引入云端）。
