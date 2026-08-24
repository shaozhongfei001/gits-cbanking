# P24-DKWS-Platform 缺陷与修复记录

## FAIL-2026-08-20-P24-01：CLI 独立运行时 schema 未注册

- 现象：通过 `python -m dkws` 跑 `ingest` 报 `未注册的合同 schema 值: manifest/v1`；
  直接 import `dkws.schemas` 的测试却通过。
- 根因：schema 注册只在 `dkws.schemas` 被显式 import 时触发；CLI 入口未 import。
- 修复：在 `dkws/__init__.py` 顶部 `from . import schemas` 触发注册（幂等）。
- 验证：CLI 端到端链路冒烟通过；44 项测试全绿。

## FAIL-2026-08-20-P24-02：knowledge.candidate 关系引用不存在的目标实体

- 现象：CLI 派发 `knowledge.candidate` 后，`register_relation_candidate` 抛
  `关系引用的实体候选不存在`。
- 根因：仅注册了 source 实体 `{domain}-corp`，未注册 target 实体 `{domain}-asset`。
- 修复：先注册 source 与 target 实体，再注册关系（遵守引用完整性）。
- 验证：CLI 冒烟通过。

## FAIL-2026-08-20-P24-03：`_cmp` 将比较运算符表误记为值

- 现象：`service.rule` 的 `gte` 求值恒 False；e2e 中 `net_worth>=1000000` 命中失败。
- 根因：`{"gt": a > b, ...}` 在取字典时已先求值为 bool，再对其 `(...)` 调用。
- 修复：改为 lambda 比较器表。
- 验证：`TestRuleExec` 通过。

## FAIL-2026-08-20-P24-04：dataclass `field(default_factory=list)` 覆盖已定义字段默认

- 现象：`RealLlm.last_calls()` 返回的 `_calls` 是 `dataclasses.Field` 对象而非 list。
- 根因：`_calls: list[LlmCall] = field(default_factory=list)` 在 `__init__` 场景被 `field()` 占位覆盖。
- 修复：改为 `self._calls: list[LlmCall] = []` 直接初始化。
- 验证：真实 DeepSeek 连通测试后 `last_calls()` 返回 token/延迟记录。

## FAIL-2026-08-20-P24-05：真实 LLM `items` 重复 / 未回填数据

- 现象：`--llm real` 时产品 items 出现 PROD-WCL/PROD-FAL 重复；且缺失必备资产被误报。
- 根因：模型返回 items 与 DKWS 回填 names 叠加未去重；`_is_names_overlap` 用并集逻辑不彻底。
- 修复：改为 `_dedupe` 保序去重（模型要点在前、DKWS 数据补全），并补齐未经 LLM 提供的资产回填。
- 验证：真实 DeepSeek `status: READY` 无重复；`tests/test_previsit_report.py::TestRealLlmComposeNormalization` 通过。

## FAIL-2026-08-20-P24-06：CSV 含 BOM 时 `csv.DictReader` 首列 key 带 `\ufeff`

- 现象：图谱 CSV 接入 `row["entity_id"]` 抛 KeyError。
- 根因：`DictReader` 不剥离 BOM，首列 key 变 `\ufeffentity_id`。
- 修复：统一 `_csv_rows()`（demo）与测试逐行 `removeprefix("\ufeff")`。
- 验证：`tests/test_graph.py`（with_bom=True）通过。

## FAIL-2026-08-20-P24-07：生成产物"只有文件头"（内容占位缺陷）

- 现象：人工演练发现 `03_core`/`02_work/C` 产物正文大量是模板占位
  （`候选实体`/`待审核`/`-`/`无。`），数据只堆在 `---` frontmatter；`04_serve` 投影缺失（0 文件）。
- 根因：
  1. `knowledge.py::_candidate_body` 为硬编码占位正文，未按 values 渲染真实语义；
  2. `demo_rm_data_access.py` 客户接入只采 name/tier，未把原文属性（行业/地区/注册资本/产品线）落下；
  3. 发布/演示流程未自动构建 `04_serve` 投影。
- 修复：
  1. `_candidate_body` 重写为按 `values` 动态渲染（描述/证据/规范表达/审核说明含真数据）；`_rewrite_candidate` 审核后重新渲染正文；
  2. `register_entity_candidate` 增 `attributes`/`description` 参数，demo 把 customer_master.json 完整属性落入；
  3. `demo_rm_data_access.py` 增第 2.5 步自动构建投影 → `04_serve/.../entities|relations|statements.csv + PROJECTION.md + CURRENT.md`。
- 验证：重新生成工作区，`ENT-CUST-001.md` 含完整 attributes 与真实合作摘要正文；`04_serve` 投影含数据行（非空表头）；54 项测试全绿。

## FAIL-2026-08-21-P24-08：KE frontmatter 布局导致供应链数据永远为空

