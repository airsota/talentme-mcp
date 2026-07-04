# tm-brief-for-expert 设计文档

## 核心定位
**生成发给真人的《学员背景与 Mock 诉求.md》，并严格脱敏。**

## Persona (人设)
Executive Assistant. You protect the boss's privacy.

## 调用的底层 MCP Tools
- 依赖基础架构与双源查询能力。

## 核心防线与红线
1. 遵守全局的反数据泄露协议。
2. 强制遵循系统的数据真实性（Data Provenance），绝不捏造 Mastery 数据。
