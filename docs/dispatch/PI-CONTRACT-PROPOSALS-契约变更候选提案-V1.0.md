# PI 契约变更候选提案 V1.0（待合同 Owner 签批）

```text
提交人：tech_lead（TL）｜ 提交时间：2026-09-22
性质：**候选提案**——未经合同 Owner 签字不得改 specs/、不得改生成的合同产物、不得对外承诺字段可用。
依据：R2 `05_合同端点与版本快照映射.md`；Owner 2026-09-22 已批 O-3 方向（见 PI-O-裁决登记）
签批路径：合同 Owner 批准 → TL 改 specs/ 源 → `make generate` → `make check` → 再实现
```

## 提案 1｜解读响应新增 DEMO/来源字段（`CTR-PK-INT-001`）

| 项 | 内容 |
|---|---|
| 合同 | `CTR-PK-INT-001`（authority_source `specs/product-knowledge/interpretation-api.openapi.json`），**Owner = `knowledge_architecture_owner`**，现状态 `CANDIDATE` |
| 问题 | 实测解读响应字段为 `productId, releaseId, bundleHash, view, purpose, isStale, fields, generatedAt` ⇒ **无 `provenanceState`/`isDemo`**，页面无法显示 DEMO 徽标（R1-05 `P-3`） |
| 提案 | 响应新增可选字段：`provenanceState`（枚举，如 `DEMO`/`SIM`/`PROD`）、`environment`（`DEMO`/`UAT`/`PROD`）、`isDemo`（boolean） |
| 兼容策略 | 只增不删、**可选**、不放开 `additionalProperties`；既有 P38 消费者不受影响；主版本 `v1` 不变（记 `v1.1`） |
| 验证用例 | ① `PROD-CM-001` 返回 `provenanceState=DEMO`；② 字段缺失时前端**必须**显示"未标识来源"而非默认"真实"；③ 契约消费测试（`scripts/pkc_contract_tests.py`）新增该字段断言 + 变异复验 |
| 影响面 | KERT 投影生成侧需写入 `provenanceState`；GITS 侧 1 处 DTO + 1 处页面徽标 |
| 签批 | ☐ 合同 Owner 日期：______ |

## 提案 2｜版本与证据快照字段（`CTR-PK-INT-001` + 新版出口 `CTR-PKC-API-001`）

| 项 | 内容 |
|---|---|
| 合同 | `CTR-PK-INT-001`（Owner `knowledge_architecture_owner`）；新版出口 `CTR-PKC-API-001`（Owner `integration_contract_owner`） |
| 问题 | 下游引用需固定 `published_version_id` + `evidence_snapshot_id`（需求包为 `READY_FOR_OWNER_REVIEW` 候选，**不得**直接升级为强制规则）；且**任何现有哈希未经定义不得充当证据快照 ID** |
| 提案 | ① `published_version_id`：值 = Release ID（如 `RLS-2026.09.06.1`），由解读响应与新版出口显式暴露；② `evidence_snapshot_id`：值 = `EVSNAP-<releaseId>-<evidenceManifestHash 前 12>`，由 **KERT 侧发布时生成**并写入 Release 与投影；③ 保留 `bundleHash`/`assertionManifestHash`/`rulePackageHash` 原语义，**均不得**改名为快照 ID |
| 版本切换/过期 | 下游引用固定版本 → `lifecycleState ≠ PUBLISHED` 或 `staleFlag=true` ⇒ **409 `VERSION_EXPIRED`**；版本不存在 ⇒ **404 `NO_PUBLISHED_VERSION`**；**禁止**静默回落最新版 |
| 兼容策略 | 只增不删、可选字段；灰度双写（Release 侧生成 + 投影/出口暴露）；不改变既有字段语义 |
| 验证用例 | ① 正常引用两字段；② 版本切换后旧引用 409；③ 过期版本 409；④ 证据缺失 → 字段为空或"待核验"，不得伪造；⑤ `purpose=RECOMMENDATION` 仍 422 |
| 影响面 | KERT 发布流程（生成 `EVSNAP`）；GITS 新版出口 2 字段；下游服务（推荐/建议书）引用改造属**后续独立范围** |
| 签批 | ☐ 合同 Owner 日期：______ |

## 提案 3｜通用合同路径前缀订正（`CTR-API-001`）

| 项 | 内容 |
|---|---|
| 合同 | `CTR-API-001`（`specs/openapi/gits-kno-api.openapi.json`），**Owner = `integration_contract_owner`** |
| 问题 | `servers.url = '/api/v1'`，而 product-knowledge 三条路径写作 `/api/v1/product-knowledge/...` ⇒ **前缀重复**（新发现，R2 `01` §3、R2 `05` §1） |
| 提案 | 三条路径改为相对 `servers` base 的写法：`/product-knowledge/cards`、`/product-knowledge/cards/{productId}`、`/product-knowledge/{productId}/interpretation`（**或**保留现状但把 `servers.url` 置为 `/`，二者择一，由合同 Owner 定） |
| 兼容策略 | 仅文档层订正，**运行时路径不变**（实现路径为 `/api/v1/...`）；对外调用方无影响；需同步 `generated/` |
| 验证用例 | `make generate` + `make check` PASS；`generated/openapi/gits-kno-api.normalized.json` 中路径与 base 组合后与运行时一致 |
| 风险 | 若其它合同按"路径含前缀"的旧口径消费该文件，需合同 Owner 评估下游影响 |
| 签批 | ☐ 合同 Owner 日期：______ |

## 关于路径前缀订正的纪律

实现方（TL/Feature Pilot）**不得**静默修改 `specs/openapi/gits-kno-api.openapi.json`。
若合同 Owner 选择暂不订正，本项**登记为技术债**并在下一版合同一并处理，**不得**因此改变运行时行为。
