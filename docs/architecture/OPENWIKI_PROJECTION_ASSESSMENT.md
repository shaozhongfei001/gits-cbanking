# OpenWiki 知识投影评估报告

> **⚠️ 2026-08-23 架构审查标注**：本文档中引用的 `adapters/knowledge-filesystem/`（含 `InMemoryKnowledgeStore`、`KnowledgeSnapshotLoader`、`FailClosedJsonReader` 等）已在 P24 DKWS 重构中移除。当前知识读取由 `scenario/dkws-platform/` 模拟平台提供 stub 实现。下文中涉及 `knowledge-filesystem` 的代码路径和类名仅作历史参考。

```text
DOC_ID=OPENWIKI-PROJECTION-ASSESSMENT-001
STATUS=OWNER_ADOPTED_DEFER
AUTHOR=tech_lead
CREATED_AT=2026-08-19
OWNER_DECISION_DATE=2026-08-19
OWNER_DECISION=ADOPT_DEFER_UNTIL_PRODUCTION_READY
RELATED=ADR-0017（OpenWiki知识投影边界，PROPOSED_FOR_P20_OWNER_REVIEW）
BASIS=P20 wiki-ontology fusion shadow 验证结果（qa_pass, 6/6 gate）
```

> **Owner 决策（2026-08-19）**：采纳"暂缓（DEFER_UNTIL_PRODUCTION_READY）"建议。OpenWiki 暂不引入，保持 ADR-0017 边界为强制设计约束；待 P20 转生产就绪或出现明确业务需求时再评估。ADR-0017 状态维持 `PROPOSED_FOR_P20_OWNER_REVIEW`（暂不推进）。

> 本文档评估 P20 之后是否应引入真实 OpenWiki 作为知识地图投影/阅读入口，以及边界与实施路径。供 Owner 决策，不替代 Owner 批准。

---

## 1. 背景与现状

### 1.1 P20 已验证的能力（Git 文件系统过渡方案）

P20 用 `adapters/knowledge-filesystem/`（纯文件系统读取器）验证了知识架构控制面，全部通过（`qa_pass`）：

| 能力 | 实现 | 验证 |
|---|---|---|
| Knowledge Map 读取 | `FilesystemKnowledgeMapReader` | ✅ hash-attested |
| Asset Manifest 目录 | `FilesystemAssetCatalogReader` | ✅ |
| Route Policy 读取 | `FilesystemRoutePolicyReader` | ✅ |
| Activation Contract 读取 | `FilesystemActivationContractReader` | ✅ |
| 前导元数据 | `JsonFrontmatterExtractor` + `FailClosedJsonReader` | ✅ 27/27 测试 |
| 路径安全 | `PathSafety`（越界/符号链接拒绝） | ✅ |

**结论**：知识地图、资产清单、路由、激活合同已能通过文件系统可靠读取，双路径融合为 ActivationPlan 且可重放。

### 1.2 OpenWiki 的定位（ADR-0017 边界）

ADR-0017 将 OpenWiki 定义为**可替换的外部投影和阅读入口**，明确 OpenWiki **不得**：
- 保存原始 KYC / 交易明细；
- 成为运营对象权威状态库；
- 直接决定权限；
- 直接执行任意工具；
- 将页面链接图等同于业务知识图谱；
- 绕过 Activation Contract 调用资产。

---

## 2. 引入 OpenWiki 的权衡

### 2.1 引入的理由（Pro）

| 理由 | 说明 |
|---|---|
| 人机共读体验 | OpenWiki 提供人类可浏览的 Markdown 知识地图，RM/架构师可直接阅读与检索 |
| 知识编辑与协作 | 比 Git 文件更适合业务侧审阅、评论、版本讨论（若启用编辑权限） |
| 团队熟悉度 | 已有团队使用 Wiki 类工具，降低知识消费门槛 |
| 投影可替换性 | ADR-0017 保证换 Wiki 不影响 ActivationPlan / Skill / Agent 运行时 |

### 2.2 不引入的理由（Con）

