# CR-2026-001 激活合同权威 schema 与其实例不一致

```
变更请求编号：CR-2026-001
提出人：KERT 侧施工（§5.5 ② 落地过程中发现；依据 docs/architecture/candidates/
        GITS-知识侧待接线清单-V1.0.md §5.5）
提出日期：2026-09-16
变更类型：☑ 一般（初判）  □ 重大  □ 轻微
          初判理由：涉及合同 CTR-ACTIVATION-001 与其 3 个消费者的数据一致性，
          但不改变架构边界、模块依赖方向与端口接口。分类请 CCB 按 §6.2 确认。
变更标题：AC-PREVISIT-001.json 携带权威 schema 未声明的 knowledgeItemIds，
          导致该实例不合自身合同
```

---

## 1. 变更描述

`specs/knowledge-architecture/schemas/activation-contract.schema.json`
（合同 `CTR-ACTIVATION-001`，`kind: json_schema`）声明了 **13 个属性且全部 required**，
并设置 **`additionalProperties: false`**。

但 `specs/knowledge-architecture/activations/AC-PREVISIT-001.json` 携带第 14 个字段
**`knowledgeItemIds`**（7 项：`KI-009`、`KI-FRONT-001` ~ `KI-FRONT-006`），
**该字段未在 schema 的 `properties` 中声明** ⇒ 该实例**不合自身合同**。

### 1.1 实测证据（可复现）

```
$ python3 - <<'PY'
import json, glob, jsonschema
sch = json.load(open('specs/knowledge-architecture/schemas/activation-contract.schema.json'))
for f in sorted(glob.glob('specs/knowledge-architecture/activations/AC-*.json')):
    doc = json.load(open(f)); errs = list(jsonschema.Draft202012Validator(sch).iter_errors(doc))
    print('INVALID' if errs else 'VALID ', f.split('/')[-1],
          '|', errs[0].message if errs else '')
PY

VALID   AC-FACT-RECONCILIATION-001.json |
INVALID AC-PREVISIT-001.json | Additional properties are not allowed
                               ('knowledgeItemIds' was unexpected)
VALID   AC-PRODUCT-RECOMMEND-001.json |
```

补充核实（排除误判为"schema 另有 allOf/$defs 追加声明"）：

- schema 顶层键仅 `['$schema','$id','title','type','additionalProperties','required','properties']`，
  **无 `allOf` / `$defs` / `patternProperties`**；
- `additionalProperties` 实测为 `False`；
- `properties` 实测 13 项：`schemaVersion, contractId, version, taskType, routeMode,
  preconditions, activations, semanticQueries, ruleChecks, skills, context, humanGates,
  failurePolicy`。

即：**不是校验器口径问题，是权威 schema 与权威实例之间的真实不一致。**

### 1.2 影响

| 侧 | 影响 |
|---|---|
| **KERT（消费侧）** | `domain/activation_contract.py`（§5.5 ② 新增）按权威**严格拒收**该字段 ⇒ `AC-PREVISIT-001.json` **无法入受治理副本**；§5.5 ① 目前只能落 **2 份**（`AC-FACT-RECONCILIATION-001`、`AC-PRODUCT-RECOMMEND-001`），`PRE_VISIT_PREPARATION` 任务在合同注册表上**默认拒绝**（fail-closed，不回落） |
| **GITS（权威侧）** | 合同 `CTR-ACTIVATION-001` 与其实例不自洽：凡以该 schema 做校验的环节（生成物 `generated/knowledge-architecture/activation-contract.schema.json` 亦然）都会把 AC-PREVISIT-001 判为非法 |
| **消费者** | `CONTRACT_INDEX.yaml:307-319` 登记消费者为 `activation_planner` / `skill_runtime` / `agent_orchestrator`，`compatibility: explicit_migration` |

> **说明**：KERT 侧的严格拒收**不是本变更的原因，而是发现手段**。
> KERT 曾评估"本地白名单接受该字段"，已被 Owner **2026-09-16 否决**
> （理由：违反 fail-closed 纪律，且会在跨仓权威之上另立一版口径）。
> 因此本不一致**必须在权威侧解决**。

---

## 2. 候选方案

### 方案 A（推荐）：在 schema 中**正式声明** `knowledgeItemIds`

- 动作：`activation-contract.schema.json` 的 `properties` 增加
  `knowledgeItemIds`（`type: array`, `items: {type: string}`），并纳入 `required`
  或明确列为可选；同步决定 `generated/` 生成物 与 `CONTRACT_INDEX.yaml` 的兼容性标注。
- 理由：该字段在**权威实例中真实存在且语义明确**（KI 条目引用），
  视为"遗漏声明"比视为"脏数据"更符合既成事实；且 `AC-PREVISIT-001` 是访前场景的
  主合同，其 KI 引用面不可能靠删字段表达。
- 风险：等同于**扩展** `CTR-ACTIVATION-001`（新增可选属性属向后兼容扩张，
  但需确认 3 个消费者是否应消费该字段——尤其 `activation_planner` 是否应把它
  当作激活面的一部分，否则会出现"契约给了、规划器不看"的新缺口）。

### 方案 B：从 `AC-PREVISIT-001.json` 中**移除** `knowledgeItemIds`

