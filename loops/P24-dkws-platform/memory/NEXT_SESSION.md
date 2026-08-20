# P24-DKWS-Platform 交接

- Loop: P24-DKWS-Platform
- 状态: ready_for_independent_qa（P0–P9 均已 DEV_SELF_CHECK_PASS）
- 下一持有者（Baton）: owner / independent_qa
- 权威: scenario/文件目录型数据知识服务模拟平台_详细需求与详细设计_V1.0.md（DKWS-SPEC-001）

## 待办（QA 接手）

1. 独立 QA 依 DKWS-SPEC-001 §18 门禁逐项复核，记录 QA_PASS（禁止 Feature Pilot 自签）。
2. 建议由 Owner 决定真实平台选型（RAG/GraphDB/MetadataCatalog）——本 Loop 明确不做生产接入。
3. 可选增强：安装 fastapi 后验证 HTTP API；安装 pyarrow 后验证 parquet zstd 投影列序。
4. 真实 LLM `--llm real` 验证需人工加载凭据（`DSEEK_2026_SZF_KEY`），运行时不含凭据。

## 已补充交付（完成后追加）

- **12 类知识领域资产接入**：客户/产品/SOP/KYC/本体/法人/股权/产业链/行业/关键人物/产品规则/Skill，
  原文在 `scenario/seed/`，DKWS 只读复用。清单见 `docs/RM_CONTINUOUS_ENGAGEMENT_DATA_ACCESS.md`、
  `docs/DATA_ASSETS_LOCATION.md`。
- **真实 LLM 直连**：`src/dkws/llm.py::RealLlm`（OpenAI 兼容；DeepSeek 实测），`--llm real|mock`。
  LLM 确定结构，数据由 DKWS 回填并保序去重。见 `docs/PREVISIT_REPORT_ASSEMBLY.md`。
- **方案 X（生产链，跨层）**：供应链图谱 + 知识组装轨迹。
  数据 `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-01/02/03.md`（真实实例，
  `---{json}---`）；scenario `SimulatedKnowledgeProvider` assetBinding+`AssemblyTraceStep`；
  apps/api `KnowledgeAssembler.supplyChainMarkdown` + `PreparedPrevisitResponse`/`PrevisitExecutionResponse`
  新增 `supplyChainMarkdown` + controller 注入填充；前端图谱渲染+实时控制台。
  验证：apps/api 15 tests BUILD SUCCESS、vue-tsc 通过、真实 prepare-previsit HTTP 200。

## 待办（QA 接手）— 方案 X

5. 复核 `specs/knowledge-architecture/elements/KI-FRONT-001/KE-FRONT-001-01/02/03.md` 真实供应链数据。
6. 复核前端控制台：`KnowledgePrevisitReport.vue` 知识组装模拟控制台（逐 KI 滚动）。
7. 手动验证路径：`http://localhost:5173/engagement` → 选客户 → 一键访前准备（供应链图谱+控制台）。

## 实现关键点（供复核）

- `scenario/dkws-platform/src/dkws/schemas.py` 注册 20+ 文件类型（§9）；`contract.py` 通用校验。
- `state.py` 任务/知识资产/发布状态机（§11）。
- 确定性：`docs.py` 稳定切片；`projection.py` 可重建（同输入同输出）；`hashing.py` SHA-256。
- 人工边界（§9.19）：系统禁止为 OWNER/INDEPENDENT_QA 自动生成批准决定。
- 只读生成物 + 工作区相对路径（不承载宿主绝对路径）。
- HTTP/Parquet 可选；未装依赖自动降级（CSV）/ 明确报错。
- CSV 含 BOM 的安全解析 `_csv_rows()`；`RealLlm` 凭据仅环境加载、不落盘。

## 复核命令

```bash
cd scenario/dkws-platform
PYTHONPATH=src:tests:scripts python -m unittest discover -s tests -v   # 54 passed
PYTHONPATH=src python scripts/make_seeds.py seeds        # 重生成样例后可再跑 test_seeds
# 真实 LLM（需人工加载 key，不回显）：
PYTHONPATH=src python scripts/demo_rm_data_access.py --ws /tmp/dkws-rm-demo
PYTHONPATH=src python scripts/demo_previsit_setup.py --ws /tmp/dkws-rm-demo --extra-only
eval "$(grep '^export DSEEK_2026_SZF_KEY=' ~/.bashrc)"
PYTHONPATH=src python scripts/demo_previsit_report.py --ws /tmp/dkws-rm-demo --llm real --md
```