---
name: wiki-ingest
description: 将各类散乱的文章、PDF 或网页提取为标准的本地知识库 Markdown 节点。
version: 1.0.0
---

# Wiki Ingest 技能模板

本技能模板需通过 MCP 部署至本地知识库环境中运行。

## 前置环境配置
1. 安装 MCP 客户端。
2. 配置环境变量 `LOCAL_KB_PATH` 指向您的本地知识库根目录。

## 核心指令
当收到原始资料时，执行以下步骤：
1. 总结内容，提取核心结论。
2. 生成结构化的 Markdown，存入 `LOCAL_KB_PATH/tech-fundamentals/` 下合适的子目录。
3. 查找是否有关联的已有笔记，添加 `[[wikilinks]]`。
