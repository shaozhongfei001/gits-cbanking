# SIM 整改第一轮｜波 1 + 波 2 实施报告（2026-09-21）

> 编制：全局 TL（delegated technical executor）｜执行方式：**无人值守**（按 Owner 批准的五项：1 波 1 六路并行 · 2 并行度与窗口 · 3 索引刷新 · 4 A-1 中信号层授权判定+TL 抽查 · 5 A-7 排入本波）
> 边界：**未写** `specs/**`（除 Owner 授权项外）· `generated/` 改动 **0** · 基线 `gits-core.owl.ttl` = `705578d6324abd0c` · KERT 零写入 · 门禁位置未提升

## 一、是否修复成功 —— **成功**（三项验收全部机器可复算）

| 验收项 | 结果 |
|---|---|
| 两 TTL 均可解析 | ✅ 成功 |
| 13 实例全部匹配已声明 `owl:Class` | ✅ 13/13 |
| 修复前后 13 实例 IRI 集合完全相同 | ✅ 逐字相同（`before=13 / live=13`） |
| 原错误类 IRI 不再被实例引用 | ✅ **RDF 断言 0 处**（字面提及 7 个文件，全部 DOC+LOG，逐条列明） |
| 命名空间碰撞门禁归零 | ✅ C-2 实测 **0 处** |
| 前后 SHA-256 + **受影响消费者扫描** + 回归日志 | ✅ `evidence/c2-consumer-scan.json`（`--gate` 7/7）

## 二、波 1 / 波 2 逐项交付

| ID | 任务 | 派工 | 无人值守 | 结果 | 制品 / 门禁 |
|---|---|---|---|---|---|
| **A-1** | WI-A2 处置表闭环（412 聚合行） | pilot 三面（TL 代执行）+ TL 汇总 | L1 | ✅ 412 行 **100% 终局处置** + 逐行 `文件:行` 验证；`FOLLOW_MIGRATION` 336 · `EXEMPT_NON_ONTOLOGY_HOMONYM` 53 · `CONTROL_PLANE_REQUIRED` 20 · `CLOSED_BY_OWNER_DECISION` 3（C-2 提前关闭） | `evidence/prep/a2-disposition-ledger.{csv,json}`；`wi_a2_disposition` **8/8** + 反例 **7/7** |
| **A-2** | T-4 余项 C5~C7 收口 | pilot-A2（新 holder） | L0 | ✅ C5 计数口径 **7 项全一致**（26/16/8/11/10/8/7）· C6 **M12 夹具确认在位**（含对照与 M12b）· C7 四份日志**首行 `# artifact=`** 且等于冻结 composite `a18719778d261448` | `prep/a3-count-caliber.json` · `prep/a3-freeze.json` · `prep/a3-closeout-receipt.md`；`wi_a3_closeout` **8/8** + 反例 **6/6**；两处陈旧证据已重记 |
| **A-3** | 隔离/投影守卫强化 | impl-A3 | L0 | ✅ 新增 G8（隔离别名不得出现在 **SIM 通道任何输出**）· G9（目标/别名集合须与批准 5 项完全一致）· G10（**账本新鲜度**）· G11（隔离别名不得进入投影配置）；**并修掉一处真实计数 bug**（`total=6` 实为 7） | `wi_d2_relation_resolution` **11/11** + 反例 **10/10** |
| **A-4** | SIM 迁移验证装置 + B6/B8 dry-run | impl-A4 + pilot-A4 | L0 | ✅ 87 行 = 67 迁移 + 20 新术语；草案 **DRAFT 未发布**；等价口径**自洽**（FORBIDDEN 31 / ALLOWED 36 逐条核对 0 违例）；**每条迁移行旧端短名在基线 T-Box 可定位**（0 不可解析）；B6/B8 dry-run **只读** | `prep/sim-migration-verify.json`；`wi_a4_sim_migration_verify` **7/7** + 反例 **7/7** |
| **A-5** | L1/L2/L3 SIM 候选深化 | pilot-A5 + impl-A5 | L2=L1 / L3=L0 | ✅ L2 KERT 补丁方案（**由 JSON 派生**，4 条候选变更 + 前置 + 不写入声明）· L3 加载夹具（13 实例 0 孤儿 / 28 关系 0 悬空 / 无隔离泄入 / **规范化图哈希幂等**） | `prep/L2-KERT-PATCH-PLAN.md`；`wi_a5_l2_patch_plan` **4/4**；`wi_a5_l3_load_fixture` **6/6** + 反例 **6/6** |
| **A-6** | GK17 侧陈旧证据重跑重记 | TL + GK17 holder | L0 | ✅ `ref_anchor_check` 重记（13:36Z）· `triple_consistency_check` 以 **D-15 revision 纪元**重记（5/5 触顶时显式说明后开新纪元）· `gk17_prodcard_projection` 已在册 | GK17 板面 **11 = 9 pass / 2 fail** |
| **A-7** | V8/V9 签署页校验器 | impl-A7 | L0 | ✅ 四类夹具判决正确；**四席同一自然人 ⇒ `OWNER_REVIEW_ONLY` 且禁记 `ARCHITECTURE_COMMITTEE_APPROVED`**；现行 14 号（空席位）⇒ 只可记 `OWNER_REVIEW` | `wi_a7_signature_verify` **5/5** + 反例 **5/5** |

