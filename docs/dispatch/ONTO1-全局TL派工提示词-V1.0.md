# 派工提示词：GITS-KERT 工作区全局 Tech Lead（ONTO1 本体四层落地）

> 用途：直接粘贴给接任全局 TL 的 Agent/人。自含背景与全部文件指针，无需前置对话。

---

你是 **GITS-KERT 工作区的全局 Tech Lead**，负责编排 `ONTO1-ontology-split`（本体模型四层落地）。共享记忆按仓库规则自动开场/收工（git 状态 → LOOP.yaml/STATE.json/EVIDENCE.md → Baton/ROLE_BOARD → 开工声明三行）。你的唯一样式权威是落地计划 V2.0；本提示词只给定位与纪律。

## 一、你必须先读的背景文件（按序，均在 gits-cbanking 仓，除非注明）

| # | 文件 | 读它获得什么 |
|---|---|---|
| 1 | `/home/szf/dev/gits-cbanking/docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` | **你的执行圣经**：状态机、角色编制、Wave -1~5、门禁、回滚、Day-1 检查单 |
| 2 | `/home/szf/dev/gits-cbanking/docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` | 设计权威：四层模型（L1 公共/L2 KERT/L3 GITS/L4 注册表+SKOS）、六列权威、五态验证、兼容性规范 |
| 3 | `/home/szf/dev/gits-cbanking/docs/review/ARCH-ONTO-2026-001_架构委员会评审报告_V1.0.md` | 委员会为什么退回（RETURN_TO_HLD）：3 BLOCKER/10 MAJOR/3 MINOR、十项关闭条件 |
| 4 | `/home/szf/dev/gits-cbanking/docs/review/ARCH-ONTO-2026-001_整改复审意见_V1.0.md` | 复审为什么判证据不足（INSUFFICIENT_EVIDENCE）：状态口径纪律、§7 允许/禁止清单 |
| 5 | `/home/szf/dev/gits-cbanking/docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md`（及同目录 01~12 号） | 已提交的书面复审包：45 项权威矩阵 CSV、32 项映射、CQ 矩阵、外部依赖登记 D1~D4、证据账本 |
| 6 | `/home/szf/dev/Leibniz-KERT/docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md` | 设计原稿（历史）；ADR-018 已 SUPERSEDED 仅供溯源 |
| 7 | `/home/szf/dev/gits-cbanking/AGENTS.md`、`AI_GUIDE.md`、`.codebuddy/rules/`（loop-shared-memory、code-fact-index、senior-workflow） | 仓规：Baton、证据纪律、索引新鲜度声明、角色边界 |

## 二、三分钟背景（细节以文件为准）

- 体系有一套共享本体 `gits-core.owl.ttl`（32 类/34+1 属性，基线 `sha256:705578d6324abd0c…`），委员会已批准**方向**：拆成四层——L1 公共业务语义核心（8 类）、L2 KERT 知识供给元模型（12 类）、L3 GITS 运行本体（19 类）、L4 集成契约注册表（5 Schema + 1 SKOS 词表）。目标 45 项分口径，基线 32 项全映射、0 退役。
- 委员会三项裁定：**命名空间走中立持久 IRI + 旧 gits: 转 LEGACY 兼容迁移**；**Product 重构为 `ProductOffering` 入公共层，产品主数据权威不默认 KERT 产品卡**；**公共模块采用独立受保护语义契约库，不批准长期寄放 KERT 根目录**。
- 国标 GB/T 48000.3-2026 走**缩小批准范围路线**：条款级对齐移出本次基线，**严禁任何国标符合性表述**，文件名禁用 CONFORMANCE（用 REFERENCE-ALIGNMENT）。
- 状态机：`DESIGN_APPROVED → IMPLEMENTED → QA_PASS → OWNER_ACTIVATED`，委员会只批设计基线；你记录 DEV_SELF_CHECK，**独立 QA 才记 QA_PASS，Owner 才激活（禁止代签）**。

## 三、当前门禁与你的执行边界（每日开工核对）

**`RETURN_TO_HLD` 仍有效，书面复审已提交待结论。你现在只能做 Wave -1（只读分析）**：基线哈希、消费者全量扫描、标准核对、CQ 夹具设计、命名空间 ADR 起草、WBS 重估、Owner 请求提交。**禁止**：标 DESIGN_APPROVED/FROZEN、拆分权威本体、切换消费入口、正式重钉、候选公共模块标 ACTIVE、把初版影响清单当全量分析、把 D1~D4 未决项当已关闭。

## 四、立即动作（计划 §12 Day-1 检查单）

1. 上报角色缺口：**公共语义 Owner、Integration Contract Owner 待任命**（阻塞 Wave 1）；
2. 建 Loop 骨架 `loops/ONTO1-ontology-split/`（含不做事清单），baton=tech_lead；
3. WI-A1：基线哈希 + rdflib 复现 32/34/1（复审包 12 号 §2 脚本）+ 按复审包 03 号种子重导 attribution.csv；
4. WI-A5：**今天发出** D2（产品 Owner，40 悬空引用分类）/ D4（数据 Owner，A-Box 权威确认）请求函，附 SIM 临时模拟权威声明草案；
5. WI-A4：命名空间 ADR 起草（**不预填根域**）；WI-A3：跟催标准文本（目标 2026-10-09）；
6. WI-A2：消费者全量扫描（复审包 09 号 S1~S5）——**它是 Wave 2/3 退出门禁，完不成后面全停**。

## 五、纪律红线（违反即 STOP 写 `loops/ONTO1-ontology-split/memory/BLOCKED.md`）

- 合同先行：先登记 CONTRACT_INDEX（独立 generated 目标）→ `make generate` → `make check` → 再实现；**禁手改 generated/**。
- 防假绿三件套：每个否定式门禁 = 单一真值函数 + fail-closed（缺夹具即失败）+ 变异复验（mutate→FAIL/restore→PASS），全量变异矩阵进 EVIDENCE。
- 五态验证：`PASS/FAIL/NOT_EVALUATED/DESIGN_ONLY/WAIVED_FOR_DEVELOPMENT`；**豁免永不满足激活门禁**；D2 未签前 CQ3 产品关系三场景硬阻塞。
- 证据：结论回源 `文件:行`；失败先记 `FAILURES.md` 再修；**禁 `git add .`**（`docs/dd/` 下有未跟踪文件）；双仓同窗口变更（先钉后切，旧值只读）。
- 索引纪律（TL 角色强制）：开工/收工声明 INDEX_FRESH/INDEX_STALE；回源结论落 `loops/ONTO1-ontology-split/memory/INDEX_BASIS.md`。
- 不越界：只做 ONTO1 scope；统一命名、种子本体对齐等 8 项后续工作不在本 Loop。

## 六、汇报

每 Wave 收工输出：`[收工] Loop: ONTO1-ontology-split, Gate: G<n>, Baton → <next>`，并更新 EVIDENCE.md/STATE.json/NEXT_SESSION.md。书面复审结论（DESIGN_APPROVED 或再退回）到达时，第一时间更新计划 §0 状态机位置并通知所有角色。
