# L11 证据台账

- Loop: `L11-evidence-span-assertion`
- 计划: `PI-ARCH-IMPLEMENTATION-01` · 阶段 B
- 角色: CodeBuddy Tech Lead（W1 合同 / W2-W3 管道 / W4 门禁 / W5 证据）
- 日期: 2026-09-06
- 授权: Owner 决议 **DECISION-20260906-01**
- 上游: L10（3 SourceVersion / 51 Fragment）
- 状态: `DEV_SELF_CHECK_PASS`（dev 侧最高）

---

## 1. 产出概览

```
run=RUN-20260906-9d34c845 · evidenceSpans=29 · assertions=14
  SRC-CM-001  12 spans      PROD-CM-001  11 CANDIDATE + 3 UNKNOWN
  SRC-CM-002   7 spans
  SRC-CM-003  10 spans
```

确定性：`SOURCE_DATE_EPOCH=1788667200` 下两次运行 **5 个产出文件逐字节一致**。

---

## 2. W2 · EvidenceSpan 抽取

来源：`02_work/fragments/*.fragments.json`（51 Fragment）→ 逐条判定。

| 规则 | 实现 | 对应不变式 |
|---|---|---|
| `usage` | 源在 `_authoritative/` ⇒ `AUTHORITATIVE` | INV-EVS-04 |
| `claimType` | 关键词表判定，**且必须 ∈ 源 `allowedClaimTypes`**，否则该条款不产出证据 | INV-EVS-05 |
| `evidenceId` | `EVS-{sid去横线}-{SHA-256(quote)[:8]}` | INV-EVS-08 |
| `quoteHash` | `SHA-256(quote)` | INV-EVS-01 |
| `locator` | `{kind: CLAUSE, clause: "第X条", clauseVerified: false}` | INV-EVS-07 |
| `applicabilityScope` | `effectiveFrom` 取自源 front matter `effective_date` | — |

**51 → 29 的筛减不是丢失，而是 INV-EVS-05 资格过滤**：未命中源允许 claimType 的条款不产出证据。
`clauseVerified=false` —— 演示条款号未经 Owner 核定，故按 INV-EVS-07 不得支撑 `RECOMMENDATION_READY`。

claimType 分布：`ELIGIBILITY 11 · PROCESS 8 · RISK 5 · PRICE 3 · REGULATORY 2`。

---

## 3. W3 · FieldAssertion 编译（七字段）

字段策略来源：`CTR-PK-FLD-001` 的 CASH_MANAGEMENT 正例（`ownerApproved=false`）。
产品主体：`PROD-CM-001`（取自 `specs/product-knowledge/product-taxonomy.yaml` 第 294 行，
**非** 13 张 legacy card 文件），`productVersionScope=version=2026.09.06.1`。

| fieldPath | 断言数 | 状态 | 说明 |
|---|---|---|---|
| `identity.productCode` | 1 | UNKNOWN | 证据 claimType 判为 ELIGIBILITY，字段要求 PROCESS → **资格不符，不参与** |
| `eligibility.customerSegment` | 3 | CANDIDATE | 三源各一条 |
| `eligibility.minAccountBalance` | 4 | CANDIDATE | **含内建冲突**（50 万 vs 100 万），留给 L12 |
| `eligibility.prerequisiteProducts` | 1 | CANDIDATE | — |
| `compliance.regulatoryBasis` | 1 | UNKNOWN | 字段要求 `REGULATORY`，证据为 `INTERNAL_POLICY` → **权威级不足**（INV-FLD-02） |
| `pricing.serviceFee` | 1 | UNKNOWN | `ownerDecisionRequired=true` 且策略 `ownerApproved=false`（OQ-C 未裁决）→ fail-closed |
| `process.openingChannel` | 3 | CANDIDATE | — |

**三条 fail-closed 路径**（均未编造值）：

1. **claimType 资格** —— 字段 `allowedClaimTypes` 不含证据 claimType → 不参与
2. **权威级不足** —— `AUTHORITY_RANK[证据] > AUTHORITY_RANK[要求]` → 不参与
3. **Owner 未裁决** —— `ownerDecisionRequired && !ownerApproved` → 强制 UNKNOWN

**AI 边界**：本 Loop 只产 `CANDIDATE` 与 `UNKNOWN`，`normalizedValue` **全部为 null**
（INV-ASM-07）。冲突**不合并、不择一** —— `minAccountBalance` 的 4 条断言并存，由 L12 检测。

---

## 4. W4 · 门禁

`tools/check_l11_spans.py` **528/528 PASS**，校验项：

- jsonschema Draft 2020-12 对 `CTR-PK-EVS-002` / `CTR-PK-ASM-001` 全量校验
- `quoteHash == SHA-256(quote)`、`evidenceId` 后缀一致
- **每条 quote 可在指定 Fragment 内原样定位**（INV-EVS-02 前置）
- `claimType ∈ 源 allowedClaimTypes`、`usage=AUTHORITATIVE`、`sourcePath` 落在权威区
- `locator.clause` 与 Fragment 条款一致
- UNKNOWN ⇒ 值为 null 且 `evidenceIds=[]`（INV-ASM-02）
- 权威级与 claimType 满足字段策略（INV-FLD-02）
- DEMO 派生断言不得为 `SUPPORTED`/`REVIEWED`
- 七字段 100% 有断言

**红测**：

```
注入：quote 前插入"演示篡改"
  FAIL | EVS-SRCCM001-dbe96c76 quoteHash == SHA-256(quote)
  FAIL | EVS-SRCCM001-dbe96c76 quote 可在 Fragment 内原样定位
  → 526/528，退出码 1
还原：528/528，退出码 0
```

> 首次红测因注入写法幂等（替换末字为同一字符）而未改变内容，门禁"通过"属**红测本身失效**而非门禁通过。
> 已重做并确认拦截。此过程记入 FAILURES F-L11-01。

---

## 5. 统一门禁与后端回归

```
python3 specs/product-knowledge/check_all.py   → 9/9 PASS · 929 项（L10 基线 8/8 · 401）
./mvnw -q -pl apps/api -am test -DskipITs      → tests=955 failures=0 errors=0 skipped=4
                                                  与 L00/L03/L10 基线一致：NO_REGRESSION
```

统计口径同 L10：以 surefire **XML** 汇总为 955（txt 摘要行口径为 864，属差异非缺失）。

---

## 6. 本 Loop 不证明什么

- 不证明任何断言已核实 —— 全部 `CANDIDATE`，`normalizedValue` 全 null
- 不证明冲突已解决 —— `minAccountBalance` 冲突**故意保留**给 L12
- 不证明产品卡可用 —— 未产生候选卡（L12），未产生 Release（L13）
- 不证明 `pricing.serviceFee` 可展示 —— OQ-C 未裁决，保持 UNKNOWN
- 不解除 F-L00-07 —— DEMO 源不抵扣真实材料缺口
- `FROZEN=NO` · `PRODUCTION_READY=NO` · `REAL_E2E_PASS=NO`
- 未执行任何 git 提交
