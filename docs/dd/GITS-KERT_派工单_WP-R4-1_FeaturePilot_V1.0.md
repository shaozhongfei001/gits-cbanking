# GK-KE 派工单 WP-R4-1 · Feature Pilot 合同源变更 V1.0

> 派工角色：Tech Lead → Feature Pilot
> 日期：2026-09-11
> Loop：GK0-contract-activation（W1 评审退回整改波次）
> 依据：`docs/dd/GITS-KERT_TL_派工单_AR-R4_R5_V1.0.md` 的 B 类任务
> 目标：关闭 F03/F04/F06/F07 的"设计→可校验 Schema"最后一公里缺口

---

## 0. 关键上下文（Feature Pilot 必读，避免改错位置）

### 0.1 权威合同源位置（唯一 SSOT）

| 位置 | 作用 | 是否可改 |
|---|---|---|
| `specs/gk-ke/v1/schemas/*.schema.json` | **权威合同源** | ✅ 本次变更落点 |
| `specs/gk-ke/v1/examples/positive|negative/*.json` | 正负例（对拍验证） | ✅ 需同步新增 |
| `specs/CONTRACT_INDEX.yaml` | 合同注册表（唯一注册入口） | ✅ 新增 Schema 必须登记 |
| `generated/gk-ke/v1/*.schema.json` | 生成制品 | ❌ **禁止手改**（`make generate` 产出） |
| `docs/dd/gk-ke-contract/schemas/*.json` | 评审交付包快照（AR-R0 迁移） | ❌ 本次不动（历史快照） |

**红线**：改 `specs/` → `make generate` → `make check`。禁止直接改 `generated/`。

### 0.2 现有合同登记基线

- `specs/CONTRACT_INDEX.yaml` 已登记 **14 条 CTR-GKKE-001~014**（对应 14 个 schema）。
- `generated/gk-ke/v1/` 已有 14 个生成物。
- 对拍验证器：`scripts/gk_ke_contract_examples.py`（`make check` 会调用），要求每个 schema 有 1 正例 + 至少 2 负例。

### 0.3 CONTRACT_INDEX.yaml 登记格式（新 Schema 必须照此登记）

```yaml
{
  "id": "CTR-GKKE-XXX",
  "kind": "json_schema",
  "authority_source": "specs/gk-ke/v1/schemas/<Name>.schema.json",
  "owner": "gk_ke_contract_owner",
  "compatibility": "explicit_migration",
  "consumers": ["..."],
  "generated": ["generated/gk-ke/v1/<Name>.schema.json"],
  "contract_ref": "C0X",
  "namespace": "gk-ke/v1",
  "status": "CONTRACT_CANDIDATE",
  "simulation_only": true,
  "production_ready": false
}
```

---

## 1. 六个变更任务（逐一执行）

### 任务 1｜MetricDefinition.full.schema.json（F06 G1，最高优先级）

**落点**：`specs/gk-ke/v1/schemas/MetricDefinition.full.schema.json`

**要求**：落地总契约 C04 §2 的 7 组字段，对齐 `docs/dd/gk-ke-contract/contracts/C04_分析语义服务合同.md`：

| 字段组 | 字段 |
|---|---|
| 身份 | metricId、version、中文定义、Owner、approvalRef、definitionHash |
| 对象与粒度 | population、entityType、baseGrain、aggregationGrain、dimensions、allowedJoinPaths、joinCardinality |
| 计算 | numerator/denominator 或 expressionRef、additivity、distinctKey、dedupPolicy、roundingMode、scale |
| 时间 | intervalConvention、businessTimezone、calendarVersion、asOfPolicy、lateArrivalPolicy、accountLifecyclePolicy |
| 金额 | currencyPolicy、unit、fxPolicy、fxSource、fxDateRule、precision |
| 数据 | sourceProductRef、sourceSnapshotPolicy、mappingVersion、completenessRule、nullPolicy、qualityChecks |
| 运行 | queryTemplateRef、parameterSchemaRef、resultSchemaRef、permissionRef、maxRows、timeoutMs、costBudget |

**约束**：
- 保留 `simulationOnly: const true`、`contractVersion: const "gk-ke/v1"`。
- 不发明 C04 正文未定义的字段。
- 原 `MetricDefinition.schema.json`（SIM-only 最小剖面）保留不动，full 版本作为补充。
- 正例 1 个 + 负例 2 个，放入 `specs/gk-ke/v1/examples/`。
- CONTRACT_INDEX.yaml 登记 `CTR-GKKE-015`。

### 任务 2｜negative_cases.json（F06 G2/G3 + F08 H2）

**落点**：`specs/gk-ke/v1/examples/negative_cases.json`（或 `simulation/oracles/negative_cases.json`，与 Feature Pilot 确认后统一）

**要求**：为负例提供 `simulationOnly` + `expectedError` + 隔离声明：

| 负例 | 引用 | expectedError/Modality |
|---|---|---|
| T15 跨币种 | customerId=SIM-C002（含 USD 账户 SIM-A0022） | `CURRENCY_POLICY_REQUIRED` |
| T14 重复账户日 | （坏数据样本） | `GRAIN_VIOLATION` |
| T14 缺日 | （坏数据样本） | `DATA_INCOMPLETE` |
| T12 关联放大 | （坏数据样本） | `GRAIN_VIOLATION` |
| T13 同余额两账户 | （坏数据样本） | 期望 200.00 非 100.00 |
| T02 同名异主体 | claimId=SIM-CLAIM-003 | 不并户 |

