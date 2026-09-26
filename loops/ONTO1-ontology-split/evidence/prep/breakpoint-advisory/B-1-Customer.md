# 断点 B-1｜`Customer` → `CustomerRole`

> **本页为裁定材料，不构成裁定**：命名与语义由 **PSO / 数据 Owner** 裁定；TL 只提供事实、正则、排除清单与可选出口。

## 1. 事实（可复算）

- **本名命中（真实消费者面）**：675 处（281 个文件）
- 已排除**扫描器自身产物/工具配置**命中：104 处（不计入受影响面）
- **会被朴素替换误伤的同形/包含命中**：3872 处
- 误伤名样例：`customerId`, `gateOfCustomer`, `ofCustomer`, `opportunityOfCustomer`, `profileOfCustomer`, `refersToCustomer`
- 本名命中样例：`adapters/oracle-source/src/test/java/com/gien/gits/adapter/oracle/OracleCustomerMappingTest.java:8`, `adapters/oracle-source/src/test/java/com/gien/gits/adapter/oracle/OracleCustomerMappingTest.java:16`, `adapters/oracle-source/src/test/java/com/gien/gits/adapter/oracle/OracleCustomerMappingTest.java:17`, `adapters/oracle-source/src/test/java/com/gien/gits/adapter/oracle/OracleCustomerMappingTest.java:28`, `adapters/oracle-source/src/test/java/com/gien/gits/adapter/oracle/OracleCustomerMappingTest.java:38`
- 全量演练（B6+B8 242 条）中"含本词但被跳过"的文件：见 §4

## 2. 受影响面（Top 10 文件）

| 文件 | 命中 |
|---|---|
| `gits:docs/dd/ontology-model-detailed-design.md` | 15 |
| `gits:docs/dd/gk-ke-contract/simulation/graph/nodes.jsonl` | 12 |
| `gits:generated/openapi/gits-kno-api.normalized.json` | 12 |
| `gits:specs/openapi/gits-kno-api.openapi.json` | 12 |
| `gits:docs/dd/mybatis-integration-spec.md` | 11 |
| `gits:adapters/persistence-relational/src/main/java/com/gien/gits/adapter/persistence/JdbcCustomerRepository.java` | 10 |
| `gits:docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` | 10 |
| `gits:docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 9 |
| `gits:docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 9 |
| `gits:specs/semantic/gits-core.owl.ttl` | 9 |

## 3. 受限替换配方（**仅供引用，须经裁定后使用**）

```python
pattern = r"(?<![A-Za-z0-9_])Customer(?![A-Za-z0-9_])"   # 词边界 + 前后不邻接标识符字符
```

**必须排除的相邻名**（否则会产出 `customerIdRole`、`referencesAssetDefinition` 之类脏值）：

（共 6 个）
- `customerId`
- `gateOfCustomer`
- `ofCustomer`
- `opportunityOfCustomer`
- `profileOfCustomer`
- `refersToCustomer`

## 4. 三个可选出口（**各有代价，须裁定**）

| 出口 | 做法 | 代价 / 前置 |
|---|---|---|
| **A 显式清单改名** | 逐文件、逐行按受限配方改名 `Customer` → `CustomerRole`，排除上列相邻名 | 需逐条人工确认；675 处命中须全部核对；**不得批处理** |
| **B 保留原名 + 新名并存** | `Customer` 保持只读，新增 `CustomerRole` 并以注解标注继承关系（**不得** `equivalentClass`） | 双名并存期需点名与退役计划；消费者可渐进切换 |
| **C 延后** | 本断点不进入本轮迁移，登记为待裁项 | 阻塞该术语相关的 Wave 2/3 项；须在退出前补齐 |

## 5. 与全量演练的一致性

- 演练范围：B6+B8 **242** 条；真改写 **242**；含盲替换风险被**跳过**的文件 **149** 个 ⇒ 本断点的改名在演练中**未被自动执行**（设计如此）。

## 6. 我不做什么

- 不替你选定出口（名称与语义属 PSO / 数据 Owner 权限）；
- 不把本页当作已完成的迁移；
- 不在 `specs/**` 写入任何对应改动。

