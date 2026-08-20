# 访前报告数据组装过程演示（LLM 读知识地图）

演示：给定 **客户 ID = `CUST-001`（华东精工装备集团）**，LLM 读知识地图 → 按激活合同检索
DKWS 已发布数据 → 组装 → 输出访前报告。

## 一、数据流

```
客户ID(CUST-001) + 访前任务
  → ① 读根知识地图  ROOT_KNOWLEDGE_MAP  → KM-GITS-ROOT（role/task 路由）
  → ② 进入对公持续经营域  DOMAIN_MAP   → KM-CORP-RM
  → ③ 触发激活合同  AC-PREVISIT-001    → routeMode=ONTOLOGY_THEN_MAP
  → ④ 模拟 LLM 按合同 sequence 逐资产从 DKWS 检索客户数据
  → ⑤ 按优先级组装知识上下文
  → ⑥ 输出结构化访前报告（JSON / Markdown）status=READY
```

## 二、激活合同 `AC-PREVISIT-001` 所需资产 → DKWS 命中

| seq | assetId | required | 用途 | DKWS 命中 |
|---|---|---|---|---|
| 1 | ASSET-DATA-CUSTOMER-PROFILE | 是 | 客户事实 | CUST-001 |
| 2 | ASSET-KNOW-CUSTOMER-ONTOLOGY | 是 | 主体关系与状态查询 | OBJ-Party/Need/Commitment |
| 3 | ASSET-DATA-CREDIT-FACILITY | 是 | 额度和融资事实 | FAC-001 |
| 4 | ASSET-DATA-INTERACTION-HISTORY | 是 | 历史原话和未决事项 | INT-001 |
| 5 | ASSET-DATA-TRANSACTION-SUMMARY | 否 | 本行经营变化 | —（可选） |
| 6 | ASSET-DATA-EXTERNAL-EVENT | 否 | 行业与外部信号 | —（可选） |
| 7 | ASSET-KNOW-KYC-QUESTION-LIBRARY | 是 | 未知对象问题计划 | KY-CFO-001 |
| 8 | ASSET-KNOW-PRODUCT-CARDS | 否 | 定向产品知识 | PROD-WCL@3.4、PROD-FAL@2.2 |
| 9 | ASSET-KNOW-VISIT-SOP | 否 | 访前和离场作业约束 | SOP-PRE-001 |

## 三、演示脚本

| 脚本 | 作用 |
|---|---|
| `scripts/demo_rm_data_access.py` | 初始化工作区：接入 12 类知识领域，发布客户/本体/产品 |
| `scripts/demo_previsit_setup.py` | 注册并发布访前业务资产（授信/互动/KYC/访SOP） |
| `scripts/demo_previsit_report.py` | 执行读图→组装→输出访前报告 |

运行：
```bash
cd scenario/dkws-platform
PYTHONPATH=src python scripts/demo_rm_data_access.py --ws /tmp/dkws-rm-demo   # 初始化+发布v1
PYTHONPATH=src python scripts/demo_previsit_setup.py --ws /tmp/dkws-rm-demo   # 发布v2(访前资产)
PYTHONPATH=src python scripts/demo_previsit_report.py --ws /tmp/dkws-rm-demo --md
```

## 四、演示实际输出（摘要）

```
状态: READY    缺失必备资产: 无    就绪输出: 是    人工门禁: HG-B01/HG-C01/HG-D01

知识路径: KM-GITS-ROOT@0.1.0 → KM-CORP-RM → AC-PREVISIT-001 (ONTOLOGY_THEN_MAP)

组装清单(按 sequence):
  1. 客户画像(必需)      → 华东精工装备集团有限公司
  2. 客户本体(必需)      → Party/Need/Commitment...
  3. 授信额度(必需)      → FAC-001
  4. 互动历史(必需)      → INT-001
  5. 经营变化(可选)      → —
  6. 外部信号(可选)      → —
  7. KYC问题库(必需)     → KY-CFO-001 (CFO)
  8. 产品知识(可选)      → PROD-WCL@3.4 / PROD-FAL@2.2
  9. 访前SOP(可选)       → SOP-PRE-001
```

## 四之二、真实 LLM 直连（方案 C，已实测 DeepSeek）

演示支持两档 LLM 模式（`--llm real|mock`，与 Java 端 `engagement.llm.mode` 语义一致）：

| 模式 | 使用 | 说明 |
|---|---|---|
| `mock`（默认） | `MockLlm` | 确定性读图，可复现、无外部依赖 |
| `real` | `RealLlm`（`src/dkws/llm.py`） | OpenAI 兼容 `chat/completions`，读激活合同+已检索 DKWS 资产，真实模型生成访前要点 |

真实调用运行方式（凭据只从环境加载，绝不硬编码/落盘/打印）：
```bash
eval "$(grep '^export DSEEK_2026_SZF_KEY=' ~/.bashrc)"   # 加载 key，不回显
PYTHONPATH=src python scripts/demo_previsit_report.py --ws /tmp/dkws-rm-demo --llm real --md
```

- 端点：默认 `https://api.deepseek.com`（可用 `DKWS_LLM_BASE_URL` 覆盖），模型 `deepseek-chat`
  （可用 `DKWS_LLM_MODEL` 覆盖）；key 取 `DSEEK_2026_SZF_KEY` 回退 `LLM_API_KEY`。
- 真实 LLM 确定结构（要点/顺序），**数据仍由 DKWS 已发布资产提供并回填**（LLM 不虚构事实），
  `items` 用 DKWS 命中的实体名 + 模型要点做保序去重。
- 本过程为真实外部调用、消耗 API 额度；仅用于演示/验证链路的 LLM 环节，数据组装逻辑保持确定性。

## 五、与既有 Java 实现的对应

- `KnowledgeWikiService`（`apps/api`）↔ `RealLlm`/`MockLlm` 读图 + `_read_map`/`_retrieve`
- `KnowledgeDrivenPrevisitReportGenerator`（`apps/api`）↔ `_render_report`
- `LlmClient` Port ↔ `RealLlm`（`--llm real`）；`MockLlmClient` ↔ `MockLlm`（`--llm mock`），切换方式与
  `engagement.llm.mode`（`LLM_MODE=real/mock`）对齐
- 激活合同 `AC-PREVISIT-001`、优先级 `priorityOrder`、人工门禁 `humanGates` 均复用
- 变体：`_retrieve` 从 DKWS `03_core/knowledge/version=*/` 跨版本聚合已发布实体（而非 MyBatis 查询），
  体现 DKWS 作为文件目录型数据知识服务的访问能力

## 六、说明

- 数据为合成演示（含合成声明），不代表真实客户。
- `status=READY` 表示数据组装就绪；最终对外发布仍须经过 `humanGates`（HG-B01/C01/D01）人工门禁，
  与仓库"AI 只产生候选，正式 ControlledAction 需人工确认"规则一致。