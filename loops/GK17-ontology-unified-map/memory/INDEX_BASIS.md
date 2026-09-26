
# GK17-ontology-unified-map｜索引依据（代码事实索引与检索底座）

> 流程依据：`docs/governance/CODE-FACT-INDEX-PROCESS.md`（GOV-CFI-001）
> 约束：索引是 **DERIVED 派生视图**，只给线索；下表"回源结论"必须带 `文件:行` 才可被引用。
> 本台账由 `tech_lead` 于 W0 追加；**新增文件，非单写者路径**，不覆盖任何既有记录。

| 项 | 值 |
|---|---|
| **索引版本** | `.ua/merge-meta.json` @ 2026-09-15T06:37:38Z（gits `a1e183bb` + KERT `c49ddb5f`） |
| **新鲜度声明** | `INDEX_FRESH`（两仓 drift = 0；`make index-status` = PASS，`STRICT=1` 亦 PASS） |
| **门禁** | `make index-status` → `PASS`；`make index-gate-tests` → 18/18 OK |
| **本轮交付** | `docs/dispatch/GK17-W0-打穿设计与合同变更影响面-V1.0.md`（`GK17-TL-DRILLTHROUGH-001`） |

## 候选影响面（来自索引 L0/L1/L2，**未回源前不得作为事实**）

| # | 候选对象（模块 / 文件 / 类） | 索引来源 | 回源结论（`文件:行`） | 判定 |
|---|---|---|---|---|
| 1 | 知识地图与激活编排（37 nodes） | `layer:gits-cbanking｜知识地图与激活编排` | `KnowledgeMap.java:12-26` 无 nodes/edges；`DefaultActivationPlanner.java:153-157` 地图 loadRoot deny-if-missing | 受影响 |
| 2 | 语义层运行时（14 nodes） | `layer:gits-cbanking｜语义层运行时` | `FailClosedSemanticQueryGuard.java:62,76-78` 放行为占位；`RegisteredSemanticQueryCatalog.java:14-25` 硬编码 9 个 SQ-ID | 受影响 |
| 3 | 语义层实现（Jena）（6 nodes） | `layer:gits-cbanking｜语义层实现（Jena）` | `KnowledgeArchitectureConfig.java:167-174` 仅装配**单文件 T-Box**；A-Box 零引用 | 受影响 |
| 4 | 本体权威源（OWL）（2 nodes） | `layer:...｜本体权威源（OWL）` | `specs/semantic/gits-core.owl.ttl` 实测 32/34/1/**0 个体** | 受影响 |
| 5 | 知识架构契约与实例（169 nodes） | `layer:...｜知识架构契约与实例` | 两套 `KnowledgeMap` 合同字段交集仅 3 个（见 dispatch §2 F-11） | 受影响 |
| 6 | 前端知识地图视图 | 索引**未覆盖**（`.vue` 未抽取） | 回源：`frontend/src/api/engagement.ts:651`、`frontend/src/api/knowledge.ts` | 待评估（W7） |

## 索引未覆盖、必须回源的盲区（本轮实际踩到的）

| # | 问题 | 索引为何答不了 | 回源位置（`文件:行`） |
|---|---|---|---|
| 1 | 谁构造了 `SemanticQueryPort`？ | 无函数级调用边（只有文件级 `imports`） | 全仓 grep 排除 test ⇒ **零命中**（生产零装配） |
| 2 | 两套 `KnowledgeMap` 合同的字段差异？ | `specs/` 只做文件级摘要，不做字段级解析 | `specs/knowledge-architecture/schemas/knowledge-map.schema.json` vs `generated/gk-ke/v1/KnowledgeMap.schema.json` |
| 3 | `products.ttl` 是否被代码加载？ | 跨文件引用关系不在边类型内 | `grep -rn "products.ttl" --exclude-dir=.git .` ⇒ 仅 docs/loops 命中 |
| 4 | A-Box 个体数？ | 索引不解析 Turtle 内容 | `specs/knowledge-architecture/instances/product/products.ttl` ⇒ 13 个 `gits:Product` |
| 5 | 前端影响面？ | `.vue` 结构未抽取 | `frontend/src/api/knowledge.ts`、`views/KnowledgeMapView.vue` |

## 本批次新增的可复用结论（供下一 holder 免于重复通读源码）

| # | 结论 | 出处（`文件:行`） | 落地位置 |
|---|---|---|---|
| 1 | 本体已真实进入路由：fail-closed 前置 + 内容版本进 `planHash` + `trace.ontologyEvidence` | `DefaultActivationPlanner.java:115-119,176,188,199-200` | 本台账（W2 成果，勿重复验证） |
| 2 | 语义查询 ID 三方当前恰好一致（9=9），但**零门禁** | `RegisteredSemanticQueryCatalog.java:14-25` + `specs/knowledge-architecture/{activations,skills}/*.json` | dispatch §D3 → 建议 W5 增补 WP5.3 |
| 3 | 语义查询执行在生产**零装配**；守卫放行为占位 | `FailClosedSemanticQueryGuard.java:62,76-78`；全仓构造点 grep 空 | dispatch §D1 → R-1 |
| 4 | A-Box（13 个体）未被任何装配加载；装配为单文件 T-Box | `KnowledgeArchitectureConfig.java:167-174` | dispatch §D2 → R-2（建议 W6 前置） |
| 5 | `mapPort` 注入但零使用；"知识地图"在 API 层有三个所指 | `KnowledgeMapController.java:32-36,58-59`、`CustomerContextController.java:83` | dispatch §D5 → R-5 |
| 6 | 图侧 `SIM-GQRY-*` 与语义侧 `SQ-*` 两套命名空间、零映射 | `specs/knowledge-architecture/graph/bounded_queries.json` | dispatch §D6 → R-3 |

## 检索配方（本轮实测可用，供后续 holder 直接复用）

```bash
# L0 模块级
python3 -c "import json;g=json.load(open('.ua/knowledge-graph.json'));[print(l['name'],len(l['nodeIds'])) for l in g['layers'] if any(k in l['name'] for k in ('知识','语义','本体','地图'))]"
# L1 归属
python3 -c "import json,sys;k=sys.argv[1];g=json.load(open('.ua/knowledge-graph.json'));[print(n.get('type'),n.get('filePath')) for n in g['nodes'] if k.lower() in (n.get('name','')+n.get('filePath','')).lower()]" OntologyPort
# L2 依赖方向（注意：只有 imports/contains/exports，无函数级调用边）
python3 -c "import json,sys;k=sys.argv[1];g=json.load(open('.ua/knowledge-graph.json'));[print(e['type'],e['source'],'->',e['target']) for e in g['edges'] if k in e['source'] or k in e['target']]" semantic-runtime
# 收工前红线
make index-status STRICT=1
```

## 非声明

- 本文件是**派生线索 + 回源结论**的记录，不是权威职责定义；与 `specs/` 冲突时以 `specs/` 为准。
- 本文件不构成 `QA_PASS`，不作为 Gate/ADR 依据；**不推进 W1–W8 任何一波的状态**。
- 本轮未触碰 GK17 单写者路径（`STATE.json` / `ROLE_BOARD.yaml` / `ORCHESTRATOR.md` / `NEXT_SESSION.md` / `EVIDENCE.json`）。
