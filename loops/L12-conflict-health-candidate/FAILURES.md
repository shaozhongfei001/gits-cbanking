# L12 FAILURES

> Loop: `L12-conflict-health-candidate` · 建立 2026-09-06

---

## F-L12-01 · MAJOR · RESOLVED

**标题**：`conflictType` 硬编码为 `VALUE_MISMATCH`，覆盖实际判定结果

**发现**：首轮运行输出 customerSegment / minAccountBalance / openingChannel 三个冲突，
类型**全部**显示 `VALUE_MISMATCH`，而代码已按 valueType 分流判定。

**根因**：构造 ConflictCase 时 `"conflictType": "VALUE_MISMATCH"` 为**字面量**，
未使用计算出的 `ctype`。判定逻辑正确但被写入阶段覆盖 —— 与 F-L10-02「门禁假安全」同源：
**判定了不等于生效了**。

**修复**：改为 `"conflictType": ctype`。

---

## F-L12-02 · MAJOR · RESOLVED

**标题**：ENUM 字段多源互补被误判为冲突

**证据**：`SRC-CM-001` 第五条「适用于大型企业客户、集团客户、机构客户。
**小微企业客户不适用**本产品」—— 同一条款内部的适用性限定，被"存在肯定词 + 存在否定词"
规则判为 `SCOPE_OVERLAP`。同理 `process.openingChannel` 的柜面/网银/直联列举属**互补**。

**处置**：
- 移除 ENUM/TEXT 的自动冲突判定，**只保留 MONEY/RATE 数值冲突**；
- 语义型字段在体检报告标注 `needsHumanReview=true`，交 Owner 复核。

**理由**：自动判定误报会把"正常的多渠道说明"变成"待裁决冲突"，
污染 Owner 审核队列并制造虚假阻断 —— **误报代价高于漏报**。

**验证**：修正后冲突数 3 → 1，仅保留 DEMO 内建的真实数值冲突。

---

## 承继（本 Loop 未改变）

| ID | 状态 |
|---|---|
| F-L10-01 make check / generate 失败 | 已于 L13 修复（15 条合同缺 generated 目标 + yaml_taxonomy 不支持） |
| O-L10-01 RLS-001 缺 provenanceState | 已于 L13 修复（补字段 + INV-RLS-09 + V023 约束） |
| O-L10-02 SourceVersion/Fragment 无 schema 合同 | OPEN |
| F-L00-07 真实材料 27/28 | BLOCKED_ON_OWNER |
