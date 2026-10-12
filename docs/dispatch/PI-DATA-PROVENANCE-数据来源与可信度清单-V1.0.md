# PI 数据来源与可信度清单 V1.0

> 触发：Owner 指出「这里所有数据都是模拟的」，要求停止用演示值论证业务价值。
> 本文件是**强制前置**：此后任何汇报、设计评审、验收说明，凡引用数据，必须带本清单的行号；
> **演示（DEMO）值禁止进入业务论证**。

```text
生成时间：2026-09-22
生成人：tech_lead
适用范围：gits-cbanking / Leibniz-KERT 两仓中，与「对公产品中心 / 产品解读」相关的全部数据
状态：IN_FORCE（立即生效）
```

## 1. 强制规则

| 编号 | 规则 |
|---|---|
| `DP-01` | 引用任何产品数据，必须标注本清单行号 + 数据可信级别 |
| `DP-02` | 可信级别为 `DEMO_SIMULATED` / `PLACEHOLDER` 的数据，**只能**用于说明系统结构与渲染行为，**不得**用于论证业务价值、业务规则、业务口径 |
| `DP-03` | 任何"业务优劣 / 业务高明"结论，只能基于**设计推理**（目标用户、待办任务、失败模式、成本），不得基于上述数据值 |
| `DP-04` | 页面与接口中，`DEMO_SIMULATED` 数据必须常驻标识，且不得呈现为「已核验口径」 |
| `DP-05` | `DEMO_SIMULATED` 数据欲进入生产正式版本 → 发布流程必须阻断（需求 03 §8） |
| `DP-06` | 如需真实业务口径，须由业务侧提供制度/价目/协议原文（真实或脱敏），并单独登记来源 |

## 2. 清单

| # | 数据 | 路径 | 引入 commit | 日期 | 自述可信级别 | 可否用于业务论证 |
|---|---|---|---|---|---|---|
| D-1 | 13 张产品卡（含法人账户透支 `PROD-CM-003`） | `Leibniz-KERT/examples/product-recommendation-assets/03_core/*/product-cards/PROD-*.md` | `a237ce7`→`699106b` | 2026-09-01 / 09-13 | `CANDIDATE`（MANIFEST §4：全部资产 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO）；`01_raw/_authoritative/` 为空；27 源全部 `PENDING_SOURCE`；`content_hash` 为占位假值（如 `sha256:cm001hash`） | **否**（仅可说明系统现状） |
| D-2 | 解读投影 `interpretation/PROD-CM-001.json` | 同上 `04_serve/interpretation/` | `5f3a2b8` | 2026-09-06/07 | `provenanceState = DEMO`；`lifecycleState = PUBLISHED`（仅表示发布流程状态，不代表内容真实） | **否** |
| D-3 | Release 记录 `RLS-2026.09.06.1.json` | 同上 `04_serve/releases/` | `5f3a2b8` | 2026-09-06/07 | 同上（含 `gateReport` / `ownerDecisionIds`，属流程证据，非业务口径证据） | **否** |
| D-4 | 产品分类基线 `product-taxonomy.yaml` | `gits-cbanking/specs/product-knowledge/` | `e7abd7b` | 2026-09-10 | 自述 `CANDIDATE / FROZEN=NO / IMPLEMENTED=NO`；文件内 D-1~D-4 已知差异登记 | **否**（结构可引用，族名/规模可引用为"当前基线"） |
| D-5 | 产品知识版本种子 `V021__corporate_product_knowledge_seed.sql` | `gits-cbanking/adapters/persistence-relational/.../db/migration/h2/` | `1bd4363` | 2026-09-14 | 文件自述：**"本表为产品知识版本元数据，非产品卡权威源"** | **否** |
| D-6 | 情景种子（客户 `CUST-CORP-0001` 等） | `gits-cbanking/scenario/seed/` | 历史提交 | ≤ 2026-09-14 | KERT 侧 commit 明示 `simulated customer` | **否** |
| D-7 | PC1/PC1.5 代码、测试、Loop 文档 | `gits-cbanking`（`apps/api/.../productcenter/`、`frontend/src/components/product-center/`、`loops/PC1-*`） | `7098022`、`4f22c85` | 2026-09-22 | 代码与测试夹具（无业务数据） | **不适用**（不含业务数据） |

**注意**：单测文件中的 `TAXONOMY` 常量、`PROD-CM-*` 等属**测试夹具**（`apps/api/src/test/...`），是为验证程序行为构造的，与 D-1~D-6 无关，同样不得作为业务依据。

## 3. 由此得出的结论

1. **当前两仓内不存在可用于业务论证的真实产品口径数据。** 任何"业务上更优/更差"的判断，只能来自设计推理。
2. 因此「对公产品中心」模块可验证的价值只有**机制层**：能表达"未核验"、不可承诺边界、可追溯链、缺口清单、DEMO 隔离与生产阻断。
3. 要让页面呈现"已核验"的真实口径，必须先有 D-01 规则下的真实来源（制度/价目/协议原文）。

## 4. 已落实的界面处置（PC1.5+）

| 位置 | 处置 |
|---|---|
| 环境条 | `DEMO · 演示数据` 常驻标识 |
| 首屏 / 章节 | 缺失字段一律显示「待核验」，不填推测值 |
| 知识治理栏 | 新增「数据来源声明」：环境 + 演示数据不代表真实银行制度/价目/协议 + 禁止对客引用 + 生产发布应阻断 |
| 原始材料区 | 警示升级为「模拟（DEMO）数据，非真实银行规则」，并登记 D-1 的可信度事实 |