- 动作：删除该字段（7 项 KI 引用的语义若仍需要，须另行落到其它**已声明**字段，
  例如并入 `activations` 的资产引用或 `semanticQueries`）。
- 理由：保持 schema 不变，改动面最小。
- 风险：**语义丢失**。7 项 KI 是访前报告的取材面，删掉若无替代落点，
  等价于静默削减该任务的激活面——与 KERT 侧 P1 一致性核对
  （`tests/integration/test_control_plane_consistency.py`）所防的缺陷同类。

### 方案 C（**已否决**）：KERT 侧放宽

- 由消费侧把 `knowledgeItemIds` 列入"已知扩展"白名单接受。
- **否决理由**：会让"权威"出现两版口径（GITS 说非法、KERT 说合法），
  且与 KERT 模块纪律"未知字段一律拒绝（不静默忽略）"直接冲突。Owner 已裁定。

---

## 3. 影响分析（IA-CR-2026-001）

```
影响分析报告编号：IA-CR-2026-001
对应变更请求：CR-2026-001
分析人：KERT 侧施工（待技术代表复核）
分析日期：2026-09-16

1. 架构影响评估
   - 是否违反六边形架构原则：否
   - 是否改变模块依赖关系：否（方案 A/B 均不改依赖方向）
   - 是否影响端口接口定义：否（不影响 Java Port 签名）
   - 详细说明：仅涉及 JS 契约（json_schema）与其数据实例的自洽性。

2. 合同影响评估
   - 受影响合同列表：CTR-ACTIVATION-001（authority_source =
     specs/knowledge-architecture/schemas/activation-contract.schema.json）
   - 向后兼容性：方案 A ＝ 兼容（新增属性）；方案 B ＝ 数据面变更（explicit_migration）
   - 详细说明：方案 A 须同步 generated/ 生成物与 CONTRACT_INDEX.yaml；
     方案 B 须评估 activation_planner / skill_runtime / agent_orchestrator 的读取行为。

3. 数据影响评估
   - Schema 变更：方案 A 有（附 diff）；方案 B 无
   - 数据迁移需求：方案 A 无；方案 B 有（AC-PREVISIT-001.json 内容变更 ⇒
     KERT 侧对账基准 sha256 须重算，见下）
   - 详细说明：变更落地会**改变 AC-PREVISIT-001.json 的字节哈希**，
     KERT 侧 §5.5 ① 的对账基准必须重新计算后再落副本。

4. 测试影响评估
   - 回归测试范围：GITS 侧以该 schema 校验的用例；KERT 侧
     tests/unit/test_activation_contract.py（已知缺口用例须随之改写）
   - 新增测试用例估算：1~2（AC-PREVISIT-001 恢复为合法实例的用例）
   - 详细说明：KERT 侧"权威缺口"用例本身即本变更的**验收哨兵**——
     变更未落地时它必须红/必须拒收，落地后应改为断言接受。

5. 进度与资源影响
   - 估算工作量：方案 A 约 0.5 人天（含 generated 与索引同步）；方案 B 约 1 人天
     （含消费者影响评估）
   - 对迭代计划的影响：不阻塞其它施工；仅阻塞 §5.5 ① 的第 3 份副本

6. 风险评估
   - 风险等级：低
   - 风险描述及缓解措施：主要风险是"改了 schema 但消费者不消费该字段"形成新缺口
     （方案 A）；缓解方式是在 CCB 评审时同步确认 activation_planner 的读取口径。

7. 结论
   - 建议处理方式：☑ 批准（倾向方案 A）
   - 理由：以权威 schema 补齐"既成事实的字段声明"成本最低、无语义丢失；
     方案 B 存在静默削减激活面的实质风险。
```

---

## 4. 替代方案与回退

- **替代方案（不修改基线）**：KERT 侧放宽白名单 —— **已否决**（见 §2 方案 C）。
  除此之外无"不改基线又能恢复自洽"的方案：实例与 schema 的矛盾必须有一侧让步。
- **回退方案**：方案 A 实施后如需回退，撤销 `properties` 中的 `knowledgeItemIds`
  声明并同步 `generated/` 与 `CONTRACT_INDEX.yaml` 即可；数据文件未动，回退无残留。

---

## 5. 实施要求（按 CHANGE-CONTROL-PROCESS §7.1）

变更获批后须同步更新：

| 项 | 路径 |
|---|---|
| 权威 schema | `specs/knowledge-architecture/schemas/activation-contract.schema.json` |
| 生成物 | `generated/knowledge-architecture/activation-contract.schema.json` |
| 合同索引 | `specs/CONTRACT_INDEX.yaml`（`CTR-ACTIVATION-001` 条目，必要时调整 `compatibility`） |

> 本变更**不得**由消费侧（KERT）实施：KERT 仓不修改 `specs/` 权威源、
> 不手工编辑 `generated/`（§5.5 施工单纪律）。

---

## 6. 提交与审批

- 提交渠道：CCB 主席（或指定代理人）；提交截止：CCB 例会前 3 个工作日
- 审批路径：变更请求 → 影响分析（本 §3 可作初稿）→ CCB 评审 → 批准/拒绝 → 实施 → 验证
- 当前状态：**初判为「一般变更」，等待 CCB 评审**
