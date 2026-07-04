# Report Issue Tool Design Document

**Phase**: 2 (P2 Tools)
**Type**: MCP Tool

## 1. 核心目标
支持（Crowdsourcing 飞轮），允许用户发现本地考点/云端数据的错误时，一键提报到主库。

## 2. 接口规范
```python
def report_issue(topic: str, issue_description: str) -> str:
    """Send an issue report directly to the Cloud API."""
```

## 3. 核心逻辑
- **API 通信**：利用启动时配置的 `api_url`，通过 `requests` 库向 `https://{api_url}/api/v1/report_issue` 发送包含 `email`, `topic`, `issue_description` 的真实 POST 负载。
- **云端联动**：彻底打通真实的数据物理闭环，而非停留在本地打假桩。
- **Prompt Injection**：无论网络成功或失败，返回友好的告知。若成功，指示 Agent 发送感激的话语：“感谢您的极客精神，您的纠错已经提交给 TalentMe 核心维护组”。
