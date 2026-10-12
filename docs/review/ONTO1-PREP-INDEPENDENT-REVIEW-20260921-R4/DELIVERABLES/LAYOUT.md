# L1 候选仓布局（规划，未创建正式仓）

```
<L1-repo>/                        # 候选：独立语义契约库（尚未建立）
├── terms/                        # L1 公共术语（类 / 属性）——由 specs/semantic 收窄而来
│   └── gits-core.owl.ttl         #   候选：仅保留公共核心；L3 私有部分留在 GITS
├── contracts/                    # CTR-SEM-003 权威源与方法论
├── generated/                    # 生成物（schema / shacl）——需合同拆条获批后才有生成目标
└── version/                      # 版本与发布清单（BOM）
```

## 与现有结构的关系（收窄映射）
| 现状 | 候选去向 |
|---|---|
| `specs/semantic/gits-core.owl.ttl`（CTR-SEM-002 权威源） | **收窄为 L3**；公共核心部分上移 L1（CTR-SEM-003） |
| KERT 侧 `90_control/ontology/` | 改放 **L1 副本 + L2 本体**（CTR-SEM-004；需 KERT 维护方权限） |
| 注册表 Schema/SKOS | **CTR-SEM-005**（L4） |

## 验证
- `python3 scripts/onto1_l1_prep.py --gate`：骨架不变式（清单可复算 / 命名空间为 provisional / 未发布新 IRI / 骨架未越出证据区）
- `python3 scripts/onto1_l1_prep.py --migration`：消费者本体引用面解析覆盖率（迁移验证材料）
