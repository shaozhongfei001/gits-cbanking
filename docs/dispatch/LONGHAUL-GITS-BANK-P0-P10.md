# GITS Bank UX 长程无人值守施工程序

> Owner 授权：2026-08-25 全链路执行，不再阶段停问。  
> 状态：`LONGHAUL_AUTHORIZED`  
> 契约：`AUTHORITY_SOURCE_CHANGE=NO`（C3 只做 CCC 评审与 C2 降级，不改权威源）  
> 生产：`PRODUCTION_READY=NO` `FROZEN=NO`

## 总控规则

- Tech Lead 只派工、审门禁、开下一 Loop。
- Feature Pilot SubAgent 实现当前 Loop；失败先 FAILURES.md。
- Independent QA SubAgent 复跑后才可 `QA_PASS`。
- 阻塞写 `memory/BLOCKED.md`，改派或标记 blocked。
- 禁止 `git add .`；本程序默认不 commit。

## 波次（对应规划 P0–P10，零契约变更）

| 波 | Loop ID | 规划阶段 | 页面/能力 | C 策略 | 退出 |
|---|---|---|---|---|---|
| W0 | （已完成） | P0 接手 | 双包基线、CCC、P30 创建 | — | Owner OD 已落盘 |
| W1 | **P30-gits-bank-experience-shell** | P1 部分+P2 | Shell + P01–P03 只读；CI 契约非零 | C0/C1/C2 | ready_for_independent_qa → IQA |
| W2 | P31-gits-bank-customer-slice | P3 | P04–P10 只读/既有查询 | C0/C1；写=C2 | 同上 |
| W3 | P32-gits-bank-engagement-slice | P4 | P11–P19 复用 journey/previsit/CRM 既有合同 | C0；缺对象 C2 | 同上 |
| W4 | P33-gits-bank-need-task-degrade | P5 | P20–P22、P36：Need 禁用；Task/Commitment C0 | C2 Need；C0 任务 | 同上 |
| W5 | P34-gits-bank-proposal-degrade | P6 | P23–P30：建议书只读/禁用 G0–G5 写 | C2/C3 降级 | 同上 |
| W6 | P35-gits-bank-gov-degrade | P7 | P31–P40：HumanGate/Audit C0；其余禁用 | C0/C2 | 同上 |
| W7 | P36-gits-bank-mobile-degrade | P8 | P41–P44：无离线写；在线只读或禁用 | C2 | 同上 |
| W8 | P37-gits-bank-sit-gates | P9 | 适用用例执行；不强行 264 PASS | 证据 PLANNED→执行 | IQA |
| W9 | （Owner/Release） | P10 | UAT/发布/冻结 | **不自动授予** | 仍需人类 Owner |

W9 不由 Agent 签署 UAT/FROZEN。W1–W8 在 C2 降级下尽可能交付可运行界面。

Owner 验收包：`docs/dispatch/W9-gits-bank-uat-release.md`。默认范围是 **W9-A（已交付 C0/C2 壳）**；W9-B（V3.2 正式对象）依赖未签署的 C3 合同 Loop，不得与本波混签。

## 当前 Baton

W1–W8 Agent 链已结束。P37 Independent QA `qa_pass`（session `iqa-p37-20260825T175104Z`）。

**W9-A 人类 Owner 人工测试不通过**（`OD-GITS-BANK-UX-W9A-FAIL-2026-08-26`）：左导航把阶段页塞进一级域，配色未对齐 V3.2 Token；点选「互动对象」因 `GET /api/v1/interactions` 未实现被打成 500。`UAT_PASS=NO`。壳层已按 `NAV_GROUPS` 与 Token 返工；该 GET 正在按既有合同补只读实现。不改合同源。

Agent 链 `qa_pass` 会话（供 Owner 查阅，不是发布结论）：

| Loop | session | evidence sha256 |
|---|---|---|
| P30 | `iqa-p30-20260825T155239Z` | `c93a13b72688caef02d912c393ef7182b4a18d51f19bd4b605018a4445835457` |
| P31 | `iqa-p31-20260825T161011Z` | `c9196f5d0fbc8ecd647e460e80ef6f13684322d603a4a1be73e8a6a96f9e535e` |
| P32 | `iqa-p32-20260825T163009Z` | `b518926e7f3f1b9520f59124cbe80c4c0e6876ef52dbb4916bc544ddc8acee15` |
| P33 | `iqa-p33-20260825T164814Z` | `3e9cac1fa6a608daf0b66edbd70efd901317f2dac47297ed99c0e63dd358fb93` |
| P34 | `iqa-p34-20260825T170412Z` | `3600d8bcc9c8067bbe50b3be9fd774180370eeb7abd0e1c83e0f97c57657de51` |
| P35 | `iqa-p35-20260825T172016Z` | `15e859d7bfc081bff65f337c951f5cde0a47e0179b167a5705524ef5e12b7801` |
| P36 | `iqa-p36-20260825T173432Z` | `feb53817e016aca96190d05115aac33590c7c90d99fd6a5d013be9274072b8c2` |
| P37 | `iqa-p37-20260825T175104Z` | `035a98d97e6fc6c990ad3aab7e0ec6f0d7b3a414b503d9e20d2ea43087a9fff1` |

