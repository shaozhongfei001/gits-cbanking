# L11 FAILURES

> Loop: `L11-evidence-span-assertion`（PI-ARCH-IMPLEMENTATION-01 / 阶段 B）
> 建立: 2026-09-06

---

## F-L11-01 · MINOR · RESOLVED

**标题**：首次红测的注入写法幂等，导致"红测通过"实为红测失效

**证据**：注入脚本把 quote 末字替换为**。**，而原文末字本就是**。**，文件内容未变。
门禁返回 528/528 PASS，一度被误读为"门禁未拦截篡改"。

**危害**：与 L10 的 F-L10-02 同源 —— **用无效的注入得出的 PASS 是假安全**。
若就此收工，等于用一次空转证明门禁有效。

**修复**：改为在 quote 前插入 `"演示篡改"` 后重做。

**验证**：
```
FAIL | EVS-SRCCM001-dbe96c76 quoteHash == SHA-256(quote)
FAIL | EVS-SRCCM001-dbe96c76 quote 可在 Fragment 内原样定位
→ 526/528，退出码 1；还原后 528/528
```

**教训**：红测必须**先证明注入确实改变了数据**（打印 before/after 或比对 hash），
再断言门禁失败。后续 Loop 沿用此要求。

---

## O-L11-01 · OBSERVATION · OPEN

**标题**：`identity.productCode` 的 UNKNOWN 暴露关键词分类粒度不足

**事实**：`SRC-CM-001` 第四条「产品代码统一为 `CM-CASH-POOL-001`」，
因条款同时含"适用范围"而被判为 `ELIGIBILITY`，而字段 `identity.productCode`
的 `allowedClaimTypes=[PROCESS]`，按 INV-EVS-05 资格不符 → UNKNOWN。

**判断**：**不是缺陷，是 fail-closed 正确工作**。擅自放宽 claimType 匹配就是绕过不变式。

**处置**：登记为观察项。若 Owner 认为该字段应被覆盖，正确路径是
① 调整 `SRC-CM-001` 的 `allowedClaimTypes`（合同变更）或 ② 细化条款切分粒度，
**而不是**在抽取器里放宽资格校验。留待 L12 体检报告呈现给 Owner 裁决。

---

## O-L11-02 · OBSERVATION · OPEN

**标题**：`clauseVerified=false` 使全部证据按 INV-EVS-07 不得支撑 RECOMMENDATION_READY

**影响**：演示链路可跑通解读（INTERPRETATION_READY 路径），但**到不了推荐门槛**。
这是红线要求（DEMO 不冒充真实）的必然结果，非缺陷。

**处置**：L13 签发 Release 时必须显式带 `provenance_state=DEMO` 且
`recommendationReady=false`。已在 O-L10-01 登记的 RLS-001 字段缺口与此联动。

---

## 承继缺陷（本 Loop 未改变）

| ID | 状态 |
|---|---|
| F-L10-01 `make check` FAIL（CTR-PR-API-001） | OPEN（承继，非本 Loop 引入） |
| O-L10-01 RLS-001 缺 `provenanceState` 字段 | OPEN（L13 前必补） |
| O-L10-02 SourceVersion/Fragment 无 schema 合同 | OPEN（建议 L11 前裁决 → 仍未裁决，继续挂起） |
| F-L00-07 真实权威材料缺口 27/28 | BLOCKED_ON_OWNER |
| F-L00-02 / F-L00-09 / F-L03-03 | OPEN |
