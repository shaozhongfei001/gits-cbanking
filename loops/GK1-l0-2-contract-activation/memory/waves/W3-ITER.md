# W3｜ITER（L0-2 规划迭代记录）

## ITER-1：Loop 创建与守卫自愈

- **动作**：`make new-loop LOOP=GK1-l0-2-contract-activation HOLDER=tech_lead` → 创建成功。
- **测量**：`python3 scripts/loop_guard.py --loop GK1-l0-2-contract-activation`
- **结果**：**FAIL** — `STATE implementation_actor and Baton holder disagree`
- **根因**：初始把 `baton.holder` 设为 `feature_pilot`（意图是"把下一棒交给 FP"），但 `STATE.implementation_actor` 仍为 `tech_lead`；`loop_guard.py:76` 要求非 review 状态下二者必须一致。
- **修复**：
  - `STATE.json`：`baton` 保持 `tech_lead`，新增 `baton_next_holder: feature_pilot` 表达下一棒。
  - `ROLE_BOARD.yaml`：`baton.holder: tech_lead` + `baton.next_holder: feature_pilot`。
  - `NEXT_SESSION.md`：holder 回改为 `tech_lead`。
- **重跑**：`loop-guard: PASS`。

## ITER-2：GK0 守卫回归

- **动作**：把 `loops/GK0-contract-activation` 的 holder 从 `owner_review` 改为 `tech_lead`，表示"LB-2 已移交新 Loop"。
- **测量**：`make memory-check LOOP=GK0-contract-activation`
- **结果**：**FAIL** — `review state requires an independent QA or owner-review Baton holder`
- **根因**：GK0 的 `STATE.status = qa_pass` 属 review 状态，`loop_guard.py:73-75` 要求 holder ∈ {`independent_qa`, `owner_review`}。
- **修复**：holder 回退为 `owner_review`；改用 `board_status: L0_2_DISPATCHED_TO_NEW_LOOP` + `baton.next_holder: tech_lead` + `blocked_note` 表达移交，
  **不改 GK0 的 status**（红线：GK0 不标 closed）。
- **重跑**：`loop-guard: PASS`（GK0 与 GK1 双双 PASS）。

## 门禁执行说明

本波 **未执行** 六个 implementation 门禁（`contract_generate` / `contract_check` / `security_check` /
`gk_ke_examples` / `gk_ke_openapi_lint` / `gk_ke_hash`）——它们属 Feature Pilot 的实现交付，
TL 在 L0-2 不得代为执行与签署。

## 无 FAILURES 记录

两个 ITER 均为**规划期元数据自愈**，未涉及合同/实现变更，按 `record_before_fix` 语义不构成 Gate 失败，
故未写入 `FAILURES.md`（该文件保留给门禁失败）。