| 理由 | 说明 |
|---|---|
| **非权威源风险** | OpenWiki 一旦被误作权威，会造成与 `specs/` 语义合同源漂移 |
| **权限边界** | OpenWiki 天然缺乏细粒度权限（字段级）；若承载敏感知识需额外工程 |
| **同步/双写成本** | 权威源 → 编译发布 → OpenWiki 投影需维护 CI 管线与一致性校验 |
| **非必需** | P20 已验证控制面不依赖 OpenWiki；引入是体验增强，非功能必需 |
| **影子阶段约束** | P20 为 shadow_only，`production_ready=no`，OpenWiki 属生产侧投影，超出当前阶段 |

### 2.3 关键判断

OpenWiki 的价值在于**投影与阅读**，不在控制面。当前阶段（shadow → 生产准备前），**不引入 OpenWiki 不阻塞任何已验证的架构能力**；引入只带来阅读体验提升，同时增加权威源与投影的同步治理成本。

---

## 3. 决策建议

### 建议：**有条件暂缓（DEFER_UNTIL_PRODUCTION_READY）**

```
建议状态=DEFER
建议理由=OpenWiki 是生产侧投影体验增强，非 P20 架构必需；当前阶段引入会引入双写/同步/权限治理成本，且 P20 production_ready=no。
前置条件（满足其一再评估）：
  A. P20 正式转 production_ready（Owner 授权 FUSION/cutover 后）
  B. 出现明确的业务侧知识编辑/浏览需求，且 Owner 愿意承担投影同步治理
```

**但保留 ADR-0017 的边界约束为强制性设计原则**：无论是否引入 OpenWiki，都必须维持"权威源 → 编译发布 → 投影"单向流，OpenWiki 永不成为权威源/权限引擎/本体运行时。

### 决策路径（供 Owner 选择）

| 选项 | 动作 | 成本 | 收益 |
|---|---|---|---|
| **A. 暂缓（推荐）** | 保持 ADR-0017 为 PROPOSED；不引入 OpenWiki；继续用 Git 文件系统投影 | 低 | 避免双写/权限治理；聚焦生产就绪 |
| **B. 原型验证** | 建一个 OpenWiki 原型 loop（只读投影），验证 CI 发布 + 一致性校验 + 权限隔离 | 中 | 提前验证投影管线可行性，积累证据 |
| **C. 直接引入** | Owner 批准 ADR-0017 + 建正式 loop 落地 OpenWiki 投影 | 高 | 立即获得阅读/协作体验 |

---

## 4. 若引入（选项 B/C）的实施路径

若 Owner 选择原型验证或直接引入，建议遵循：

1. **合同先行**：新增 `projection` 相关合同（如 `CTR-PROJECTION-*`），OpenWiki 页面结构与权威 `specs/` 地图映射需登记到 `CONTRACT_INDEX.yaml`。
2. **单向发布管线**：`specs/` 权威源 → `make generate` 校验哈希 → 编译发布到 OpenWiki，禁止反向回写。
3. **只读投影**：OpenWiki 仅承载知识地图/资产/SOP 的可浏览投影，不含 KYC/交易明细。
4. **权限隔离**：投影内容按 `knowledge-architecture` 的权限标签过滤，未决权限不发布。
5. **独立 QA**：投影一致性校验（页面 ↔ 权威源哈希）纳入 gate，由独立 QA 验证。

---

## 5. 结论

- **P20 已验证**：Git 文件系统投影足以支撑知识架构控制面，功能闭环完整（qa_pass）。
- **OpenWiki 引入**：属于生产侧体验增强，**非当前阶段必需**，且会引入同步/权限治理成本。
- **建议**：**暂缓（DEFER_UNTIL_PRODUCTION_READY）**，保留 ADR-0017 边界为强制设计约束；待 P20 转生产就绪或出现明确业务需求时，再评估原型验证或引入。

---

## 变更记录

| 版本 | 时间 | 说明 |
|---|---|---|
| v1 | 2026-08-19 | 初始评估，基于 P20 shadow 验证结果 |
