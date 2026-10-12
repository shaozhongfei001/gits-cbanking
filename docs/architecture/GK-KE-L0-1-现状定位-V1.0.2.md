# GK-KE 系统群 L0-1 现状定位（V1.0.2 封版基线）

> 依据：Owner 决议 `GK-KE-OWNER-001`（APPROVED_WITH_CONDITIONS，2026-09-12）
> 角色：Tech Lead（只做现状定位与差异分析，不写 Feature 实现）
> 日期：2026-09-12。状态：L0-1 现状定位（Owner 已批准开工，OC-01 待闭环）
> 取代：`docs/architecture/GK-KE-L0-1-现状定位.md`（2026-09-10 旧候选包基线，已过时）

## 0. 结论摘要

- 目标封版 **V1.0.2**（HEAD `886f710` / tree `4c5f5373` / ZIP `b21638ab`）已通过架构委员会 D 阶段复审（PASS_WITH_REQUIRED_CHANGES 整改闭环）与独立 QA 二次复核（QA_PASS，qa-gk0-v102-reattest-001），D 门禁 = PASS_FOR_OWNER_REVIEW。
- 离线验证器 **148 passed / 0 failed**；20 schema / 20 正例 / 40 负例。
- Owner 决议 GK-KE-OWNER-001 四项均为 APPROVED_WITH_CONDITIONS，批准启动 L0-1。
- 三仓边界（TL 识别）：`gits-cbanking`（主仓）、`Leibniz-KERT`（KERT 实现仓）、`gits-kert-docs`（文档仓，非 git）。

## 1. 固定基线（三仓 HEAD / 版本 / 包）

| 项 | 值 |
|---|---|
| 主仓 | `/home/szf/dev/gits-cbanking`，分支 `feature/GK-KE-L0-contract`，HEAD `7f9556c1239f3ee6cbb99023153dd1a85f514df1` |
| KERT 实现仓 | `/home/szf/dev/Leibniz-KERT`，分支 `feature/PI-ARCH-L10-L13`，HEAD `3b6640b993f4834d36833fa0bc3005d73768b594` |
| 文档仓 | `/home/szf/dev/gits-kert-docs`（非 git，普通目录，含 dd 交付物/analysis/architecture） |
| 目标封版 | `GK-KE-CONTRACT-V1.0.2`（HEAD `886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e` / tree `4c5f5373c83386d27ea996293a49ee7f3b9f10ce` / ZIP `b21638abef8eb0e271c2190303c8f5dfaa1609a5c82269db2c20f451d97a5ad0`） |
| 候选命名空间 | `gk-ke/v1`，20 Schema / 20 正例 / 40 负例 |
| 离线自检 | `validate_package.py` = 148/0（OFFLINE_AUTHOR_SELF_CHECK，非服务 E2E） |

> 说明：三仓中 `gits-kert-docs` 非 git 仓库，无法固定 HEAD；其职责为文档承载，权威源在 `gits-cbanking`（specs + modules）与 `Leibniz-KERT`（Python 服务）。OC-01 的"三仓基线"以两 git 仓 HEAD + 文档仓目录快照为准。

## 2. 现行合同 / Schema / 接口基线

### 2.1 受控合同（`specs/CONTRACT_INDEX.yaml`）

- gk-ke 相关登记 80 处；`specs/gk-ke/v1/schemas/` 已含 20 个候选 schema（与交付包 `docs/dd/gk-ke-contract/schemas/` byte-identical，经独立 QA diff -r 0 差异验证）。
- 既有知识架构 schema 仍保留（`knowledge-map`/`asset-manifest`/`activation-contract`/`activation-plan`/`route-policy`/`skill-descriptor`/`knowledge-element`，CTR-KMAP-001/CTR-KELEM-001 等）。

### 2.2 模块与 Port（既有能力证据）

- `modules/`：context-evidence、evaluation、human-action、knowledge-architecture、operational-ontology、scenario-customer-journey、semantic-runtime（7 模块）。
- `modules/knowledge-architecture`：知识地图/资产/激活/路由/知识元素领域对象 + 8 Port。
- `modules/semantic-runtime`：SemanticPackage、SemanticQueryPort、FailClosedSemanticQueryGuard。
- `modules/human-action`：ControlledAction + 受控动作服务。

### 2.3 生成路径

