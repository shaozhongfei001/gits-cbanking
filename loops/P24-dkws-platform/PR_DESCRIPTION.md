# PR: P24-DKWS 文件目录型数据知识服务模拟平台 + 供应链图谱生产链

- 分支机构：`feature/P24-dkws-supplychain`
- 合并目标：`main`
- 关联 Loop：`P24-DKWS-Platform`
- 合同变更（如有）：无（`specs/knowledge-architecture/elements/**` 为手写权威源，不触碰 contract hash；`scenario/seed/**` 为演示数据非受控源）

## PR 描述

该分支交付 **P24 文件目录型数据知识服务（DKWS）模拟平台**，并完成 Owner 批准的**方案 X**：把"公司供应链图谱"从空壳数据落到实处，端到端贯通生产链，并在前端提供**知识组装模拟控制台**。

### 提交构成（4 个原子提交）

| 提交 | 消息 | 内容 |
|---|---|---|
| `1307f17` | `feat(engagement): 公司供应链图谱生产链 + 知识组装轨迹` | 方案 X 主体 |
| `eacda25` | `feat(dkws): P24 文件目录型数据知识服务模拟平台` | Python 平台（contract/schemas/ingest/docs/knowledge/publish/projection/service/cli/llm…） |
| `5e7750d` | `chore(dkws): P24 演示知识要素 + Loop 权威入口入库` | KI-FRONT-001..006 要素 + supply-chain/rules/tasks + LOOP.yaml/memory |
| `6c15175` | `test(engagement): 修复 controller 测试新增依赖 mock` | 方案 X 引入的测试回归补丁 |

### 核心改动

**1. 供应链图谱数据（原为空）**
- `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-01/02/03.md`：从 DRAFT 占位模板填充真实供应商实例（上游 3 / 下游 2 / 位置解读），改用标准 `---{json}---` frontmatter（修复原纯 JSON 布局导致 `FailClosedJsonReader` 无法解析、永远返回空的问题）
- `scenario/seed/05_knowledge/demo/supply-chain/supply-chain.yaml`：演示图谱数据

**2. 知识条目→数据映射（KI→assetBinding）**
- `knowledge-map.yaml` 增 `knowledgeItemBindings`；`elements/_index.yaml` 每 KI 增 `assetBinding`（dataAsset/dataPath/elementType）
- `SimulatedKnowledgeProvider` 读 binding 装配真实数据 + 新增 `AssemblyTraceStep` 逐 KI 轨迹；`KnowledgeAssemblyResult` 扩展 `trace`

**3. 生产装配与 DTO**
- `KnowledgeAssembler.supplyChainMarkdown(kiIds)`：从 KE content 解析供应链 JSON → Markdown
- `PreparedPrevisitResponse` + `PrevisitExecutionResponse` 新增 `supplyChainMarkdown`（带兼容构造，不破坏既有构造）
- `EngagementJourneyController` 注入 `KnowledgeAssembler`，`prepare-previsit` 填充供应链数据

**4. 前端**
- `KnowledgePrevisitReport.vue` KI-FRONT-001 区块：占位 → 真实供应链图谱渲染（上游/中游/下游徽章 + 属性）
- 新增**知识组装模拟控制台**：逐 KI 实时滚动打印「读图→解析映射→取数→装配→完成」，带时间戳 + 状态图标
- `EngagementWorkspace.vue` 传递 `supplyChainMarkdown`；`api/engagement.ts` 接口加字段

## 自检清单

| # | 检查项 | 结果 |
|---|---|---|
| 1 | `make generate` 成功 | ✅ 无需改动受控生成源（`scenario/seed`、`specs/knowledge-architecture/elements` 非 generate 源） |
| 2 | `make check` 通过 | ✅ PASS：contract-check / knowledge-architecture-check / loop-guard / secret-scan / enum-consistency / semantic-rule-gate(SHACL+Schema+DMN+LinkML) 全 PASS |
| 3 | `make backend-test` 通过 | ⚠️ 需要注意（见下"已知说明"），已用等价离线方式验证 |
| 4 | `make frontend-test` 通过 | ⚠️ `npm ci` 因锁文件既有失同步（`@emnapi/wasi-threads`）失败；已验证 `npm run check` + `test` + `build` 全过（见下） |
| 5 | 新增代码有测试覆盖 | ✅ `KnowledgeAssemblerSupplyChainTest`(2) + `SimulatedKnowledgeProviderTest` 供应链/轨迹断言 + `EngagementJourneyControllerTest` mock 修复 |
| 6 | 合同变更已注册 CONTRACT_INDEX | ✅ 无合同变更（见上） |
| 7 | 无敏感信息泄露 | ✅ secret-scan PASS；无 key 硬编码 |

### 自检详细结果

**make check**（真实运行）
```
contract-check: PASS
knowledge-architecture-check: PASS
loop-guard: PASS
secret-scan: PASS (90 advisory 提示，非暴露)
enum-consistency: PASS — 2 族受控枚举, 19 个 seed 文件
semantic-rule-gate: SHACL/Schema/DMN/LinkML: PASS
```

**后端测试**（`apps/api -am`，14 模块）
- 单元测试全过；`make check` 使用 `MAVEN_OPTS=-Ddependency.check.auto.update=false`（离线）
- 全量 `mvn verify` 首次因 OWASP dependency-check 需联网下载 RetireJS 超时 → 环境原因，非代码回归；离线模式编译+单测 SUCCESS

**前端**（`frontend/`）
- `npm run check`（vue-tsc --noEmit）✅
- `npm run test`（vitest）✅ 9 files / 100 tests passed
- `npm run build` ✅ built in 530ms
- `make frontend-test` 的 `npm ci` 报锁文件失同步（`@emnapi/wasi-threads@1.2.1` 不在 lock）→ **既有环境问题，非本分支引入**；node_modules 已存在故直接跑 check/test/build 均过

**DKWS 平台 Python 测试**
- `python -m unittest discover -s tests` ✅ 54 tests OK

## 已知说明（诚实披露）

1. `make frontend-test` 与全量 `mvn verify` 的**确失败点均与本分支改动无关**：前端锁文件失同步既有、后端 OWASP 依赖检查需联网既有。本分支引入的**唯一真实回归**（`EngagementJourneyControllerTest` 缺 mock）已识别并在 `6c15175` 修复、复跑 4/4 通过。
2. 供应链数据为**合成演示数据**（华东精工线，06_interactions 叙事）并标注 demo，不代表真实客户。
3. `agent-browser` 对 Naive UI 点击选择器失效，浏览器级手动操作未自动化；真实操作证据为后端 HTTP 链路 + 前端类型/测试/构建通过与渲染快照。手动验证：`http://localhost:5173/engagement` → 选客户 → 一键访前准备。