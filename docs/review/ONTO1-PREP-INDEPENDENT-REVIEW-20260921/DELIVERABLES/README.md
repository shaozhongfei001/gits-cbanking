# L1 独立语义契约库 · **候选骨架**（未建立正式仓）

> 状态：`CANDIDATE_NOT_EFFECTIVE`｜命名空间：`PROVISIONAL_SIM_LEGACY_NAMESPACE`（**非**正式根域）

## 这是什么
按四层设计（`docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md`）准备的 **L1 公共核心语义契约库**骨架，
用于承接 `CTR-SEM-003`（L1 公共核心）候选合同。**本目录不是独立仓**，只是候选材料，位于 Loop 证据区。

## 禁令（逐条来自执行计划，必须遵守）
1. **D3 签署前禁止发布新 IRI / 重钉**（§WI-A4）；
2. 重构项**禁止**使用 `equivalentClass`（§WI-1-3 校验④）；
3. **不宣称**正式根域获批；命名空间一律标 `PROVISIONAL_SIM_LEGACY_NAMESPACE`；
4. 未获合同拆条批准前，**不得**把候选内容标 `ACTIVE` 或写入正式 `specs/` 权威路径。

## 内容
- `l1-term-inventory.json`：L1 候选术语清单（类 / 对象属性 / 数据类型属性 / 注解属性，来自 `specs/semantic/gits-core.owl.ttl`）
- `l1-namespace.json`：候选命名空间（provisional）+ 未获批声明
- `LAYOUT.md`：候选仓布局与生成物规划
