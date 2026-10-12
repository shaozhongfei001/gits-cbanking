# ADR · 产品规则资产（ASSET-KNOW-PRODUCT-RULES）缺口处置

- 日期：2026-09-07
- 角色：Tech Lead（PI-ARCH-IMPLEMENTATION-01）
- 状态：**ACCEPTED（路径 A 已执行，2026-09-07）**
- 关联：F-L13-01 · L13 `rulePackageHash` 占位 · SP-15 · AC-PRODUCT-RECOMMEND-001

---

## 背景

`specs/knowledge-architecture/skills/SP-15.json`（产品适配与综合方案，
`implementationType=RULE_MODEL`）声明依赖 `ASSET-KNOW-PRODUCT-RULES`；
`activations/AC-PRODUCT-RECOMMEND-001.json` 同样引用它。
但 `assets/` 下**只有 20 份资产清单，其中没有产品规则** —— 只有 `product-cards.md`。

`scripts/validate_knowledge_architecture.py` 因此报错：
`SP-15.json: unknown asset dependency ASSET-KNOW-PRODUCT-RULES`，
导致 `make check` 在 `knowledge-architecture-check` 步骤失败。

同一缺口在 PI-ARCH 侧的投影：L13 的 Release 用 `rulePackageHash = SHA-256("RULEPACKAGE:EMPTY")`
占位 —— **产品规则包同样尚未建设**。两者是同一个缺口在两个体系里的表达。

---

## 关键约束（决定了这不是"顺手就能修"）

1. 校验要求 `exactly 20 P20 asset manifests` —— **新增第 21 份资产必须同时改这条常量**，
   即改动 P20 受控资产集基线，属 `knowledge_architecture_owner` 域。
2. 资产清单必填 `governance.owner/classification/permissionInherit/allowedActions`
   且 `evidence.citationRequired/sourceVersionRequired/contentHashRequired` 全为 `true`。
   一个**尚未建设**的资产无法诚实填写这些字段。
3. 直接把 `ASSET-KNOW-PRODUCT-RULES` 从 SP-15 依赖里删掉，会让契约声称
   "产品适配不需要产品规则"，**掩盖缺口** —— 与本计划"不留白、不假办"原则冲突，不予采用。

---

## 裁决

**不在本计划内擅自新增 P20 资产，也不删除依赖声明。**
维持 `F-L13-01 = BLOCKED_ON_OWNER`，并向 Owner 提供两条解除路径。

| 路径 | 动作 | 代价 | 适用判断 |
|---|---|---|---|
| **A 建设资产** | 新增 `assets/knowledge-rules/product-rules.md` + 校验常量 20→21，并同步 KERT 规则包使 `rulePackageHash` 非占位 | 需确定规则包来源、owner、密级、证据要求 | 产品规则**确实要由知识架构承载** |
| **B 撤回声明** | 从 SP-15 与 AC-PRODUCT-RECOMMEND-001 移除该依赖，并同步把 SP-15 的 `implementationType` 从 `RULE_MODEL` 改为不依赖规则包的类型 | 契约弱化，需确认产品适配确不由规则驱动 | 产品规则**改由 KERT Release 承载**、知识架构不重复持有 |

**Tech Lead 建议：选 A。**
理由：SP-15 是 `RULE_MODEL` 实现，产品规则是它的必要输入；KERT 侧已有
`rulePackageHash` 槽位等待填充，两处一起建设可一次性消除双写风险。

---

## 最小解除步骤（Owner 选定后执行）

路径 A：
1. 新增 `specs/knowledge-architecture/assets/knowledge-rules/product-rules.md`
   （front matter 含 `assetId` 与 `governance` / `evidence` 必填项）
2. `scripts/validate_knowledge_architecture.py`：`len(assets) != 20` → `!= 21`
3. KERT：规则包落地后重跑 `l13_publish_release.py`，使 `rulePackageHash` 不再是 EMPTY 占位
4. `make check` 与 `python3 specs/product-knowledge/check_all.py` 双复跑

路径 B：
1. `SP-15.json` 的 `assetDependencies` 移除 `ASSET-KNOW-PRODUCT-RULES`
2. `AC-PRODUCT-RECOMMEND-001.json` 移除对应 `assetId`
3. 重新审视 SP-15 的 `implementationType` / `ruleDependencies` 是否仍自洽

---

## 影响

- `make check` 在 `knowledge-architecture-check` 持续失败 → CI 结论不可用
- **不影响** PI-ARCH 的 L10–L13 交付：统一门禁 `check_all.py` 11/11 PASS，
  解读 API 已通过真实 E2E（S1–S17 全 PASS）
- 不阻断演示级使用；阻断的是"拿到 CI 绿灯"这一步
