# PR · PI-ARCH-IMPLEMENTATION-01 阶段 B（L10–L13）

> 两仓同名分支 `feature/PI-ARCH-L10-L13`，需分别开 PR，**KERT 先合、GITS 后合**
> （GITS 的解读 API 依赖 KERT 的投影产物）。

---

## PR 1 · Leibniz-KERT

**分支**：`feature/PI-ARCH-L10-L13` → `main`
**提交**：6 个（`d0d3df6` → `3b6640b`）
**变更**：41 files, +5078 / −16

### 概述

在受控知识工程仓内建成"演示制度 → 源版本/片段 → 证据/断言 → 冲突/体检/候选卡 → 发布包/三视图投影"的加工链，供 GITS 侧只读消费。

| Loop | 产出 |
|---|---|
| L10 | 3 份 DEMO 演示制度（`.DEMO.md`，与真实制度物理隔离）→ 3 SourceVersion / 51 Fragment |
| L11 | 29 EvidenceSpan + 14 FieldAssertion（11 CANDIDATE / 3 UNKNOWN） |
| L12 | 1 个冲突（内建 50万 vs 100万）+ 七字段体检 + 候选卡（不复用 legacy） |
| L13 | Release `RLS-2026.09.06.1` PUBLISHED + 三视图投影 + 规则包容器 + Owner 决策台账 |

### 关键设计

- **DEMO 三道防冒充闸**：`.DEMO.md` 物理隔离 / front matter `provenance_state: DEMO` / 登记表 §5.8 单列统计
- **真实缺口不抵扣**：DEMO 源不计入权威区基数，真实材料缺口仍 **27/28**，F-L00-07 未解除
- **确定性**：`SOURCE_DATE_EPOCH` 固定下所有产出逐字节可复现
- **fail-closed**：claimType 资格 / 权威级 / Owner 未裁决，三条路径一律不参与或 UNKNOWN
- **AI 边界**：只产 CANDIDATE，`normalizedValue` 全 null；冲突不自动择一

### 自检清单

- [x] `python3 tools/check_registry_consistency.py` → 67/67
- [x] `python3 tools/check_l10_sources.py` → 48/48
- [x] `python3 tools/check_l11_spans.py` → 549/549
- [x] `python3 tools/check_l12_conflicts.py` → 23/23
- [x] `python3 tools/check_l13_release.py` → 24/24
- [x] 红测：篡改 DEMO 标记 / quote / 字节数均被门禁拦截（非零退出）
- [x] `SOURCE_DATE_EPOCH=1788667200` 下产出可复现（diff 为空）
- [x] 13 张 legacy card 未被读取或复用（`legacyCardReused=false`）
- [x] 公开轨 44 条证据全程未参与编译
- [x] 未 `git add .`，全部显式添加

### 遗留（不阻塞合并）

- 真实行内制度 27/28 未上传（F-L00-07，BLOCKED_ON_OWNER）
- 规则包 `status=NOT_BUILT`，内容待产品管理部与风险部签署
- `attestedBy` 为会话级标识 `OWNER`，正式发布前须替换为自然人标识（O-L13-02）

---

## PR 2 · gits-cbanking

**分支**：`feature/PI-ARCH-L10-L13` → `main`
**提交**：7 个（`2ceb66d` → `433a21d`）
**变更**：73 files, +17428 / −84

### 概述

1. **合同**（先行）：DEMO 语义入合同、解读端点登记、修复生成管线阻塞
2. **实现**：产品解读只读 API（CTR-PK-INT-001）
3. **知识架构**：注册 `ASSET-KNOW-PRODUCT-RULES`，`make check` 转绿灯

### 合同变更

| 合同 | 变更 |
|---|---|
| `CTR-PK-EVS-002` | 增 `INV-EVS-09/10/11`（DEMO 源不得支撑 RECOMMENDATION_READY、不得与 VERIFIED 混合） |
| `CTR-PK-RLS-001` | 增 `provenanceState` + `INV-RLS-09` |
| `CTR-PK-ASM-001` | 增 `INV-ASM-09`（SUPPORTED 保留 conflictId 时的裁决一致性） |
| `CTR-PK-INT-001` | 升 3.1.1，补 400 响应与 `BAD_REQUEST` 码 |
| V023 迁移候选 | `provenance_state` 增 `DEMO`；Release 表增 `pk_rls_prov_ck` / `pk_rls_demo_ck` |
| `CONTRACT_INDEX.yaml` | 15 条 CANDIDATE 合同补 `generated` 目标（**解除 F-L10-01**） |
| `contract_pipeline.py` | 支持 `yaml_taxonomy` kind |
| 主 OpenAPI | 登记解读端点（paths 53 → 54）+ 4 个 schema |

