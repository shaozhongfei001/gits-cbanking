# PC1-product-center-shell｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

---

## PC1-GOV-01 · 治理违规：TL 未声明角色切换即编写实现代码

```text
时间：2026-09-22（PC1 实施期间），记录于 2026-09-22T06:10+00:00
类型：GOVERNANCE（非命令失败；record_gate.py 不适用于本条，故按同格式手工追加，append-only）
规则依据：.codebuddy/rules/senior-workflow/RULE.mdc
  - "禁止 Tech Lead 直接写 Feature 实现代码（必须切换到 Feature Pilot）"
  - "同一对话中禁止角色混用。如果需要切换角色，明确声明切换。"
事实：同一上下文内以 tech_lead 身份：
  ① 审批并登记合同（CTR-PKC-API-001 / CTR-PKC-DOM-001 / PkcError.SOURCES_UNAVAILABLE）；
  ② 随后直接编写实现（apps/api/.../productcenter/*、frontend/src/components/product-center/*、
     frontend/src/views/ProductCenterView.vue）且未声明 [角色切换] tech_lead → feature_pilot。
证据：commit 7098022、4f22c85、8241033（同会话内既含合同变更又含实现）
分类：GOVERNANCE / MAJOR（不构成 BLOCKER：实现本身有测试与证据；但对"审批方与实现方分离"的规则构成破坏）
下一动作：
  1. 登记 Owner 裁决 R-4（docs/dispatch/PI-ROLE-角色与决策权登记-V1.0.md §1）与 §4 强制切换规则；
  2. 后续实现阶段必须单独上下文并以 [角色切换] 显式声明 feature_pilot；
  3. 本条不追溯性撤销已交付的 PC1 证据，但 PC1 的"合同审批"与"实现"应视为**两次不同角色的动作**分别记账。
根因（2026-09-22 追加）：以"先把页面做出来"为目标，跳过角色声明；且当时尚未建立业务代表角色，
  TL 在缺少业务结论的情况下自行推进到实现，属**角色缺位下的越位**。
```

---

## PC1-ANA-01 · 分析错误：以"环境未配置"判定"能力缺失"，导致错误的基线结论

```text
时间：2026-09-22，记录于 TL 差异表评审阶段（Owner 要求以 P38 为基线后）
类型：ANALYSIS（非命令失败；record_gate.py 不适用，按同格式手工追加，append-only）
事实：
  TL 曾据运行态 `/api/v1/product-knowledge/PROD-CM-001/interpretation` 返回
  `503 {"code":"FAILED_CLOSED","message":"KERT 解读快照目录未配置"}`，
  得出"P38 的制度深度解读拿不到 / 能力不完整"的结论，并据此论证新版价值。
复验（2026-09-22）：
  以 `--gits.product-knowledge.snapshot-dir=<KERT>/04_serve/interpretation` 启动 8089 实例，
  同一端点返回 HTTP 200：releaseId=RLS-2026.09.06.1、isStale=false、三视图可读、
  字段证据可展开。⇒ P38 该能力**真实可用**，先前结论**不成立**。
分类：ANALYSIS / MAJOR（错误结论已进入面向 Owner 的汇报，构成误导风险）
根因：把"本机演示环境未配置"当成"系统能力缺失"；未区分**配置缺失**与**能力缺失**，
  且未按"先构造可用环境再判定"的纪律复核。
下一动作：
  1. 撤回相关结论（见 docs/dispatch/PI-DELTA-P38-新版能力差异表-V1.0.md §1 与 §4 E-1）；
  2. 今后凡涉及"某能力是否具备"的判定，必须：先构造最小可用配置 → 再实测 → 才允许下结论；
     仅有失败响应时，只能记 `UNKNOWN`，不得记"缺失"。
```
