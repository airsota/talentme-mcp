# Rebuild Wiki Graph Tool 设计文档

**Tool 名称**: `rebuild_wiki_graph`  
**类型**: MCP Tool  

---

## 1. 核心目标
全局检索本地知识库所有卡片，建立概念索引字典，自动在各 Markdown 文件的正文语境内建立双向链接 `[[wikilinks]]`，追加 Cross-References 并生成全局目录文件 `glossary.md`。

---

## 2. 哲学理念
*   **语法分块保护 (Tokenizer)**：在织网链接时，使用分词正则跳过 YAML Frontmatter、代码块、行内代码、标题行以及现有双链，防止破坏原有的 Markdown 编译结构。
*   **数据完整性**：动态建立索引和汇总。同时在知识库根目录重新编译输出一个包含首字母分类标题、概念概述和直连双链的 `glossary.md` 索引词典。

---

## 3. 接口规范

```python
def rebuild_wiki_graph(target_dir: str = None) -> str:
    """
    Rebuild the Knowledge Base graph. Cleans legacy formats, generates a global glossary.md,
    injects safe semantic wikilinks across all markdown files, and auto-appends Cross-References.
    
    Args:
        target_dir: 待重建的知识库路径。若未提供，默认使用配置的全局路径。
    """
```

---

## 4. 执行逻辑

### 4.1 字典构建
*   扫描本地所有有效 `.md` 文件（剔除 glossary, changelog, index 等文件）。
*   提取 YAML 标题与正文第一行用于快速词典的术语描述。

### 4.2 词素匹配与织网
*   按照术语长度由长到短排序，防止短词拦截长词匹配。
*   利用正则在纯文本文段内，为匹配的术语插入 `[[target|display]]` 链接。
*   在被修改的文件末尾自动拼接 `## 🔗 Cross-References` 结构，列出此卡片的入链 prerequisites。

### 4.3 Glossary.md 生成
以首字母对所有术语进行归类，并列出：
*   词条名称。
*   词条的“快速问答 (What is it?)” 概述。
*   指向文件的 `[[link]]`。

### 4.4 输出格式
返回重建统计指标：
```text
[REBUILD WIKI GRAPH SUCCESS]
Processed Target Directory: /Users/suiyaochen/Desktop/Memory/Suiyao/obsidian-memory/my_memory
Execution Time: 0.45 seconds
Extracted Concepts: 32
Modified Files (Links/MOC/References updated): 5
Total Cross-References Mapped: 23
Global Glossary Generated: glossary.md
```
