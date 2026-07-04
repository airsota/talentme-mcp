# TalentMe 开发主清单 (Development Master List)

基于您在 `self/memory_research/` 中的底层调研（`FEATURE-MAP.md`, `TALENTME-UX-FLOW.md`, `UX_FEATURES.md`, `ROADMAP.md`），昨天我们已经完成了面向创作者的云端生产工具链（Cloud-Dev-Tools）以及最核心的第一个 MCP Tool：**`search`（双源检索）**。

接下来，我们需要开发面向终端用户的**消费端工具链**。以下是根据调研文档为您深度对比整理的**待开发全景映射表**。

---

## 1. MCP Tools (后端基础能力)
MCP Tools 是底层代码驱动的接口，负责连接云端 API、操作本地 SQLite 数据库（`memory.db`）以及做确定性的增量计算。

| 优先级 | Tool 名称 | 核心功能 | 支撑的 UX Feature |
|--------|------------|----------|-------------------|
| **已完成** | **`search`** | 本地与云端双源检索。 | 全局基石 |
| **已完成** | **`guide`** | 读取 `memory.db` 返回当前的 Hot Context（盲区/进度）。 | Daily Digest (F22) |
| **已完成** | **`learn`** | 拉取云端知识，按角色编译，注入 Frontmatter，写入本地。 | 风格适配 (F2), 追问预览 (F18) |
| **已完成** | **`assess`** | 拉取云端问卷，初始化用户的 Mastery 种子数据。 | 新用户 Assessment (F1) |
| **已完成** | **`review`** | 读取遗忘曲线数据，返回最需要复习的知识点。 | 日常学习循环 |
| **已完成** | **`status`** | 聚合 Mastery 数据，返回雷达图、热力图数据结构。 | 掌握度可视化, Readiness Score (F19), Peer Comparison (F9) |
| **已完成** | **`lint`** | 盲区检测（云端对比本地）、过期追踪、悬空链接检查。 | 健康检查 |
| **已完成** | **`edit`** | 修改本地 Wiki 页面的内容。 | 基础维护 |
| **已完成** | **`interview`** | 面试时间线 CRUD 操作，记录各轮次状态。 | 面试时间线 (F5) |
| **已完成** | **`import-feedback`**| 解析专家的结构化评分（JSON），用来精准校准本地 Mastery。 | 专家反馈导入 (F12) |
| **已完成** | **`log-progress`**| 底层核心写入器，记录所有学习与评测的 Mastery 熟练度落盘。 | 状态流转枢纽 |
| **已完成** | **`calendar-sync`**| 对接日历 API 或系统定时器，实现面试日程的主动唤醒提醒。 | 日程驱动 (F10) |
| **已完成** | **`report-issue`** | 一键将本地纠错或脱敏后的优质面经分享上报回云端。 | 社区数据飞轮 (Crowdsourcing) |

---

## 2. Agent Skills (Agent 智能指令)
Skills 是一组纯文本的指令文件，用于教导 Agent 如何在正确的时机调用上述 MCP Tools，并利用 LLM 自身的判断力处理复杂的业务逻辑（如判断合并、发现矛盾、生成计划）。

