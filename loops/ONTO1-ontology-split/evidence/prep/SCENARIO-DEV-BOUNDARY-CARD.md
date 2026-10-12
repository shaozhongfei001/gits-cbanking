# 业务场景开发｜边界卡 + 就绪清单

> 编制：全局 TL｜依据：Owner 2026-09-21 决议（**开发与正式批准分开**）；执行状态 `OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION`

## 1. 结论

**可以开发业务场景**（SIM 环境）。开发/联调/自动化测试/迁移验证**不再等**签署页或委员会。

## 2. 五条不能碰

| # | 禁令 | 说明 |
|---|---|---|
| 1 | **不接生产数据、不写回生产** | 仿真/seed 数据可以 |
| 2 | **不发布新 IRI** | 用 `PROVISIONAL_SIM_LEGACY_NAMESPACE`（D3 未签） |
| 3 | **不声称委员会批准 / 正式基线生效** | 板面仍有 1 项 inconclusive（`C-1b` 待 D3） |
| 4 | **不把候选资产标 `ACTIVE`** | L1 候选 8 类等保持候选 |
| 5 | **不手改 `generated/`、不写 KERT** | 前者随 `make generate`；KERT 写权限未定 |

## 3. 实测：你的场景资产会撞到什么

- 写死本体 IRI 字面量的文件：**2** 个
  - `apps/api/src/main/resources/claim-reconciliation.dmn`（1 处）
  - `apps/api/src/test/java/com/gien/gits/api/e2e/MechanismE2eIT.java`（3 处）
- 未裁定断点术语的引用（**延用现行名，别预改名**）：
  - `Customer`：73 个文件
  - `GroupRelationship`：3 个文件
  - `Product`：16 个文件
  - `KnowledgeMap`：1 个文件
  - `Skill`：81 个文件
- 隔离别名出现（**不得自行映射**）：
  - `CASH_MANAGEMENT`：3 个文件 → 见 `SCENARIO-QUARANTINE-HITS.md`
- 已批准别名引用：**0** 个（0 = 场景当前不依赖 D2 已解析关系 ⇒ 产品关系不阻塞场景）

## 4. 就绪底座（现在就能用）

- **13 个产品实例**（跨境人民币结算 / 内保外贷 / 现金池 / 资金归集 / 法人账户透支 / 流动资金贷款 / 应收账款质押融资 / 订单融资 / 并购贷款 / 单位结算账户 / 国内保理 / 银行承兑汇票 / 国内信用证）
- **28 条已批准产品关系**（SIM 通道投影，含溯源）
- **场景数据包**：`scenario/seed`（客户经理持续经营场景 V1.1）· `scenario/execute` 模块 · 既有 e2e：`EngagementScenarioE2eIT` / `V11ScenarioDataLoaderTest` / `ScenarioDataProviderTest`
- **迁移影响查询**：`evidence/prep/migration-worklist.csv`（462 行）

## 5. 开工前建议（最省返工）

**别在场景里硬编码术语名/IRI**，把『术语 → IRI/类别』收敛到一个**解析层**（配置 + 解析函数）。
理由：已批准的 28 条关系就是这么做的（版本化配置），实测『迁移只改配置、不动业务代码』。
你现在的改造面很小：**2 个文件**写入 IRI 字面量（沙箱预演见 `scenario-term-layer-rehearsal.diff`）。

> 本卡数字**全部由实测得出**（`scripts/onto1_scenario_readiness.py`），可复算。

