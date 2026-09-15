# L13 证据台账

- Loop: `L13-release-interpretation-api` · 计划 `PI-ARCH-IMPLEMENTATION-01` · 阶段 B
- 日期: 2026-09-06 · 状态: `DEV_SELF_CHECK_PASS`

---

## 1. KERT 侧：Release 与三视图投影

```
releaseId=RLS-2026.09.06.1  lifecycle=DRAFT
interpretationReady=False   recommendationReady=False   provenanceState=DEMO
BLOCKED_ON_OWNER: 未获 Owner 签署决策，Release 保持 DRAFT（不冒充已发布）
```

**红线守持**：脚本**不生成**任何 ReviewDecision。
未传入经 Owner 签署的决策文件（`ownerAttested=true` + `attestedBy` + 每项 `decidedByRole ∈ Owner 角色`）
⇒ `lifecycleState=DRAFT`、`publishedAt=null`，并输出 `90_control/BLOCKED_ON_OWNER.json`
与决策模板 `DECISIONS.template.json`。

产物：
- `04_serve/releases/RLS-2026.09.06.1.json`（CTR-PK-RLS-001）
- `04_serve/interpretation/PROD-CM-001.json`（三视图 + 证据回链）
- `90_control/decisions/DECISIONS.template.json`

`bundleHash` 由四 manifest 哈希拼接待验（INV-RLS-07，门禁已校验）。

---

## 2. GITS 侧：解读 API

**合同先行**：端点与 4 个 schema 登记进 `specs/openapi/gits-kno-api.openapi.json`
（paths 53 → **54**）→ `make generate` **PASS** → 实现。

实现（新包 `com.gien.gits.api.productknowledge`）：

| 组件 | 职责 |
|---|---|
| `ProductInterpretationController` | 只读 GET；404/409/422/503 受控失败；局部 `@ExceptionHandler` 不改全局 |
| `ProductKnowledgeInterpretationPort` | 端口接口（GITS 不得持有产品规则写能力） |
| `KertReleaseSnapshotAdapter` | 读 KERT `04_serve/interpretation` 投影；不可达抛 `KnowledgeSourceUnavailableException` |
| DTO records | `InterpretationResponse` / `InterpretedField` / `EvidenceSummary` / `ProductKnowledgeErrorResponse` |

行为矩阵：

| 场景 | 响应 |
|---|---|
| 无投影 / 未 PUBLISHED | 404 `PRODUCT_KNOWLEDGE_NOT_PUBLISHED` |
| Release stale | 409 `RELEASE_STALE` |
| 用途不允许 | 422 `PURPOSE_NOT_ALLOWED` |
| KERT 不可达 | 503 `FAILED_CLOSED`（绝不本地兜底） |
| productId 格式错 | 400 `BAD_REQUEST` |
| 非就绪字段 | `displayValue=null`，`evidenceSummaries=[]` |

测试：`ProductInterpretationControllerTest` **6 项全通过**（含 404/422/503/400 与证据回链）。

---

## 3. 合同增补（O-L10-01 落地）

| 变更 | 原因 |
|---|---|
| `CTR-PK-RLS-001` 增 `provenanceState` + `INV-RLS-09` | 红线要求 demo Release 打 DEMO 标记，原合同无字段承载 |
| V023 增 `provenance_state` / `pk_rls_prov_ck` / `pk_rls_demo_ck` | 数据库层强制 `DEMO ⇒ recommendation_ready=false` |
| `CTR-PK-INT-001` 3.0.3 → 3.1.1 | 生成管线要求 OpenAPI 3.1.1 |
| 15 条合同补 `generated` 目标 | 解除 F-L10-01（generate 直接失败） |
| `contract_pipeline.py` 支持 `yaml_taxonomy` | 分类基线合同此前无法进管线 |

---

## 4. 门禁与回归

```
统一门禁：11/11 PASS（L10 48 / L11 549 / L12 22 / L13 23 …）
后端：tests=961 failures=0 errors=0 skipped=4（基线 955 + 新增 6）
contract-generate：PASS（此前 FAIL）
make check：contract-check PASS → 失败点推进至 knowledge-architecture-check（见 F-L13-01，既有）
```

---

## 5. 本 Loop 不证明什么

- 不证明 Release 可发布 —— **DRAFT**，等 Owner 签署
- 不证明解读 API 能返回 200 —— 当前链路正确返回 **404**（未发布），这是 fail-closed 而非缺陷
- 不证明真实 E2E 通过 —— `REAL_E2E_PASS=NO`
- 未执行 git 提交
