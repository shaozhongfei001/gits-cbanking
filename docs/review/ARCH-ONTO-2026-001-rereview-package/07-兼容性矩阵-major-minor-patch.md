# 兼容性规范：major / minor / patch 判定矩阵（M-09 关闭证据）

## 1. 判定矩阵

| 变更类型 | 级别 | 依据 | 必须动作 |
|---|---|---|---|
| 修订 rdfs:comment/label、补充示例、修正错别字（不动语义） | **patch** | 消费方解析结果不变 | CHANGELOG；旧钉值仍有效 |
| 新增类/属性（只增） | **minor** | 旧消费方不受影响的充分条件：**且不改既有约束** | CHANGELOG + 版本号 minor 递增；旧钉值有效 |
| 放宽约束（如 required→optional、扩大值域） | **minor** | 旧实例仍合法 | 同 minor |
| **新增约束**（可能推翻既有结论的必填、基数、值域收窄前置） | **major 候选** | 委员会指正：只增也可能破坏兼容——新约束可使既有合法数据变非法 | 按 major 流程评审；至少要求影响面分析 + 旧夹具行为预测 |
| 删除类/属性/词表项 | **major** | 破坏性 | 新 versionIRI + 弃用期 + 迁移映射 + 回滚预案 + 双侧 Owner 批准 |
| 改名（IRI 变更） | **major** | 破坏性 | 同上 + oldIRI→newIRI 映射（等价规则见 04-D） |
| 收窄 domain/range/值域 | **major** | 旧实例可能非法 | 同 major |
| range 改指（如 ofCustomer→CustomerRole） | **major** | 消费方类型断言失效 | 同 major（本次迁移已按 major 登记） |
| 转制品类型（OWL→Schema/SKOS） | **major** | 消费协议变更 | 同 major + `TRANSFORMED` 映射状态 + 投影层过渡 |
| 基数量变（1..1→0..1 放宽=minor；0..n→1..n 收窄=major） | 按方向定 | 同上 | 同上 |

## 2. 例外与防误判

1. **「只增」不自动等于 minor**：新增约束、新增 `owl:disjointWith`、新增必需属性均为 major 候选，必须过影响面分析。
2. **词表变更单列**：SKOS 新增概念 = minor；退役概念 = major（须 `owl:deprecated` + 替代映射）；改定义不动 notation = patch/minor 评审。
3. **Schema 变更**：新增可选字段 = minor；新增必填字段/删字段/改类型 = major（与消费者绑定版本联动，CQ5 可验）。

## 3. 版本与退役机制

- **版本号**：`versionIRI` 承载语义版本（MAJOR.MINOR.PATCH）；发布制品同时附内容哈希（项目加严，见 V2.0 §6.4）。
- **弃用期**：major 变更须 ≥1 个发布周期**新旧双发布**；旧项标 `owl:deprecated true` + 弃用映射（`oldIRI → newIRI` + 映射关系类型）。
- **迁移映射**：仅语义完全相同且身份可互换用 `owl:equivalentClass/Property`；重构用 SKOS `closeMatch` 或项目状态 `REMODELED`/`TRANSFORMED`。
- **回滚**：每次发布保留上一版本制品只读；回滚 = 消费方重钉旧 versionIRI + 哈希，单向可执行。

## 4. 变更测试（每次变更必跑）

| 测试 | 内容 |
|---|---|
| 旧夹具回归 | 上一版全部正例/负例夹具在新版下的行为必须与**变更预测表**一致（该通过仍通过、该失败仍失败） |
| 影响面分析 | 输出受影响钉值方、plan hash 失效范围、消费者清单（脚本） |
| import closure 检查 | 闭包内不得同时含同一 ontology series 的两个版本 |
| 变异复验 | 注入一处违规 ⇒ 必须 FAIL；恢复 ⇒ PASS |
