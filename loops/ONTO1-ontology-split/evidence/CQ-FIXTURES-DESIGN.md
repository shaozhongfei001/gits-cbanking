# ONTO1 WI-A6｜六类 CQ 夹具设计（机读夹具说明）

| 项 | 值 |
|---|---|
| 来源 | 复审包 `08-CQ语义验收矩阵.md`；五态模型见 `06-验证状态模型与状态跃迁表.md` |
| 机读产出 | `evidence/cq-fixtures/CQ1.json` … `CQ6.json`（schema `onto1_cq_fixture/v1`） |
| 生成/校验 | `python3 scripts/onto1_cq_fixtures.py --gate` / `--selftest` |
| 执行时机 | **Wave 4**（本次只做设计基线；执行需实现存在） |
| 门禁 | `wi_a6_cq_fixtures` / `wi_a6_cq_fixtures_selftest`（均 PASS） |

## 1. 夹具结构（每 CQ 必备六要素）

| 字段 | 含义 | 缺失后果 |
|---|---|---|
| `query` | 查询形态（SPARQL / 图查询 / API 调用） | 门禁 Q2 FAIL |
| `positive` | 正例（必须可执行、可判真） | 门禁 Q2 FAIL |
| `negative` | **否定式断言**（fail-closed 具名拒绝） | 门禁 Q2/Q5 FAIL |
| `expected` | 预期结果（含具名错误码） | 门禁 Q2 FAIL |
| `mutation` | 变异用例（改一处 ⇒ 必须 FAIL） | 门禁 Q2/Q5 FAIL |
| `owner` | 责任 Owner | 门禁 Q2 FAIL |

## 2. 六 CQ 现状（本轮）

| CQ | 验证对象 | 层 | 责任 Owner | 本轮状态 | 外部阻塞 |
|---|---|---|---|---|---|
| CQ1 | `CustomerRole` + `SourceIdentifier` | L1 | 公共语义 Owner（**待任命**） | `NOT_EVALUATED` | **D4** |
| CQ2 | `GroupMembership`（有效期 + 来源） | L1 | 公共语义 Owner（**待任命**） | `NOT_EVALUATED` | **D4** |
| CQ3 | `describesProduct` + `ProductKnowledgeVersion` | L1/L2 | Knowledge Owner（KERT 维护方） | `NOT_EVALUATED` | **D2（硬阻塞）** |
| CQ4 | ActivationPlan planHash + 版本子块 | L3/L4 | Integration Contract Owner（**待任命**） | `DESIGN_ONLY` | — |
| CQ5 | `CapabilityPublication` 四态可区分 | L4 | Integration Contract Owner（**待任命**） | `DESIGN_ONLY` | — |
| CQ6 | `Action`/`Receipt`/`HumanConfirmation` + 复算 | L3 | GITS Owner | `DESIGN_ONLY` | — |

**纪律**：
- 设计阶段**任何 CQ 不得为 `PASS`**（门禁 Q3 硬拦）；`PASS` 只能由**独立 QA** 在执行后记录；
- `NOT_EVALUATED` 与 `DESIGN_ONLY` **均不满足激活门禁**（设计 §6.1、复审包 06 号 §3）；
- CQ3 的三场景（产品关系）在 D2 未签前**不得**以豁免替代。

## 3. 防空转设计（为什么这些夹具不会"假绿"）

1. 每个 CQ 强制具备 `negative` + `mutation` ⇒ 只测正例无法通过门禁；
2. 变异语义明确到"改哪一处、期望何种失败"（如"删除 `SourceIdentifier.sourceSystem` ⇒ 必须 FAIL"）；
3. 门禁自检（`--selftest`）证明：把 CQ3 标成 `PASS` 会被 Q3/Q4 同时拦下，删除变异断言会被 Q2/Q5 拦下，删除夹具文件会被 Q1 拦下；
4. 执行阶段还须记录**实际目标数 > 0**（无实例 ⇒ `NOT_EVALUATED`，不得以"0 目标 0 违规"充当通过）。

## 4. 执行阶段还需补的（不在本轮）

- 每个 CQ 的**可执行夹具文件**（SPARQL/.rq、JSON 请求/响应、Python 断言）；
- 正/负/变异命中数统计与目标数断言；
- 六 CQ 接入 `make conformance`（内部规则名义，**禁用 CONFORMANCE / 国标符合性字样**）；
- 独立 QA 复核记录（禁开发自签）。
