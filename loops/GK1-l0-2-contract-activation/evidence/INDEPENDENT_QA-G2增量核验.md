# 独立 QA 增量核验报告：GK-KE-OWNER-003 落实（G2 增量）

- **角色**：Independent QA（gate_review）
- **Session**：`qa-gk1-g2-001`
- **依据**：`GK-KE-OWNER-003` §7.2「**核验增量**：QA 核对新增定义、对应关系及有效生成/消费者约束；
  受影响的语义拒绝条件保留测试计划或相应阶段证据。已有有效证据直接引用；**新增实质差异不可冒用旧 QA 通过**」
- **核验范围**：提交 `7034ddd` 引入的增量（三份定义 + 侧车登记 + 核验脚本 + 映射登记 + 确认函修正 + `ActivationPlan` 合同约束）
- **日期**：2026-09-12
- **结论**：**QA_PASS**（经 1 次 MAJOR 修复后）

---

## 1. 增量清单（本次核验对象）

| 文件 | 类型 | 变更 |
|---|---|---|
| `specs/gk-ke/v1/definitions/SIM-ASSET-P001.json` | 新增定义 | 产品卡集合→单卡选择/构造 |
| `specs/gk-ke/v1/definitions/SIM-MAP-FINANCE.json` | 新增定义 | 受限场景投影（有损） |
| `specs/gk-ke/v1/definitions/SIM-ROUTE-001.json` | 新增定义 | 访前融资路由切片 |
| `specs/gk-ke/v1/definitions/_registry.json` | 新增侧车 | 真实字节指纹登记 |
| `scripts/gk_ke_g2_definitions_check.py` | 新增脚本 | 结构核验 + 指纹计算 |
| `docs/integration/L0-2_G2_MAPPING_CONFIRMATION.md` | 新增登记 | 四问答复 + 认领 + 路径/hash |
| `specs/gk-ke/v1/schemas/ActivationPlan.schema.json` | **合同变更** | `planId` 增加 AC 前缀拒绝约束 |
| `specs/gk-ke/v1/examples/negative/ActivationPlan_3.json` | 新增负例 | AC-as-planId 拒绝 |

## 2. 逐项核验

| # | 核验项 | 结论 | 独立证据 |
|---|---|---|---|
| 1 | 三份定义存在且结构合规 | **PASS** | `gk-ke-g2-definitions-check: PASS`，`definitions: 3` |
| 2 | 内嵌 instance 通过对应 gk-ke/v1 Schema | **PASS** | `AssetVersion` / `KnowledgeMap` schema 校验通过 |
| 3 | **侧车指纹真实性**（独立重算） | **PASS** | 3/3 重算与实际文件字节**逐字节一致** |
| 4 | 无自引用回归 | **PASS** | 3/3 `origin.contentSha256 = null`（见 FAIL-2026-09-12-03） |
| 5 | **Q1 约束落地** | **PASS** | `sourceGranularity=COLLECTION`、`notIdentityEquivalent=true`、`lifecycle≠PUBLISHED` |
| 6 | **Q2 约束落地** | **PASS** | `noMatch` 与 `ambiguity` **分别定义**；`ambiguity=ROUTE_AMBIGUOUS`；`AC-NOT-IN-P20` 已排除；`claimed=true` 而 `implemented=false` |
| 7 | **Q3 约束落地** | **PASS** | `relation=SCENARIO_PROJECTION`、`lossy=true`、scope 限 SIM-C001/SIM-O01/INTERPRETATION、`whatItDoesNotProve` 已记录 |
| 8 | **Q4 约束落地** | **PASS（修复后）** | 见 §3 —— 首次核验为 **FAIL** |
| 9 | 未声称已发布/已实现 | **PASS** | `contentPublished=false`、`serviceReady=false`、`lifecycle=CANDIDATE` |
| 10 | 既有门禁无回归 | **PASS** | generate / check / security / examples(**20 pos / 41 neg**) / openapi_lint 全 exit 0 |
| 11 | 未改封版制品、未改 `generated/` 手工 | **PASS** | `git diff` 校验 |
| 12 | `CTR-GKKE-API-001` 状态未变 | **PASS** | 保持 `CONTRACT_CANDIDATE` |

## 3. **发现问题：FAIL-2026-09-12-04（MAJOR）**

**核验方法**：对 Q4「禁止复用 AC ID 作 planId」执行**负例验证**（而非仅读文档）：

```
baseline positive: VALID (good)
AC-id-as-planId: ACCEPTED (bad - constraint missing)
```

**判定**：`ActivationPlan.schema.json` 的 `planId` 仅有 `{type,minLength}`，
**Owner 决议的硬禁令未落到受控合同** → 该行为在实现层可被违反而不报错。

**为何这是真问题**：按 workspace 规则「合同 SSOT」，未落到合同的约束**无强制力**；
§7.2 明确要求 QA 核对「**有效生成/消费者约束**」，仅文档声明不构成有效约束。

**处置**：独立 QA 判定 `RETURN_TO_FEATURE_PILOT` → 按**合同先行**修复：

1. `specs/gk-ke/v1/schemas/ActivationPlan.schema.json`：`planId` 增加 `pattern: "^(?!AC[-_]).+$"` + 说明
2. `make generate` → `make check`
3. 新增负例 `specs/gk-ke/v1/examples/negative/ActivationPlan_3.json`

**复验（负例必须被拒）**：

| 输入 | 期望 | 实测 |
|---|---|---|
| `planId=SIM-PLAN-001` | VALID | **VALID** ✅ |
| `planId=AC-PREVISIT-001` | REJECTED | **REJECTED** ✅ |
| `planId=AC_PREVISIT_001` | REJECTED | **REJECTED** ✅ |
| 全门禁重跑 | 全 0 | **全 0** ✅（负例 40→41，全被拒） |

## 4. 独立性边界（明确未覆盖）

- **未**重放 KERT 仓源码（本环境只读参考；已按 §1 采信 TL 陈述，不冒充独立验证）
- **未**验证 L2-2 / L3 / L4 运行实现（§7.3 明确移交，不属 G2）
- **未**验证 `SIM-ROUTE-001` 的 canonical instance hash（策略无内嵌完整实体，见登记 §4.1）
- **未**代替 Owner 作出任何认领或映射决定
- **未**代替 KERT 维护方在 KERT 仓落盘正式副本

## 5. QA 结论

**QA_PASS**（G2 增量部分）。依据：

1. 三份定义结构合规、instance 通过 Schema 校验；
2. 侧车指纹**经独立重算逐字节一致**，无自引用；
3. Owner 决议 §3–§6 的约束**逐条在合同中或定义中落地并可被负例拒绝**；
4. 未声称已发布/已实现，状态区分（候选/激活/已发布/可执行）维持；
5. 既有门禁全部无回归；
6. 发现的唯一 MAJOR（FAIL-2026-09-12-04）已按合同先行修复并复验。

**G2 关闭建议**：本条核验通过后，G2 的「受控定义、身份、转换、责任、内容指纹」要件在**主仓侧**齐备。
仍建议 TL 在登记中如实标注：**KERT 仓正式副本待落盘**（本环境无写权限）。

本报告**不代替** Owner 裁定，也**不**自动使 ACT-01 生效。
