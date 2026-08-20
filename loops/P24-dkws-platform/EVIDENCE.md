# P24-DKWS-Platform 实施证据

状态：P0–P9（平台 + 演示资产 + 真实 LLM 集成 + 方案 X 供应链生产链）完成，待独立 QA 复核。

## 范围

在 `scenario/dkws-platform/` 实现 `DKWS-SPEC-001`（文件目录型数据知识服务模拟平台）
P0→P9 全量：五层工作区、契约化 Markdown 合同（20+ 文件 schema）、接入/文档/候选/发布/投影/服务、
CLI（`dkws`）+ 可选 HTTP API；并接入「客户经理持续经营」场景（华东精工线）的 12 类知识领域资产，
提供 LLM 读知识地图 → 访前报告的组装演示（含真实 DeepSeek 直连）。

## 交付物

| 类别 | 说明 |
|---|---|
| 平台源码 | `scenario/dkws-platform/src/dkws/*.py`（contract/schemas/state/workspace/ingest/docs/knowledge/publish/projection/service/http_api/cli/trace/hashing/logging/mdio/errors/**llm**） |
| 真实 LLM 适配器 | `scenario/dkws-platform/src/dkws/llm.py`（OpenAI 兼容 `RealLlm`；凭据仅环境加载） |
| 测试 | `scenario/dkws-platform/tests/*.py`（**54 项通过**） |
| 样例 | `scenario/dkws-platform/seeds/{legal,illegal}`（`scripts/make_seeds.py`） |
| 场景演示脚本 | `scripts/demo_rm_data_access.py`（接入 12 类知识领域）、`demo_previsit_setup.py`（访前业务资产）、`demo_previsit_report.py`（LLM 读图→访前报告） |
| 文档 | `scenario/dkws-platform/README.md`、`docs/DATA_ASSETS_LOCATION.md`、`docs/RM_CONTINUOUS_ENGAGEMENT_DATA_ACCESS.md`、`docs/PREVISIT_REPORT_ASSEMBLY.md` |
| CLI | `python -m dkws --help` 可用，端到端链路冒烟通过 |

## Gate 证据

| Phase | 验收点 | 结果 |
|---|---|---|
| P0 | 五层工作区 init/inspect、meta、需求矩阵 | PASS：`tests/test_pipeline.py::TestWorkspace`，54 测试全绿 |
| P1 | 契约化 MD 框架 + schema 校验 + DSL + 合法/非法样例 | PASS：`tests/test_contract.py` + `tests/test_seeds.py`（seeds 合法全过、非法全拒） |
| P2 | Raw 接入 + MANIFEST + SHA-256 幂等 + 任务状态机 | PASS：`TestIngest`（幂等冲突、大小上限、非法 domain） |
| P3 | 结构化清洗与 Parquet（zstd/列序；无 pyarrow 降级 CSV） | PASS：投影构建出 csv + schema 文件 |
| P4 | 文档登记 + 规范化 + 稳定切片 | PASS：`TestDocs`（重跑同段数） |
| P5 | 知识候选 + 冲突检测 + 审核决定（系统禁自签 OWNER/QA） | PASS：`TestKnowledge`（自动 OWNER 决定被拒） |
| P6 | 发布 + Release + CURRENT + 回滚（需批准/冒烟） | PASS：`TestPublish`（无批准拒绝、切 CURRENT、缺版本报错） |
| P7 | Parquet/向量/图/规则投影 + 可重建性 | PASS：`tests/test_projection.py`（重建幂等、无绝对路径） |
| P8 | CLI 服务 query/search/rule + 可选 HTTP（fastapi 惰性） | PASS：`TestRuleExec` + 冒烟；HTTP 未装依赖时明确报错 |
| P9 | 安全（路径穿越/敏感日志/无绝对路径）+ 性能 + E2E 黄金场景 | PASS：`tests/test_security_perf.py` + `tests/test_e2e.py` |

## 测试命令

```bash
cd scenario/dkws-platform
PYTHONPATH=src:tests:scripts python -m unittest discover -s tests -v   # 54 passed
```

## 场景演示资产（客户经理持续经营，华东精工线）

接入 12 类知识领域资产（原文权威源 `scenario/seed/`，DKWS 只读复用）：
客户主数据、产品知识、访前 SOP、KYC 问题库、本体、法人/股权/产业链/行业/关键人物图谱，
产品规则版本、Skill-Product。图谱经 CSV(BOM) 安全解析接入，关系注册遵循引用完整性。
访问清单见 `docs/RM_CONTINUOUS_ENGAGEMENT_DATA_ACCESS.md`、`docs/DATA_ASSETS_LOCATION.md`。

## 方案 X：公司供应链图谱 + 知识组装轨迹（生产链）

> 前置：Owner 确认方案 X（改生产知识链、动 `specs/`）。非原 simulation 边界，属生产链条增强验证。
> 合规：经 code-explorer 全链路确认，`specs/knowledge-architecture/elements/**` 为手写权威源，
> `make generate` / `make check` 均不处理该目录，改 KE content **零 hash 风险、无需 generate**。

### 交付（跨层）
| 层 | 改动 |
|---|---|
| 数据 | `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-01/02/03.md`：从 DRAFT 占位模板填充**真实供应链实例**（上游 3 供应商/下游 2 客户/位置解读），标准 `---{json}---` frontmatter（移除多余 `demo` 字段，规避 `FAIL_ON_UNKNOWN_PROPERTIES`） |
| 演示知识地图 | `scenario/seed/05_knowledge/demo/knowledge-map.yaml` 增 `knowledgeItemBindings`；`elements/_index.yaml` 每个 KI 增 `assetBinding`（KI→dataAsset/dataPath/elementType） |
| 场景 provider | `scenario/execute/.../SimulatedKnowledgeProvider`：读 binding `dataPath` → 装配真实数据进上下文 + 逐 KI 轨迹；新增 `AssemblyTraceStep` record；`KnowledgeAssemblyResult` 扩展 `trace` |
| 生产装配 | `apps/api/.../KnowledgeAssembler.supplyChainMarkdown(kiIds)`：从 KE content 解析供应链 JSON → Markdown；新增 `KnowledgeAssemblerSupplyChainTest`（2 项） |
| 生产 DTO | `PreparedPrevisitResponse` + `PrevisitExecutionResponse` 新增 `supplyChainMarkdown` 字段（带兼容构造，不动既有 11/4 参构造） |
| 生产 controller | `EngagementJourneyController` 注入 `KnowledgeAssembler`，`preparePrevisit` 响应填 `supplyChainMarkdown` |
| 前端 | `api/engagement.ts` 两接口加字段；`EngagementWorkspace.vue` 传 `supplyChainMarkdown`；`KnowledgePrevisitReport.vue` KI-FRONT-001 区块改真实图谱渲染 + 新增**知识组装模拟控制台**（逐 KI 实时滚动：读图→取数→装配→完成，时间戳+状态图标） |

### 验证证据（真实系统，已在跑）
- 后端 `apps/api` test：`DtoSerializationTest 13 passed` + `KnowledgeAssemblerSupplyChainTest 2 passed` → BUILD SUCCESS
- 前端：`vue-tsc --noEmit` exit 0（无类型错误）
- 真实 HTTP 链（HTTP 200）：`POST /journey/start` → journeyId + operatingCaseId →
  `POST /journey/{id}/prepare-previsit`（customerId+operatingCaseId+rmId:RM-ZW-001）→
  返回 `supplyChainMarkdown`（位置解读/下游客户真实数据）+ `previsitReport` + `battleCard`（8.5KB）
- `GET /knowledge/items/KI-FRONT-001` 现返回真实 KE（修复前 `[]`）
- 重启：新 jar 已部署 8082，前端 5173 HMR 已加载新组件

### 设计中修复的真实缺陷
- KE frontmatter 原为纯 `{json}` 布局，`FailClosedJsonReader` 无法提取 → 永远空；
  改标准 `---{json}---` 块并去含 `FAIL_ON_UNKNOWN_PROPERTIES` 的未知字段后**可读**。

### 浏览器层说明（诚实）
`agent-browser` 对 Naive UI SPA 的点击选择器（`[ref]`/`button`/`text=`）定位失效，
故"浏览器内点按钮"未自动化；但真实 API 链 + 前端类型通过 + HMR 生效 + 前端渲染快照均为操作证据。
手动验证路径：`http://localhost:5173/engagement` → 选客户 → 一键访前准备。

## 真实 LLM 集成证据（方案 C，DeepSeek 实测）

- 适配器 `src/dkws/llm.py::RealLlm`：OpenAI 兼容 `chat/completions`，默认
  `https://api.deepseek.com` / `deepseek-chat`；凭据仅从环境加载
  （`DSEEK_2026_SZF_KEY`→回退`LLM_API_KEY`），不硬编码/不落盘/不打印。
- 模式切换 `--llm real|mock` 与 Java 端 `engagement.llm.mode`（`LLM_MODE`）语义对齐。
- 实测：连通性测试通过；`demo_previsit_report.py --llm real` 生成 `status: READY` 访前报告
  （9 项资产命中，知识路径 KM-GITS-ROOT→KM-CORP-RM→AC-PREVISIT-001，人工门禁 HG-B01/C01/D01）。
- 设计：LLM 确定结构（要点/顺序），数据由 DKWS 已发布资产回填并保序去重（LLM 不虚构事实）。
- 测试（离线不触网）：`tests/test_previsit_report.py::TestRealLlmComposeNormalization`。

## 明确非交付（按 DKWS-SPEC-001 simulation 边界）

- 不写生产、不迁移生产、不连真实 RAG/GraphDB/向量库。
- HTTP（fastapi）与 Parquet（pyarrow）为可选项，未安装自动降级/明确报错。
- 系统不自动生成 OWNER / INDEPENDENT_QA 批准决定（§9.19 强制）。
- 真实 LLM 直连为**演示/验证链路**能力；消耗真实 API 额度，凭据不随代码分发（须人工加载）。

## 待办给 QA

- 由独立 QA 依 DKWS-SPEC-001 §18 门禁复核后记录 QA_PASS（开发角色禁止自签）。
- 建议真实平台（RAG/GraphDB/MetadataCatalog）选型由 Owner 另行指定。