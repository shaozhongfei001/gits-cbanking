# W1｜PLAN（本体扩到设计范围，合同先行）

## Goal

把本体从"只规范 9 类"扩到能承载**设计点名的对象**，并**让地图已引用的 ID 空间有权威**，
从而使后续 W2（本体进入路由）/ W5（引用锚定门禁）具备前提。

**量化缺口（W1 前实测）**：`modules/operational-ontology` 有 **30+ 真实领域对象**，
而本体合同只规范 **9 类**；设计点名的 8 类（公司/集团/账户/产品/文档/断言/任务/能力）**只覆盖 1 类**。

## 输入

- `evidence/W1-INPUTS.md`（两个只读侦察代理的产出：类清单 + ID 空间锚定清单）
- 标识字段一律**从 Java record / 注册表实测取名**，不猜、不发明

## Work Packages（**写串行**）

| WP | 内容 | 状态 |
|---|---|---|
| WP1.1 | 设计点名对象：公司 / 集团 / 产品 | ITER 1 完成 |
| WP1.2 | 系统既有对象：授信 / 本行关系快照 / 交易 / 机会 / 承诺 / KYC缺口 / 人工门禁 / 规则 / 外部事件 等 | **未完成（下一 ITER）** |
| WP1.3 | 产品关系谓词 + **权威归属裁定** | ITER 1 完成（裁定件已落盘） |
| WP1.4 | ID 空间补全（任务 / 能力） | ITER 1 完成 |

## 合同先行流程（**唯一合法路径**）

```
改权威源（specs/semantic/gits-core.owl.ttl + gits-core.linkml.yaml）
  → make generate（CTR-SEM-001/002）
  → make check（门禁必须绿，INTEGRITY FAILURES 为空）
  → MechanismE2eIT（真实 Jena 装载 + SHACL 校验）
  → record_gate.py 落证
```

**禁止**：手工编辑 `generated/`；绕过 generate 直接写制品。

## ACCEPT 判据

1. `make generate` PASS；
2. `make check` PASS 且 `INTEGRITY FAILURES` 为空；
3. `MechanismE2eIT` PASS（改过的 OWL 能被真实 Jena 解析）；
4. 新类**确实出现在** `generated/semantic/gits-core.shacl.ttl` 与 `.schema.json`；
5. 全部经 `record_gate.py` 落证。

## 非声明

- WP1 **不解决**「取值词表未受控」（`SETTLEMENT_ACCOUNT` 无户口）—— 属 W3/W5；
- WP1 **不启用**任何关系实例（实例由 W3 投影产生）；
- WP1 **不承诺** `Account` / `Document` 入本体（无系统实据，须先裁定权威物理源）。
