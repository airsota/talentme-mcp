# Edit Tool 设计文档

**Tool 名称**: `update_wiki_page`  
**类型**: MCP Tool  

---

## 1. 核心目标
安全地在用户本地已有的 Markdown 文件尾部追加（append）或覆盖（overwrite）写入内容。

---

## 2. 哲学理念
*   **路径穿透防范（CWE-22）**：在对任何文件写入前，执行 canonical 规范化路径比对，确保目标文件位置严格属于 `memory_path` 子目录，防范大模型写入恶意路径。
*   **原子写入边界**：本工具仅限对**已存在**的文件进行修改，新建文件请调用 `create_wiki_page`。

---

## 3. 接口规范

```python
def update_wiki_page(page_name: str, mode: str, new_content: str) -> str:
    """
    Modify an existing local wiki page by appending or overwriting.
    
    Args:
        page_name: 文件名（带或不带 .md 后缀）。
        mode: 写入模式，'append' (追加内容) 或 'overwrite' (全文本覆盖)。
        new_content: 待写入的 Markdown 文本内容。
    """
```

---

## 4. 执行逻辑

### 4.1 安全路径匹配
*   在 `memory_path` 中全局递归检索是否存在对应的 `page_name` 文件。
*   匹配成功后，通过 `os.path.realpath` 强比对物理路径安全界限。

### 4.2 文件写入操作
*   `append` 模式：使用 `a` 附加写模式打开文件，自动换行并追加内容。
*   `overwrite` 模式：使用 `w` 覆盖写模式打开文件并覆写。

### 4.3 输出格式
返回执行结果：
`Successfully appended page: Transformer.md.`
