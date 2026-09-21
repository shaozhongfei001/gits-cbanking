# PC0-product-center-baseline｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-20T16:10:00+00:00` |
| **holder** | `tech_lead` |
| **packet** | `PC0-product-center-baseline` |
| **wave** | `W2`（PC1 页面骨架，待 OD-PI-03 背书后启动正文实现） |
| **index_basis** | `memory/INDEX_BASIS.md`（TL/架构角色必填：`INDEX_FRESH` / `INDEX_STALE(n)` / `INDEX_ABSENT`） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、P38 任何改动、PC2（需 OD-PI-03 背书） |

## 已完成（PC0 全部设计任务）

- T0-2/T0-3：菜单「产品中心」+ 路由 + 骨架页 + 测试基线（vue-tsc 0 错 / vitest 344/344 / playwright 4/4）
- T0-4：`specs/product-center/product-center-api.openapi.json`（3.1.1，15 operation）+ `product-center-domain.schema.json`（18 对象）
- T0-5：`CTR-PKC-API-001` / `CTR-PKC-DOM-001` 已登记，`make generate` 产出独立 generated 目标
- T0-7/T0-8/T0-10：DEMO 隔离 / 错误码映射 / 权限决策点 / 搜索脱敏（`specs/product-center/README.md`）
- T0-11：`scripts/pkc_contract_tests.py`（fail-closed + 6/6 变异复验 PASS；FAIL-2026-09-20-01 已闭环）
- 门禁：`make generate` PASS · `make check` PASS（INCONCLUSIVE=gate-injection-tests 既有基线，不计为通过）· `make security-check` PASS
- T0-6 决策：12 张 `pk_*` 候选表落地推迟至 PC2（README §7）

## 下一会话任务

0. **OD-PI-12 已登记（Owner 2026-09-21 澄清）**：全目录升级（13 产品/6 族），非单产品演示。执行口径见 round-1 决策登记 OD-PI-12；PC1 目录必须渲染分类法全集，其余产品补齐前诚实显示完整度缺口
1. **OD-PI-03 背书**：向 Owner 提交 `specs/product-center/README.md` §9 映射表（7 态），背书前不进 PC2
2. **PC1**：三栏页面骨架（环境条 / 页内头部 / 左目录=13 产品 6 族 / 产品首屏 / 章节导航吸顶 / 1680-1440-1280 基线），数据源=PC0 合同的目录与详情端点实现（最小只读：families/products/detail）
3. PC1 交付物：三档宽度截图 + 目录切换不残留 + 高亮互斥证据 + 13 产品目录渲染证据 + Loop 记忆更新
4. 待 Owner 明确：KERT 侧 12 产品内容加工的批次顺序（建议按比较集倒逼：透支/流动资金贷款/订单融资 → 其余按族）

## Owner 决定（2026-09-21，登记于 `docs/architecture/ONTO1-SCENARIO-PI-Owner决定登记-V1.0.md`）

- **比较章节 = B 方案 + 造数授权**：A 本行产品间为主体、B 公开参考（脱敏非权威）、SIM 同业对照（造数，四条硬约束）。未豁免项 8 条（不得作字段权威/不进门禁/无机构名/不对客/…）。门禁负例 5 条已写入 `specs/product-center/README.md` §6.5，PC4 必测。
- **SIM 临时模拟权威：Owner 同意生效**（产品身份部分）⇒ 状态 `OWNER_APPROVED_PENDING_TECHNICAL_PRECONDITIONS`；**仍非 EFFECTIVE**，4 项技术前置（Schema 校验 / 正负夹具 / 来源时点版本校验 / 独立 QA）未完成。P1~P3 我方即可启动，**P4 需独立角色**。
- **仍未决**：40 条悬空产品引用分类（产品 Owner）；我方先出「按页面影响排序的待裁定清单」。

## 准入约束

- Owner 已确认路线 A（契约先行）；演示效果诉求已通过 PC1 排期回应
- P38 冻结；`git add` 只用显式路径；`make generate/check` 串行且跑后还原 `evidence/gk-ke-chain-trace/trace.json`