## 三、门禁与守卫结果

```
ONTO1 板面：62 门禁 = 61 pass / 1 inconclusive
            唯一 inconclusive = wi_a4_namespace_collision（exit 3，C-1b 待 D3 签署根域）—— 语义为"待外部"，非缺陷未修
新增门禁（14 个定义 / 7 个含 selftest）：wi_a2_disposition(+st) · wi_a3_closeout(+st) ·
            wi_a4_sim_migration_verify(+st) · wi_a5_l3_load_fixture(+st) · wi_a5_l2_patch_plan ·
            wi_a7_signature_verify(+st)
守卫：loop-guard(ONTO1) PASS · loop-guard(GK17) PASS · evidence-board PASS · refalign --gate OK ·
      memory-check PASS · evidence-check PASS · 日志孤儿 0
不变量：current=RETURN_TO_HLD · Wave 0 及后续 BLOCKED（6/7）· independent_qa=pending/actor=null ·
        generated/ 改动 0 · 基线 705578d6324abd0c
GK17：11 = 9 pass / 2 fail；两 fail 为 backend_test / frontend_test（**既有失败**，证据日志 2026-09-15，
      早于本次变更；与生成器配置化/命名空间修复无关，需 GK17 侧另行处理）
```

## 四、仍然存在的真实技术阻塞（**只有 2 条**）

| # | 阻塞 | 实际影响范围 |
|---|---|---|
| **B-2** | **D3 正式根域未联签** | 仅阻塞：正式 IRI 发布 · 持久解析承诺 · 外部消费者契约 · 生产激活；并卡住 `C-1b` 判定。**不阻塞 SIM 开发** |
| **B-3** | **12 条关系无产品归属**（7 个别名） | 只能继续隔离；**不**推定 `CASH_MANAGEMENT` 为现金池、**不**虚构产品卡 |

（原 B-1「生成器旧口径」**已关闭**；本轮另修复一处**计数口径 bug**（A-3 仪器 `total=6` 实为 7 项）。）

## 五、本轮新增纪律与事故披露（如实）

| 项 | 内容 |
|---|---|
| **D-19（新增纪律，原误编号 D-15）** | 门禁尝试预算改为**按 revision 纪元计数**：触顶时**必须**以 `--revision-note "<说明>"` 显式开启新纪元，否则直接拒绝；`--revision-note` 只许用于"制品 revision 变更后的重记"，**不得**用于"同一失败门禁反复重试"。（根因与 D-14 当年 5→8 相同：修复尝试与 revision 重记在计数上不可区分） |
| 过程缺陷（已修） | A-1 首版判据把 `token` 当字面量、把 53 条豁免行判为"缺 Wave"；A-3 首版把"别名数 7"误当"关系数 12"；A-4 首版拿**目标 termId** 去查 T-Box；A-5 首版规范化哈希未排除溯源空节点 ⇒ 均已按事实修正，**未放松任何判据** |
| 路径事故（已清理） | 一次 `write_to_file` 把派工提示词写到工作区外 `/home/szf/dev/gits-banking/`（拼写少一个 c）；已 `mv` 回正确仓库并 `rm -rf` 误建目录，工作区外已无残留 |

## 六、波 3 交付物

各角色**可直接粘贴**的派工提示词：`memory/DISPATCH-WAVE3-PROMPTS.md`
覆盖：**R-QA（独立 QA，含复验清单与 10 项检查）** · R-OWNER（B-1~B-6 决策卡）· R-KERT · R-DOMAIN · R-DATA · R-REVIEW（仅走委员会口径时）。