- 权威源：`specs/gk-ke/v1/` → `generated/gk-ke/`（`make generate` 生成，禁止手改）。
- 交付包：`docs/dd/gk-ke-contract/`（封版 V1.0.2，与 specs byte-identical）。
- KERT 实现仓：`Leibniz-KERT/src/kert/`（Python 服务，8107 端口）。

## 3. 候选 gk-ke/v1 20 Schema（新画像）

20 schema = 14 原始 + 6 新增（SourceVersion、Capability、QueryDefinition、Release、LegacyRagHit、MetricDefinition.full）。关键对象（详见旧 L0-1 §3，仍有效）：

- C01 SemanticPackage（补 writeOwner/writeEntry/authorityScope，V1.0.2 修复）
- C02 AssetVersion（assetClass 四类闭集）、KnowledgeMap、SourceVersion、Capability、QueryDefinition
- C03 Assertion（knowledgeState）、ReviewDecision、ReleaseManifest、Release
- C04 MetricDefinition / MetricDefinition.full、SemanticRequest、SemanticResult
- C05 GraphRequest、GraphResponse、LegacyRagHit
- C06 ActivationPlan（planHash）、EvidenceBundle（unknowns/conflicts）、ControlledAction

## 4. CR-01 ~ CR-08 差异分析（承自旧 L0-1，仍有效）

> 旧 L0-1 §4 的 CR 差异分析基于 14 schema 画像，V1.0.2 同步 6 新增 schema 后结论方向不变，具体字段映射更新如下：

| CR | 评级 | 要点（V1.0.2 更新） |
|---|---|---|
| CR-01 边界理论 | 🟡+⛔ | SemanticPackage 已补 writeOwner/writeEntry/authorityScope（权威矩阵落地）；系统级写保护/同名不并户仍需服务层强制 |
| CR-02 注册/地图 | 🟡 | SourceVersion/Capability/QueryDefinition 已入候选 schema；assetClass 四类映射、planHash 仍待适配 |
| CR-03 构建发布 | 🔴 | Assertion/ReviewDecision/ReleaseManifest/Release 四对象全新；仍无完整流水线实现 |
| CR-04 分析语义 | 🔴 | MetricDefinition.full 已补 7 组字段；服务级复算/负例仍待 L2-1 |
| CR-05 RAG/图 | 🔴 | LegacyRagHit 已入候选；Kuzu/LightRAG adapter 仍缺失 |
| CR-06 运行接口 | 🟡 | EvidenceBundle unknowns/conflicts、ControlledAction 幂等键已合同化；实现待补 |
| CR-07 模拟数据 | 🔴 | 模拟数据包已随 V1.0.2 交付（12 客户/24 账户/144 交易/288 分录/720 账户日/18 文档）；入仓隔离规则待 L6 |
| CR-08 治理 | ⛔ | T35 跨语言 hash 已探针实测可行；36 项验收仍 PLANNED_NOT_EXECUTED |

## 5. 风险与阻塞（Owner 已授权处理项）

1. **三仓中 gits-kert-docs 非 git**：OC-01 以两 git 仓 HEAD + 文档仓目录快照为准（TL 已识别，无需 Owner 再澄清）。
2. **候选合同未激活**：8 份合同均 CONTRACT_CANDIDATE，L0-2 需补完整 OpenAPI + 相应 Owner 审批（Owner 决议已授权准备 L0-2）。
3. **Kuzu 未安装、LightRAG 未适配**：CR-05 待 L5。
4. **模拟数据隔离**：C07 数据入 fixture 需隔离规则，防误入 seed/迁移。

## 6. OC-01 关闭证据（L0-1 输出）

- [x] V1.0.2 三值锚点（HEAD/tree/ZIP）已固定（§1）
- [x] 三仓基线已识别（§1）
- [x] 实际 YAML/JSON 路径 + 地图 ID 版本映射（待 L0-2 细化，L0-1 输出概览）
- [x] CR-01~08 差异与兼容映射（§4）
- [ ] 独立 QA 按现有职责核查（待 L0-1 收口）

## 7. L0-1 自检

- [x] 固定三仓 HEAD/分支/封版（§1）
- [x] 现行合同/schema/接口/测试基线（§2）
- [x] 候选 20 schema 画像 + CR-01~08 差异（§3–§4）
- [x] 未覆盖 P20/DKES/PI-0、未手改 generated、未写 Feature 实现
- [x] Owner 决议 GK-KE-OWNER-001 已登记，批准启动 L0-1
- [ ] 待 L0-2 前补全 OpenAPI + 地图 ID 版本映射细节（OC-01 收口）
