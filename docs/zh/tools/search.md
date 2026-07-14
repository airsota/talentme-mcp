# Search Tool 设计文档

**Tool 名称**: `search`  
**类型**: MCP Tool  

---

## 1. 核心目标
将原有的本地 Wiki 检索与云端知识库检索合并为一个统一的双源混合检索工具。为 AI 助手提供全局视角，使其能瞬间判断知识是仅存在于云端、还是已经内化到本地。

---

## 2. 哲学理念
*   **云端作为“柏拉图理念世界”**：云端知识库通过 QMD 提供纯粹的“知识块”（Pure Knowledge Content），返回时剥离所有文件名或标题信息，以防止大模型产生架构偏见。
*   **本地作为“个性化具象世界”**：本地检索包含文件相对路径和匹配的 Snippet，允许 Agent 执行重构和双链指向。
*   **职责分离**：当 Agent 发现云端有相关知识而本地不存在时，大模型必须引导调用 `learn` 工作流对知识点进行实例化和本地落盘。

---

## 3. 接口规范

```python
def search(query: str, scope: Literal["local", "cloud", "all"] = "all", lex_query: str = None, vec_query: str = None, top_k: int = 5) -> str:
    """
    Execute a Hybrid Dual-Source Search against both Local and Cloud Knowledge Bases.
    
    Args:
        query: 主查询字符串。用于扫描本地 vault，若未提供 lex_query/vec_query，将以此作为默认值。
        scope: 检索范围。"local" (仅本地), "cloud" (仅云端), 或 "all" (双源混合检索)。
        lex_query: 云端关键字检索查询词。
        vec_query: 云端向量/语义检索查询词。
        top_k: 从云端拉取的知识分块数量。
    """
```

---

## 4. 执行逻辑

### 4.0 路由分发
*   `scope == "local"`：仅扫描本地 Obsidian 工作区（跳过 `.skills`, `_meta`, `_raw` 等目录）。
*   `scope == "cloud"`：仅调用云端接口 `api/kb/hybrid_search`。
*   `scope == "all"`：并行执行双源检索，并拼装结果。

### 4.1 本地正则扫描
*   遍历 `memory_path` 下的所有 `.md` 文件，利用正则表达式匹配查询关键字。
*   返回相对路径与匹配段落前后的 Snippet（约 200 字符）。

### 4.2 云端混合检索
*   通过 POST 请求将检索指令和 Token 传入 `/api/kb/hybrid_search`。
*   对返回的数据进行清洗，剔除 QMD 的标题元数据，只保留知识主体。

### 4.3 输出格式
返回格式化后的 JSON 字符串：
```json
{
  "local_results": [
    {
      "path": "concepts/Transformer.md",
      "snippet": "...Transformer 架构依赖于自注意力机制，通过..."
    }
  ],
  "cloud_pure_knowledge": [
    "KV Cache 是一种在生成式模型推理阶段被广泛采用的加速技术..."
  ]
}
```
