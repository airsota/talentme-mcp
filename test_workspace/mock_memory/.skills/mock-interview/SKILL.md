---
name: mock-interview
description: 结合目标公司面经，在终端中模拟面试交互。
version: 1.0.0
---

# Mock Interview 技能模板

本技能模板需通过 MCP 部署至本地知识库环境中运行。

## 前置环境配置
1. 配置 `LOCAL_KB_PATH` 以读取 `company` 目录下面经数据。

## 核心指令
1. 询问用户希望挑战的目标公司与岗位。
2. 从本地读取对应的真实面经数据。
3. 扮演面试官，一次只抛出一个问题。
4. 根据用户的回答，给予提示或 Follow-up 问题，最后生成打分报告存入 `interviews` 目录。