| 分类 | Skill 名称 | 核心能力 (Agent 判断逻辑) | 支撑的 UX Feature |
|------|-------------|----------------------------|-------------------|
| **已完成** | `tm-guide` | 教 Agent 何时调用 search vs learn vs review。 | 引导与路由 |
| **已完成** | `tm-review` | 接管 review 返回的薄弱点，执行苏格拉底式的间隔重复抽查。 | 间隔重复复习 |
| **已完成** | `tm-cross-linker` | 发现新页面中未链接的 mention，智能补全 Wikilink。 | 引用图谱维护 |
| **已完成** | `tm-provenance` | 写入知识时，判断并标记来源（云端提取 / 个人经验）。 | 数据溯源 |
| **已完成** | `tm-contradiction`| 对比新旧知识，发现矛盾时提醒用户。 | 质量控制 |
| **已完成** | `tm-merge` | 导入外部资料时，判断是新建、扩展还是合并。 | 知识导入 (F24) |
| **已完成** | `tm-tag-taxonomy` | 维持标签一致性（例如防止出现复数、缩写等混乱）。 | 标签管理 |
| **已完成** | `tm-assess` | 执行 Assessment 流程，与用户交互出题。 | 新用户 Assessment (F1) |
| **已完成** | `tm-mock` | 全真模拟面试教练，严格控制追问压力，绝不直接给答案。 | Mock 面试 (F6) |
| **已完成** | `tm-plan` | 基于 Assessment 和目标，生成个性化的 `study-plan.md`。 | 复习计划生成 (F3) |
| **已完成** | `tm-prep` | 面试前生成预测题目与知识盲区清单 (`PREP.md`)。 | PREP 面试准备 (F4) |
| **已完成** | `tm-debrief` | 面试后引导复盘，更新 Mastery (`debrief.md`)。 | DEBRIEF 轮次复盘 (F4) |
| **已完成** | `tm-summary` | 面试结束后提炼经验，回流至知识库 (`SUMMARY.md`)。 | 面试总结 (F4) |
| **已完成** | `tm-question` | 面试后/刷帖时录入新面经题，匹配云端并关联知识点。 | 面经整理工具 (F25) |
| **已完成** | `tm-brief-for-expert`| 从本地数据脱敏生成发给专家的 Mock 准备文档。 | Mock 前 Brief (F11) |
| **已完成** | `tm-coaching-capture`| 捕获职业咨询（Coaching）中的决策，修改复习计划和目标。 | 决策捕获 (F14) |
| **已完成** | `tm-import-review`| 接收专家批改过的模板文档，智能合并到本地。 | 简历/答案 Review (F16) |
| **已完成** | `tm-articulate` | 教练模式：强迫用户按 STAR 等框架输出，纠正表达。 | 表达结构化教练 (F17) |
| **已完成** | `tm-session-save` | 自动判断聊天记录中值得保留的知识并存为笔记。 | 对话沉淀 |
| **已完成** | `tm-history-learn`| 跨项目扫描 Agent 聊天历史提取面经和知识。 | 历史挖掘 |
| **已完成** | `tm-insight` | 扫描本地面经库，利用 LLM 聚类发现近期高频考点模式。 | Pattern Detection (F7) |
| **已完成** | `tm-resume` | 依据 Mastery 数据自动重写简历 Markdown，并联动 LaTeX 编译。 | 简历动态优化 (F16) |
| **已完成** | `tm-offer` | 协助量化对比 Offer，扮演冷酷 HR 进行薪资谈判 Role-play。 | 谈判决策教练 (F20) |

---

## 3. UX Feature 与底层实现的映射归纳
从用户的视角出发，上述所有的工具和技能将交织成以下的 TalentMe 产品特性。

1. **零基础冷启动循环**
   - **Empty State 智能路由**: 系统发现用户为“白板”时，各组件不报错，而是主动切换话术引导向导。
   - 用户运行 Setup。
   - `tm-assess` (Skill) 调起 `assess` (MCP Tool) 获取问卷并计算初始水平。
   - `tm-plan` (Skill) 自动生成 `study-plan.md`。
2. **日常无感沉淀体验 (The Aha Moment)**
   - 每日打开，`guide` (MCP) 的 Hot Context 支持 **Daily Digest (F22)**。
   - 用户提问，触发 **Search -> Learn -> Merge/Link** 自动化流水线。
   - 其中 `learn` (MCP) 的不同参数支撑 **风格适配 (F2)**，并返回 **追问角度预览 (F18)**。
3. **面试实战全家桶**
   - 面试推进时，使用 `interview` (MCP) 记录 **时间线 (F5)**。
   - 依赖 `tm-prep`, `tm-debrief`, `tm-summary` 生成结构化文档 **(F4)**。
   - 收集到的新题目利用 `tm-question` 进入 **面经库 (F25)**。
4. **高端变现：专家护城河**
   - 本地知识太虚？一键使用 `tm-brief-for-expert` 生成 Brief 给专家 **(F11)**。
   - 专家点评后，调用 `import-feedback` (MCP) 将专家打分转化为本地绝对的熟练度数值 **(F12)**，并用 `tm-coaching-capture` (Skill) 修改接下来的路。
5. **社交与动力**
   - 基于 `status` (MCP) 的 Mastery 数据，在云端支持 **Peer Comparison (F9)**，提供 **Readiness Score 面试就绪度评估 (F19)**。
