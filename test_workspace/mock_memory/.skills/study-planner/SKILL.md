---
name: study-planner
description: 对比本地知识库与云端技能树，生成 14 天冲刺计划。
version: 1.0.0
---

# Study Planner 技能模板

本技能模板需通过 MCP 部署至本地知识库环境中运行。

## 前置环境配置
1. 配置 `LOCAL_KB_PATH` 读取现有的知识分布。

## 核心指令
1. 调用 TalentMe 云端接口，获取目标岗位的技能树。
2. 扫描本地 `tech-fundamentals` 和 `projects` 目录，对比出用户欠缺的技能盲区。
3. 生成一个针对性极强的 14 天冲刺学习 Markdown 表格。
