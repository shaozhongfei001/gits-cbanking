# L12 证据台账

- Loop: `L12-conflict-health-candidate` · 计划 `PI-ARCH-IMPLEMENTATION-01` · 阶段 B
- 日期: 2026-09-06 · 状态: `DEV_SELF_CHECK_PASS`
- 上游: L11（29 EvidenceSpan / 14 断言）

---

## 1. 冲突检测

命中 DEMO 内建冲突（L10 故意保留）：

```
CNF-PRODCM001-757c6c3b  eligibility.minAccountBalance  VALUE_MISMATCH
  SRC-CM-001 第十条：现金池主账户每日最低留存余额为人民币 50 万元
  SRC-CM-003 第六条：集团现金池主账户每日最低留存余额为人民币 100 万元
```

- `status=OPEN`、`resolution=null` —— **不自动择一**（INV-CNF-03）
- 新建 1 条 `CONFLICT` 断言，`supersedes` 指向被取代的 CANDIDATE 断言 —— **不原地覆盖**（INV-ASM-06）
- `normalizedValue=null`（INV-ASM-03）、`conflictId` 非空（INV-ASM-04）

**两次误报修正**（详见 FAILURES）：

| 轮次 | 现象 | 根因 | 处置 |
|---|---|---|---|
| 1 | customerSegment / openingChannel 报 VALUE_MISMATCH | `conflictType` **硬编码**为 VALUE_MISMATCH，ENUM 判定结果被覆盖 | 改为写入计算出的 ctype |
| 2 | customerSegment 报 SCOPE_OVERLAP | 条款内部"适用于 X；Y 不适用"被读成跨源互斥 | 移除 ENUM 自动冲突判定，改由体检标注 `needsHumanReview` |

结论：**只保留数值型（MONEY/RATE）的自动冲突判定**，语义型冲突交 Owner 复核 —— 自动判定误报的代价高于漏报。

---

## 2. 字段体检（`02_work/reports/PROD-CM-001.health.json`）

```
interpretationReady = False    blockers = 3
```

| fieldPath | 状态 | 证据 | 阻断 |
|---|---|---|---|
| identity.productCode | UNKNOWN | 0 | ✅ HARD |
| eligibility.customerSegment | CANDIDATE | 3 | — |
| eligibility.minAccountBalance | **CONFLICT** | 8 | ✅ HARD |
| eligibility.prerequisiteProducts | CANDIDATE | 1 | — |
| compliance.regulatoryBasis | UNKNOWN | 0 | ✅ HARD |
| pricing.serviceFee | UNKNOWN | 0 | —（SOFT） |
| process.openingChannel | CANDIDATE | 3 | — |

`recommendationReady=false`（DEMO 派生恒定，INV-EVS-09/INV-RLS-09）。

---

## 3. 候选卡编译

`02_work/candidate-cards/PROD-CM-001.candidate-card.json`

- `legacyCardReused=false` —— **不复用 13 张 legacy card**，完全从断言编译
- `provenanceState=DEMO`
- 未 Owner 复核字段 `value=null`（不产生规范值）
- 七字段全量

---

## 4. 门禁

```
KERT L12 冲突/体检/候选卡门禁：22/22 PASS
统一门禁：11/11 PASS
```

校验项含：CNF-001/ASM-001 schema 校验、INV-CNF-02/03、INV-ASM-03/04/06、
候选卡不复用 legacy、体检自洽（有阻断 ⇒ 两用途 false）。

---

## 5. 本 Loop 不证明什么

- 不证明冲突已解决 —— 冲突**故意保留**，等 Owner 裁决
- 不证明可发布 —— `interpretationReady=false`
- 不证明 ENUM 语义冲突可被自动发现 —— 本 Loop 明确**不做**该判定
- 未执行 git 提交