**约束**：负例数据必须与正常快照隔离，不得污染 `simulation/tables/` 的正常数据。

### 任务 3｜verify_simulation.py（F08 H1）

**落点**：`tools/verify_simulation.py`

**要求**：独立于 `build_simulation.py`，只读 `simulation/tables/` 复算：
1. 借贷平衡（每交易 DEBIT==CREDIT，2 条分录）
2. 余额滚动（closing=opening+netMovement，次日 opening=前日 closing）
3. 主外键引用闭包（7 类）
4. C001 日均（独立公式，不与 build 共享代码路径）→ 期望 2,983,333.33 CNY
5. C002 跨币种拒绝（检测 USD 账户 + 无转换政策 → 应拒绝）

**约束**：纯标准库（不引入 jsonschema 之外的依赖），退出码 0=通过。

### 任务 4｜四个注册对象 Schema（F04）

**落点**：`specs/gk-ke/v1/schemas/` 新增 4 个 schema：

| Schema | 对应 C02 §2 注册对象 | 关键字段 |
|---|---|---|
| `SourceVersion.schema.json` | SourceRegistry | sourceId、version、originalRef、hash、issuedAt、validFrom/to、sourceClass、allowedUses、permissionRef、simulationOnly |
| `Capability.schema.json` | CapabilityRegistry | capabilityId、version、inputSchemaRef、outputSchemaRef、executorRef、preconditions、sideEffect、permissionRef、budget、timeoutMs、idempotencyPolicy |
| `QueryDefinition.schema.json` | QueryRegistry | queryId、version、parameterSchemaRef、templateRef、resultSchemaRef、sourceProductRef、maxRows、timeoutMs、metricRef |
| `Release.schema.json` | ReleaseRegistry | releaseId、manifest、hash、approvalRefs、qualityRunRef、effectiveFrom、purposeFlags |

**约束**：字段对齐 C02 §2 表格，每 schema 1 正例 + 2 负例，CONTRACT_INDEX.yaml 登记 CTR-GKKE-016~019。

### 任务 5｜ExistingRagAdapter Schema（F07）

**落点**：`specs/gk-ke/v1/schemas/LegacyRagHit.schema.json`

**要求**：对齐 C05 §3 的 `LegacyRagHit` 映射：
- sourceId、sourceVersion、fragmentId、locator、text、score、permissionDecisionRef

**约束**：1 正例 + 2 负例，CONTRACT_INDEX.yaml 登记 CTR-GKKE-020。

### 任务 6｜SemanticPackage 补 writeOwner/writeEntry（F03）

**落点**：修改 `specs/gk-ke/v1/schemas/SemanticPackage.schema.json`（CTR-GKKE-001）

**要求**：`types[]` 补充权威写入口字段，对齐 C01 §2 的"唯一变更责任"：
- `writeOwner`（唯一变更责任方）
- `writeEntry`（唯一写入口，如 API/表/文档记录）
- （可选）`authorityScope`

**约束**：新增字段为可选（`required` 不含），保持向后兼容；同步更新正例 `SemanticPackage.json`。

---

## 2. 执行顺序与验收门禁

```
任务 1（F06 优先，最高风险）
  → 任务 6（F03，改现有 schema，风险最低先做也行）
  → 任务 4（F04 四 Schema）
  → 任务 5（F07 RAG Schema）
  → 任务 2（负例清单，依赖任务 1/4 的 schema 就绪）
  → 任务 3（复算脚本，独立）
```

每个任务完成后：
1. `make generate`（生成 generated/gk-ke/v1/ 新制品）
2. `make check`（含 gk_ke_contract_examples.py 对拍 + secret_scan + enum_consistency + semantic_rule_gate）
3. 记录 `DEV_SELF_CHECK_PASS`（不得自签 QA_PASS）

---

## 3. 红线（违反即退回）

1. 禁止直接改 `generated/`。
2. 禁止发明 C01–C07 合同正文未定义的字段。
3. 禁止删除现有 14 个 schema 或改动其既有语义（变更 6 只新增可选字段）。
4. 禁止把负例数据混入正常快照。
5. 禁止自签 QA_PASS / 独立 QA / Owner 决议。
6. 禁止覆盖 P20/DKES/PI-0 合同。

---

## 4. 交付清单（Feature Pilot 收工时必须提交）

| 交付物 | 说明 |
|---|---|
| 变更 diff | `specs/gk-ke/v1/` + `specs/CONTRACT_INDEX.yaml` 的逐文件 diff |
| make generate 结果 | 生成的新 generated 制品清单 |
| make check 结果 | 完整输出（含 gk_ke_contract_examples.py 的正负例计数） |
| DEV_SELF_CHECK | 每个任务的 self-check 记录 |
| 正负例清单 | 新增的正例/负例文件及对拍结果 |
| 残留项 | 未完成/待定项（如实列出，不得填虚构 PASS） |

---

## 5. 完成后 Baton 交接

Feature Pilot 完成后：
1. 更新 `loops/GK0-contract-activation/STATE.json`（6 任务 done）
2. 更新 `EVIDENCE.json` / `EVIDENCE.md`
3. 更新 `memory/NEXT_SESSION.md`（Baton → 独立 QA）
4. TL 复核后，生成独立 QA 复核提示词（见 TL 后续动作）

---

派工单已落盘。Feature Pilot 按此执行，遇到阻塞写 `loops/GK0-contract-activation/memory/BLOCKED.md`，不擅自决策。
