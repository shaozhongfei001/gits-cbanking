# GK0-contract-activation｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

---

## FAIL-2026-09-11-01: 机构委员会架构评审退回补正（RETURN_TO_HLD）

- **时间**：2026-09-11
- **角色**：Tech Lead（记录）
- **Gate**：独立 QA 前（此前 STATE.json 误标 `ready_for_independent_qa`）
- **分类**：BLOCKER（依据/实物/证据/口径类问题）
- **现象**：机构委员会《GITS-KERT CodeBuddy 交付物架构评审报告 V1.0》（GK-KE-AR-20260911-01）对交付清单作出退回决定：契约符合性 `RETURN_TO_HLD`，设计包完整性与实现完成效果 `INSUFFICIENT_EVIDENCE`。
- **根因**（TL 复核确认）：
  1. 交付清单 B 引用"§0.3 十层/§2.2 17 端点/§2.4 12 事件"等总契约 A 中不存在的锚点，引用体系未对齐（F01）。
  2. 交付包实物（MANIFEST 117 文件）未随评审提交，仅上传清单（F02）。
  3. 计数口径错误：清单声称"100 文件/json 8"，实测 MANIFEST 117 文件/json 69（F10）。
  4. 设计正文未落到可机器校验的 Schema/负例清单/复算脚本（F03–F08）。
- **修复**（AR-R0~R5，本会话完成 R0~R3 核对 + R4/R5 派工）：
  - AR-R0：固定依据（总契约 hash `a4abb089...` 与报告一致），交付包纳入 git（HEAD `f79f2b1`）。
  - AR-R1：实物补交 + 追踪映射 + 造数/复算验证。
  - AR-R2：F06 + F03–F05/F07 全量核对，缺口定位为 6 个合同源变更。
  - AR-R3：模拟闭环核对，账务/引用/3000 万场景全通过，缺口 H1/H2。
  - AR-R4/R5：TL 派工单（docs/dd/GITS-KERT_TL_派工单_AR-R4_R5_V1.0.md）。
- **下一动作**：Feature Pilot 执行 WP-R4-1（6 个合同源变更）→ 独立 QA → Owner 决议。
- **状态回退**：STATE.json 从 `ready_for_independent_qa` 回退到 `in_progress`（评审退回，不得继续宣称 ready_for_independent_qa）。

