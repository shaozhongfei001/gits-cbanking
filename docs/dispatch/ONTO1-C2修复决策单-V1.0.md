# ONTO1 · C-2 命名空间冲突｜修复决策单 V1.0

> **这一页不含流程要求。** 只需 Owner 一句话（第 4 节），我即可实施。它是**代码级缺陷**，不是文书工作。

## 1. 问题（三行证据，可自查）

**T-Box（类定义）**
`specs/semantic/gits-core.owl.ttl:1` → `@prefix gits: <https://gientech.com/gits/kno/>`
`specs/semantic/gits-core.owl.ttl:127` → `gits:Product a owl:Class`
⇒ 类 `Product` 的 IRI = `https://gientech.com/gits/kno/Product`

**A-Box（实例数据）**
`specs/knowledge-architecture/instances/product/products.ttl:1` → `@prefix gits: <https://gits.bank.example/ontology/core#>`
`specs/knowledge-architecture/instances/product/products.ttl:10` → `gits:prod_cb_001 a gits:Product`
⇒ 此处的 `Product` = `https://gits.bank.example/ontology/core#Product`

**后果**：两个 IRI 不同。产品实例 `prod_cb_001`（跨境人民币结算）与 `prod_cb_002`（内保外贷）所断言的类，**在 T-Box 中不存在** ⇒ 按类 `kno/Product` 查询实例**查不到这两条**，推理链断裂（孤儿实例）。
同源缺陷：`gits:` 这一短前缀在**第 1 行**被绑到两个不同命名空间（前缀语义随文件而异）。

> 这两条是 `wi_a4_namespace_collision` 的**唯一 fail 项**（C-2），也是 Wave 3 的退出门禁前置。碰撞检查**未误报**：登记表 `evidence/namespace-known-defects.json` 明确写有"登记 ≠ 豁免；命中即阻断发布"。

## 2. 两个方案（各只需改 1 行）

### 方案 A（推荐）：把 A-Box 对齐到 T-Box

```diff
  specs/knowledge-architecture/instances/product/products.ttl:1
- @prefix gits: <https://gits.bank.example/ontology/core#> .
+ @prefix gits: <https://gientech.com/gits/kno/> .
```

- 影响面：`products.ttl`（115 行）内全部 `gits:` 展开后的 IRI 统一；`gits.bank.example` 此后仅存在于 `docs/` 描述性文本（**无 Java 引用**，无代码连带）。
- D3 根域生效后若变更，随 L1 迁移一并调整（属原计划内迁移，不是返工）。

### 方案 B（改动最小）：保留 A-Box 命名空间，T-Box 加桥接

```diff
  specs/semantic/gits-core.owl.ttl（新增 1 行）
+ <https://gits.bank.example/ontology/core#Product> owl:equivalentClass gits:Product .
```

- 影响面：不动 `products.ttl`；但长期保留**双命名空间并存**，D3 之后仍需收敛一次。

## 3. 我拿到授权后 30 分钟内做完的事

1. 按选中方案修改**指定文件**；
2. 重跑 `python3 scripts/onto1_namespace_collision_check.py --gate` ⇒ 期望 **C-2 = 0 处**（板面唯一 fail 转绿）；
3. 从 `evidence/namespace-known-defects.json` 删除**已修项**（陈旧登记会被门禁判 FAIL，不能留假豁免）；
4. 出证据日志（含 `# artifact=<脚本>@<哈希>` 自证，退出码透传）；
5. 更新 `EVIDENCE.md` 与板面记录。

**不在本单范围**：D3 根域裁定、40 条产品关系分类（见第 5 节）。

## 4. 只需要你这一句（任选其一）

> **A**：「以 Owner 决策解阻 Wave 0，先修 C-2，采用**方案 A**，由 TL 实施并记 `OWNER_REVIEW`。」
> **B**：「同上，采用**方案 B**。」

（"记 `OWNER_REVIEW`"只是**如实标注这条授权的来源是你的 Owner 决策**，而非委员会批准或我的自定——不给你增加任何签署动作。）

## 5. 另外两处**确实还不明确**（这一句授权解决不了，需要你指定）

| 项 | 现状 | 需要你给的一句话 |
|---|---|---|
| **D3 根域** | 双 Owner 未联签（只批政策、未批根域）⇒ IRI 的"根"未定 | "按现有命名空间定稿、D3 后再说" 或 "等 D3 再改" |
| **D2 产品关系 40 处** | 全部标 `QUARANTINED_UNRESOLVED`，无人分类 | "由 TL 按现有证据推定并标注推定" 或 "由数据 Owner 分类" |

## 6. 非声明

本单不构成设计批准、不构成委员会结论、**未改动任何制品**（写本文件不触碰 `specs/`）；C-2 修复前，Wave 2/3 退出门禁**不满足**，板面仍为 31 门禁 = 30 pass / 1 fail。