### 实现变更

新增包 `com.gien.gits.api.productknowledge`（10 个类）：

- `ProductInterpretationController` —— 只读 GET，404/409/422/503/400 受控失败
- `ProductKnowledgeInterpretationPort` + `KertReleaseSnapshotAdapter` —— 只读消费 KERT 投影
- DTO records + `InterpretationProjection` + 2 个异常类

行为矩阵：未发布 → 404；stale → 409；用途不允许 → 422；KERT 不可达 → 503 `FAILED_CLOSED`（**绝不本地兜底**）；UNKNOWN 字段 `displayValue=null`。

### 自检清单

- [x] `make generate` → PASS
- [x] `make check` → **EXIT=0 全线 PASS**（contract / knowledge-architecture / loop-guard / secret-scan / enum-consistency / semantic-rule-gate）
- [x] `python3 specs/product-knowledge/check_all.py` → 11/11 PASS
- [x] `python3 specs/product-knowledge/check_invariants.py` → 103/103（51 条）
- [x] `./mvnw -q -pl apps/api -am test -DskipITs` → **968 tests / 0 failure / 0 error / 4 skipped**
- [x] 新增测试：`ProductInterpretationControllerTest`（8 项）+ `KertReleaseSnapshotAdapterTest`（5 项）
- [x] 合同变更已登记 `CONTRACT_INDEX.yaml`，哈希一致
- [x] 未手工编辑 `generated/`（全部由 `make generate` 产出）
- [x] 独立 QA 真实 E2E：`REAL_E2E_PASS=YES`（S1–S17 全 PASS，双实例真实 HTTP）
- [x] 未 `git add .`；未混入会话前既有改动
- [x] 无 `any`、无硬编码 URL/密钥；`secret-scan` PASS

### 环境注意（评审/CI 需知）

- **门禁脚本必须用 `/usr/bin/python3`（3.10.12，带 jsonschema 4.26.0）**；
  用 workbuddy python 3.14 跑会得到 4 PASS / 7 FAIL，全部根因是缺 jsonschema
- 后端测试数 968 是跨模块聚合口径；`apps/api` 单模块约 585

### 遗留（不阻塞合并）

- `F-L00-07` 真实行内制度 27/28 未上传 → 演示链路结论为 DEMO 级
- `OQ-C` 未裁决 → `pricing.serviceFee` 恒 UNKNOWN
- `O-L10-02` SourceVersion/Fragment 无 JSON Schema 合同（以 V023 表列为真值）
- `O-L13-03` 已由 `INV-ASM-09` 收敛；是否要求 SUPPORTED 清空 conflictId 留待观察

---

## 合并后验证

```bash
# KERT
cd Leibniz-KERT/examples/product-recommendation-assets
for g in check_registry_consistency check_l10_sources check_l11_spans \
         check_l12_conflicts check_l13_release; do python3 tools/$g.py; done

# GITS
cd gits-cbanking
make check
/usr/bin/python3 specs/product-knowledge/check_all.py

# 端到端冒烟（需先合并 KERT）
./mvnw -q -pl apps/api spring-boot:run -DskipTests \
  -Dspring-boot.run.arguments="--gits.product-knowledge.snapshot-dir=<KERT>/04_serve/interpretation --server.port=8087"
curl "http://localhost:8087/api/v1/product-knowledge/PROD-CM-001/interpretation?view=ELIGIBILITY&purpose=INTERPRETATION"
# 期望 200，minAccountBalance = SUPPORTED / 50 万元 / 证据回链「第十条」
```

## 证据

- Loop 台账：`loops/L10-demo-authoritative-chain/`、`L11-evidence-span-assertion/`
  `L12-conflict-health-candidate/`、`L13-release-interpretation-api/`
- 决策记录：`loops/L13-release-interpretation-api/DECISION-20260906-02.md`
- ADR：`docs/adr/ADR-PK-PRODUCT-RULES-ASSET.md`
- E2E 证据：`evidence/e2e-2026-09-07/`
- 哈希锚点：各 Loop 的 `EVIDENCE_MANIFEST.json`