- 现象：`GET /knowledge/items/KI-FRONT-001` 返回 `[]`；供应链图谱数据取不到。
- 根因：KE 文件原为"纯 `{json}` + 正文"，`FailClosedJsonReader.extract` 修剪后以 `{` 开头则
  返回整个文件内容，Jackson 解析整 .md 失败 → fail-closed 返回空；另含 `demo: true` 未知字段，
  `FAIL_ON_UNKNOWN_PROPERTIES=true` 也导致反序列化失败。
- 修复：KE 改标准 `---{json}---` frontmatter 块；移除 `demo` 字段。
- 验证：重启后 `GET /knowledge/items/KI-FRONT-001` 返回真实 KE（上游/下游/位置解读）。

## FAIL-2026-08-21-P24-09：agent-browser 无法点击 Naive UI 按钮

- 现象：真实浏览器自动化中 `agent-browser click [ref=]/button/text=` 对 Naive UI SPA 全部定位失败。
- 根因：agent-browser 对 Vue/Naive UI 动态渲染组件的可点击 a11y 与 DOM 绑定分离，选择器失配。
- 处置：不改前端代码（非系统缺陷）；真实操作证据改用**真实 HTTP API 链路** + 前端 `vue-tsc` +
  HMR 生效 + 渲染快照。
- 记录：手动验证路径 `http://localhost:5173/engagement` → 选客户 → 一键访前准备。

## FAIL-2026-08-21-P24-IQA-01：MISSING_EVIDENCE_BOARD（独立 QA 拒绝 attest）

- 分类：`MISSING_EVIDENCE_BOARD`
- 角色：`independent_qa`（非 feature_pilot / 非 tech_lead）
- 现象：STATE 声称 `ready_for_independent_qa` 且 P0–P9 `DEV_SELF_CHECK_PASS`；独立 QA 离线 unittest **54 passed**，但 `scripts/qa_attest.py` 无法记录 `QA_PASS`。
- 根因：实现侧证据板不完整，`loop_guard --evidence-only` 失败：
  - 缺失 `EVIDENCE.json`（无 per-gate actor/role/timestamp/evidence_file/output_sha256）
  - 缺失 `HANDOFF.md`
  - 另缺 loop_guard 共享记忆：`SHARED_MEMORY.md`、`memory/PROTOCOL.md`、`memory/ORCHESTRATOR.md`
  - `STATE.json.baseline_commit` 为 `null`（非 40 位 Git SHA）
  - `memory/ROLE_BOARD.yaml` 非 loop_guard 所需 JSON（缺 `baton.holder`）
  - `memory/NEXT_SESSION.md` 无 `| **holder** | \`actor\` |` 表行
  - `loops/P24-dkws-platform/evidence/` 在独立 QA 开场时不存在（无实现 gate 日志可哈希）
- 处置：独立 QA **拒绝**记录 `QA_PASS`；**未**伪造实现 gate 哈希；**未**自签为 feature_pilot。Baton 交回 `feature_pilot` 补齐机器可校验证据板后再提请独立 QA。
- 功能结论：平台 unittest 绿（非功能失败）。阻塞原因为证据/记忆板，非测试失败。
- 证据：`loops/P24-dkws-platform/evidence/independent_qa_20260821T094459Z.log`
  sha256=`f0920c24f717e9e92be31791dd8f5327dfe9d467d8aa28746ee8aa8f2d0efb94`

## FAIL-2026-08-21-P24-IQA-01 修复记录｜feature_pilot

- **fix_time**: `2026-08-21T11:41:00Z`
- **actor**: `feature_pilot`（implementation；未自签 QA_PASS）
- **root_cause**: 实现侧从未写入机器可校验的 `EVIDENCE.json` 与 loop_guard 共享记忆；LOOP 门禁 command 为叙述句，无法被 `record_gate.py` 执行。
- **change**:
  1. 将 LOOP.yaml 十个 gate 的 command 改为 `scenario/dkws-platform` 下可执行 unittest/CLI（不关扫描器语义；不调用 `--llm real`）。
  2. 用 `scripts/record_gate.py` 逐门实跑并写入 `EVIDENCE.json` 真实 `output_sha256`。
  3. 补齐 `HANDOFF.md`、`SHARED_MEMORY.md`、`memory/PROTOCOL.md`、`memory/ORCHESTRATOR.md`、`memory/waves/W0-ITER.md`。
  4. `STATE.baseline_commit` 设为 `2e1118d251ff065d3793e6d771d28a306dd5a1af`。
- **rerun_result**: P0–P9 十个 gate EXIT=0；未把独立 QA 旧日志哈希填到实现门。
- **next_action**: `ready_for_independent_qa`，baton → `independent_qa`。

## 说明

本 Loop 由 Feature Pilot 记录 `DEV_SELF_CHECK_PASS`；`QA_PASS` 仅由独立 QA 记录。
独立 QA（2026-08-21）功能复核通过但 **未** 记录 `QA_PASS`（见 FAIL-2026-08-21-P24-IQA-01）。