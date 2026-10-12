# ONTO1-ontology-split｜Handoff

| 项 | 值 |
|---|---|
| 交接时间 | 2026-09-20（含 14:20Z 送审程序包 `W-1/review-submission`、15:05Z `W1-prep/P-1`、15:12Z `W-1/D2-pack`、15:22Z `W-1/D4-pack`） |
| 交出角色 | `tech_lead`（orchestration；三个决策/准备包由派发子角色编制，Baton 未换手） |
| 接棒角色 | `tech_lead`（同一 holder 继续，Wave -1 未完成项待续） |
| 波次 | `W-1`（只读分析） |
| 状态 | `in_progress`；`blocked=false`（非技术阻塞已登记，未停机） |

## 1. 一句话交接

Wave -1 的 WI-A1/A2/A4/A5/A6/A7 已交付且门禁绿（含三套变异复验）；**复审轮送审程序包已就绪**（13/14 齐备 + `wi_review_package_integrity` PASS + 操作清单/回收预案落 `memory/handoffs/`），**待 Owner 发出**；**D2/D4 两个决策包均已就绪且可勾选**（`W-1/D2-pack` 非 Loop 门禁 `--gate` G1~G8 全 PASS；`W-1/D4-pack` 已登记 Loop 门禁 `wi_a5_d4_pack` PASS + `wi_a5_d4_pack_selftest` PASS）；**Wave 0 及以后必须等书面复审结论**；Wave 1 另受两个角色任命阻塞（公共语义 Owner / Integration Contract Owner）。

## 2. 接手第一件事

0. 读 `memory/handoffs/`（送审操作清单 + 结论回收与门禁更新预案 + 包级交接）——结论一到，**先按预案 §1 判有效性，再落门禁**；
1. 读 `memory/NEXT_SESSION.md`（待办与优先级）；
2. 读 `memory/ORCHESTRATOR.md §0/§2`（门禁位置与 G-1 状态）；
3. 核对 `memory/OWNER_REQUESTS.md` 是否有新签署件到达；
4. 复跑 `python3 scripts/onto1_consumer_scan.py --gate` 与 `python3 scripts/onto1_attribution_rebuild.py --gate` 确认基线未漂移（若基线哈希变了，先查是谁改的）。

## 3. 本会话未做（有意为之，不是遗漏）

- 未执行 `make generate`（Wave -1 只读，`generated/` 未动）；
- 未改 `specs/semantic/`、`specs/CONTRACT_INDEX.yaml`、`docs/dd/`；
- 未写 KERT 仓任何文件（本环境只读）；
- 未刷新代码事实索引（KERT 漂移 144，已如实声明 `INDEX_STALE(144)`）；
- 未记录 `DEV_SELF_CHECK_PASS` / `QA_PASS`（Wave -1 无实现可交付，且开发角色不得自签 QA）。

## 4. 风险提示（给接手人）

- **最大风险不是技术，是"等"**：复审结论未达前，任何 Wave 0+ 动作都会越界；本 Loop 的所有可做之事已做到 Wave -1 边界。
- **词法扫描的误用风险**：`FOLLOW_MIGRATION` 1038 行是**候选**义务，不是确认清单。若 Wave 2 直接照单执行会改错文件（同名不同物）。
- **`AC-` 号段碰撞**：任何按裸 `AC-` 计数或替换的动作都会误伤银行账号数据。

## 5. W-1.5 批次收工（2026-09-21T00:05Z）

**板面**：30 门禁 = **29 pass / 1 fail**（唯一 fail = `wi_a4_namespace_collision`，**仅 C-2 两处真实前缀冲突**，Wave 3 修）。`loop-guard` PASS、`onto1-evidence-board` PASS、孤儿日志 0、`independent_qa` 仍 `pending`（无人代签）。

**三包结论**：PKG-A1 = **ACCEPT**（+ 后续 PKG-A1b 升格 65 行）；PKG-A2 = **ACCEPT_WITH_CONDITIONS**（T-1~T-3 待 D3/G-1）；PKG-A3 = **NOT_ACCEPTED**（合并 7 条 C1~C7，含 QA 的 Q-1 新漏检通道）；QA 第二轮 = **NOT_ACCEPTED**（Q-1/Q-2 BLOCKER、Q-4 MAJOR，TL 已逐条裁定）。

**新增纪律（下一 holder 必读）**：
- **D-11 交付与证据绑定**：post-DONE **冻结** revision；`--gate`/`--selftest` 日志**必须自证 revision**（用 `scripts/onto1_gate_log.py`，**不要**用 `echo`——`loop_guard` 会判 dummy）；TL 审计前**连续两次取哈希确认稳定**；**崩溃 ≠ FAIL**（缺输入须具名 FAIL 或 exit=3）。
- **D-12 放行类要求必须附反例清单**：凡放行/白名单/豁免/收窄，必须同时给出"**不得放行**"反例并各配变异（本轮两次代价：`S-4`、Q-1）。
- **D-3 补丁**：`rule_statement` 放行改**联合判定**（命中标记 ∧ 规则语境 ∧ 不含合规谓词），主题词（`词表` 等）移出标记表。

**下一会话从这里开始**：`T-4`（A3 复交后沙箱复验四例 + 重记陈旧门禁 `wi_a4_namespace_collision_selftest` / `wi_a3_reference_alignment`）→ `T-5`（PKG-A1b 复核 + 重记 A1 两门禁）→ 重派 `qa-w15` 第三轮（**不得记 `QA_PASS`**）。详见 `memory/NEXT_SESSION.md` §W-1.5 批次收工记录。
