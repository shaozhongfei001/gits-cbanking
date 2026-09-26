# 断点 B-4｜`Asset` → `AssetDefinition`

> **本页为裁定材料，不构成裁定**：命名与语义由 **PSO / 数据 Owner** 裁定；TL 只提供事实、正则、排除清单与可选出口。

## 1. 事实（可复算）

- **本名命中（真实消费者面）**：148 处（66 个文件）
- 已排除**扫描器自身产物/工具配置**命中：36 处（不计入受影响面）
- **会被朴素替换误伤的同形/包含命中**：442 处
- 误伤名样例：`ASSET`, `referencesAsset`
- 本名命中样例：`docs/architecture/GK-KE-L0-2-OC01收口-V1.0.md:78`, `docs/architecture/GK-KE-L0-2-兼容与生成策略-V1.0.md:36`, `docs/architecture/GK-KE-统一地图承担者论证-V1.0.md:205`, `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md:86`, `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md:133`
- 全量演练（B6+B8 242 条）中"含本词但被跳过"的文件：见 §4

## 2. 受影响面（Top 10 文件）

| 文件 | 命中 |
|---|---|
| `gits:specs/knowledge-architecture/activation/map_spec.json` | 9 |
| `gits:docs/dd/gk-ke-contract/GITS-KERT_知识工程体系_项目总契约_V1.0.md` | 8 |
| `gits:docs/dd/gk-ke-contract/contracts/C02_注册中心与知识地图合同.md` | 7 |
| `gits:scripts/gk_ke_l2_2_registry_tests.py` | 7 |
| `gits:docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 5 |
| `gits:docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` | 5 |
| `gits:docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 5 |
| `gits:docs/review/ARCH-ONTO-2026-001-rereview-package/01-主设计-V2.0-复审快照.md` | 5 |
| `gits:scripts/_gen_gk_ke_l2_2_registry.py` | 5 |
| `gits:specs/knowledge-architecture/registry/MapVersion.json` | 5 |

## 3. 受限替换配方（**仅供引用，须经裁定后使用**）

```python
pattern = r"(?<![A-Za-z0-9_])Asset(?![A-Za-z0-9_])"   # 词边界 + 前后不邻接标识符字符
```

**必须排除的相邻名**（否则会产出 `customerIdRole`、`referencesAssetDefinition` 之类脏值）：

（共 2 个）
- `ASSET`
- `referencesAsset`

## 4. 三个可选出口（**各有代价，须裁定**）

| 出口 | 做法 | 代价 / 前置 |
|---|---|---|
| **A 显式清单改名** | 逐文件、逐行按受限配方改名 `Asset` → `AssetDefinition`，排除上列相邻名 | 需逐条人工确认；148 处命中须全部核对；**不得批处理** |
| **B 保留原名 + 新名并存** | `Asset` 保持只读，新增 `AssetDefinition` 并以注解标注继承关系（**不得** `equivalentClass`） | 双名并存期需点名与退役计划；消费者可渐进切换 |
| **C 延后** | 本断点不进入本轮迁移，登记为待裁项 | 阻塞该术语相关的 Wave 2/3 项；须在退出前补齐 |

## 5. 与全量演练的一致性

- 演练范围：B6+B8 **242** 条；真改写 **242**；含盲替换风险被**跳过**的文件 **149** 个 ⇒ 本断点的改名在演练中**未被自动执行**（设计如此）。

## 6. 我不做什么

- 不替你选定出口（名称与语义属 PSO / 数据 Owner 权限）；
- 不把本页当作已完成的迁移；
- 不在 `specs/**` 写入任何对应改动。

