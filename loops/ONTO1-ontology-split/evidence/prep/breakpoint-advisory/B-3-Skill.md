# 断点 B-3｜`Skill` → `SkillDefinition`

> **本页为裁定材料，不构成裁定**：命名与语义由 **PSO / 数据 Owner** 裁定；TL 只提供事实、正则、排除清单与可选出口。

## 1. 事实（可复算）

- **本名命中（真实消费者面）**：1398 处（356 个文件）
- 已排除**扫描器自身产物/工具配置**命中：69 处（不计入受影响面）
- **会被朴素替换误伤的同形/包含命中**：21 处
- 误伤名样例：`referencesSkill`
- 本名命中样例：`AI_GUIDE.md:25`, `HANDOFF-CURSOR-P24.md:32`, `README.md:23`, `apps/api/src/main/java/com/gien/gits/adapter/skill/FallbackSkillExecutionAdapter.java:51`, `apps/api/src/main/java/com/gien/gits/api/config/EngagementConfig.java:155`
- 全量演练（B6+B8 242 条）中"含本词但被跳过"的文件：见 §4

## 2. 受影响面（Top 10 文件）

| 文件 | 命中 |
|---|---|
| `gits:docs/analysis/PREVISIT_WORKFLOW_ANALYSIS_V3.2.md` | 52 |
| `kert:docs/dd/KERT_生产级混合架构独立评审报告_2026-08-26_V1.0.md` | 41 |
| `kert:docs/architecture/KERT_SPRING_AI_ALIBABA_VS_PYTHON_NATIVE_COMPARISON_V1.0.md` | 39 |
| `kert:docs/dd/KERT_independent_architecture_review_2026-08-26_V1.0.md` | 36 |
| `kert:evidence/kert-e2e-ci/evidence-runs/ci_kert-down.log` | 29 |
| `kert:evidence/kert-e2e-ci/evidence-runs/g4_kert_down_require_kert.log` | 29 |
| `kert:evidence/kert-e2e-ci/evidence-runs/g6_no_service_require_all.log` | 29 |
| `kert:specs/kert-openapi-v1.yaml` | 28 |
| `gits:scenario/seed/15_tests/acceptance_tests.jsonl` | 27 |
| `kert:evidence/kert-e2e-ci/evidence-runs/g1_no_service-ledger.json` | 26 |

## 3. 受限替换配方（**仅供引用，须经裁定后使用**）

```python
pattern = r"(?<![A-Za-z0-9_])Skill(?![A-Za-z0-9_])"   # 词边界 + 前后不邻接标识符字符
```

**必须排除的相邻名**（否则会产出 `customerIdRole`、`referencesAssetDefinition` 之类脏值）：

（共 1 个）
- `referencesSkill`

## 4. 三个可选出口（**各有代价，须裁定**）

| 出口 | 做法 | 代价 / 前置 |
|---|---|---|
| **A 显式清单改名** | 逐文件、逐行按受限配方改名 `Skill` → `SkillDefinition`，排除上列相邻名 | 需逐条人工确认；1398 处命中须全部核对；**不得批处理** |
| **B 保留原名 + 新名并存** | `Skill` 保持只读，新增 `SkillDefinition` 并以注解标注继承关系（**不得** `equivalentClass`） | 双名并存期需点名与退役计划；消费者可渐进切换 |
| **C 延后** | 本断点不进入本轮迁移，登记为待裁项 | 阻塞该术语相关的 Wave 2/3 项；须在退出前补齐 |

## 5. 与全量演练的一致性

- 演练范围：B6+B8 **242** 条；真改写 **242**；含盲替换风险被**跳过**的文件 **149** 个 ⇒ 本断点的改名在演练中**未被自动执行**（设计如此）。

## 6. 我不做什么

- 不替你选定出口（名称与语义属 PSO / 数据 Owner 权限）；
- 不把本页当作已完成的迁移；
- 不在 `specs/**` 写入任何对应改动。

