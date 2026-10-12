# PI 独立 QA 交接 V1.0

```text
交给人：tech_lead（TL，实现与分析方）｜ 交给：独立 QA（**智能体 QA 角色**，Owner 2026-09-20 裁决 R-3）
交接时间：2026-09-22 ｜ 交接对象物：GITS-PI-EXPERT-REVIEW-20260922-R2.zip + 本仓 Loop
当前最高结论：DEV_SELF_CHECK_PASS（作者自检）——**QA_PASS 未申请、未签发**
```

## 1. 独立性要求（先说清楚，避免假独立）

| # | 要求 | 说明 |
|---|---|---|
| `I-1` | **不得以本包结论为依据** | 包内文档是"主张"；QA 须自行复算证据并形成独立判断 |
| `I-2` | **必须独立复跑命令**，不得只读 `evidence/test-results/*.log` | 包内日志系**同一作者在同一环境**复跑，不构成独立环境复现 |
| `I-3` | **必须自行构造变异用例**（见 §3） | 本仓历史教训：夹具全为正例 ⇒ 否定式断言恒真 |
| `I-4` | 若无法提供独立环境，须显式登记为"**授权下的降级独立**" | 参照 `loops/GK17-ontology-unified-map/memory/ROLE_BOARD.yaml` 既有先例：其判定为"判定建议"，**不构成 QA_PASS** |
| `I-5` | 独立性证据须落盘 | 复跑命令、退出码、原始输出、环境差异说明，写入被验 Loop 的 `evidence/` |

## 2. 待验清单（可执行）

| # | 待验项 | 方法 | 期望 |
|---|---|---|---|
| `Q-01` | R2 包结论是否可复算 | 按 R2 `02_REVIEW_CHECKLIST.md` B1–B9 逐项执行 | 每项能复算；不能复算者判"未被证据支持" |
| `Q-02` | 反向判否（R2 `02` §D 六条） | 逐条检查是否存在：截图/样本与声明不一致、空证据行、UNKNOWN 误判、用时结论、DEMO 数值结论、越界表述 | 全部不成立 |
| `Q-03` | §3 变异用例 | 见下 | 变异必须被捕获 |
| `Q-04` | 隔离控制有效性 | 在自己环境复现 `gits.product-knowledge.enabled=false` ⇒ 链①② 404、新版 200 | 一致 |
| `Q-05` | 受控失败语义 | 复跑 `purpose=RECOMMENDATION`（422）、`view=FOO`（400）、未发布产品（404） | 一致；**409 未构造 ⇒ 记 UNKNOWN，不计通过** |
| `Q-06` | 未改受控源 | 检查 `git status` / diff：`specs/`、P38 文件、KERT 制品是否有本任务改动 | 无 |
| `Q-07` | Loop 治理 | `scripts/loop_guard.py --loop PC-i1-chapter-inheritance --memory-only/--evidence-only` | PASS；`independent_qa` 仍为 pending |
| `Q-08` | 角色合规 | 检查是否存在"TL 同上下文写实现"（`PC1-GOV-01` 复发） | 无复发；实现尚未开始 |

## 3. 必须由 QA 自行构造的变异用例（mutate → 必须 FAIL；restore → 必须 PASS）

| # | 变异 | 期望 |
|---|---|---|
| `M-1` | 把新版某章节由"未接入"改为**静默空占位** | 断言 `12 章全部有落点且无空占位` 必须 **FAIL** |
| `M-2` | 删除 C6（前置/互斥/替代/配套）独立区块 | `C6 独立可见` 断言必须 **FAIL** |
| `M-3` | 把 C9（风险与人工复核）并入比较表 | `C9 独立可见` 断言必须 **FAIL** |
| `M-4` | 让附录原文不可读（去掉原始材料区） | `事实不丢` 判定必须 **FAIL** |
| `M-5` | 在比较章节引入星级/胜率/推荐语 | 非推荐红线断言必须 **FAIL** |
| `M-6` | 在 DEMO 环境放开 `purpose=RECOMMENDATION` | 422 断言必须 **FAIL** |

> 说明：`M-1`–`M-4` 需等 `PC-i1` 实现完成后执行；`M-5`/`M-6` 现在即可执行（后者为配置级）。

## 4. 门禁判定权与禁止项

| 项 | 归属 |
|---|---|
| 判定门禁结论（`QA_PASS` / 退回） | **独立 QA**（唯一） |
| 业务范围与验收 | Owner |
| 合同文本 | 合同 Owner（`knowledge_architecture_owner` / `integration_contract_owner`） |
| 修复与取证 | TL → `feature_pilot`（实现另起上下文） |

**禁止**：QA 修改实现以通过测试（须退回 `feature_pilot`）；以"页面看起来正常"代替证据；在证据不全时签 `QA_PASS`。

## 5. 当前阻断（QA 可先行判定但不阻断其启动）

| 编号 | 阻断项 | 归属 | 影响 |
|---|---|---|---|
| `S-1` | 合同变更三项未签 | 合同 Owner | `I3`/`I4`/`P-3` |
| `S-2` | P38 冻结范围解除未批 | Owner | `P-2`（路径修复补丁不可应用） |
| `S-3` | 同业来源（B/SIM）启用确认 | 产品 Owner + 合规 | 比较章③ |
| `S-4` | 40 条悬空产品引用分类 | 产品 Owner | 比较/前置/互斥章的确定结论 |

## 6. 交接物清单

| 物 | 位置 |
|---|---|
| R2 整改包（含全部证据与哈希） | `/home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R2.zip`（sha256 `747a5b4a…`） |
| R1 原包（对照，未覆盖） | `/home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R1.zip`（sha256 `f680d1f1…`） |
| Owner 裁决登记 | `docs/dispatch/PI-O-裁决登记-2026-09-22.md` |
| 合同变更候选提案 | `docs/dispatch/PI-CONTRACT-PROPOSALS-契约变更候选提案-V1.0.md` |
| 待实现 Loop | `loops/PC-i1-chapter-inheritance/`（scope/gates/exit criteria 已定义，未开始实现） |
