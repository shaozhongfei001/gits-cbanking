# 候选合同与影响清单（DRAFT｜**未正式生效**）

- 依据：Owner 决议 2026-09-21 准备项 1；执行计划 §74
- 状态：`CANDIDATE_NOT_EFFECTIVE（**未正式生效**：不得据此改 CONTRACT_INDEX、不得发布新 IRI）`

| 合同 | 层次 | 权威源 | owner | 状态 |
|---|---|---|---|---|
| `CTR-SEM-002（收窄后）` | L3 运行本体（GITS 侧） | `specs/semantic/gits-core.owl.ttl（收窄：仅 L3）` | semantic_architecture_owner | `CANDIDATE_NOT_EFFECTIVE` |
| `CTR-SEM-003（新）` | L1 公共核心语义契约库 | `候选 L1 仓（骨架见 evidence/prep/l1-skeleton/，**尚未建立**）` | 公共语义 Owner（当前由项目 Owner 临时兼任） | `CANDIDATE_NOT_EFFECTIVE` |
| `CTR-SEM-004（新）` | L2 KERT 元模型 | `KERT 侧 90_control/ontology/（改动需 KERT 维护方权限）` | Knowledge/KERT Owner | `CANDIDATE_NOT_EFFECTIVE` |
| `CTR-SEM-005（新）` | L4 注册表 Schema/SKOS | `候选：注册表 Schema + SKOS 词表` | Integration Contract Owner（当前由项目 Owner 临时兼任） | `CANDIDATE_NOT_EFFECTIVE` |

## 影响面

- 受影响义务数（去重）：**16**
- 涉及批次：['B2_L1_L2_语义规格层', 'B7_导入级耦合（代码导入本体包）', 'B8_内容级重绑（IRI/词表/哈希）']
- 直接读 `specs/semantic/**` 的义务：[]

## 适用禁令（必须遵守）
- 未签 D3 前**禁止发布新 IRI / 重钉**（执行计划 §WI-A4）
- WI-A2 命中处置表**未完成**（未闭环聚合行 **412**：CONTROL_PLANE_REQUIRED 23 / FOLLOW_MIGRATION 270 / HOMONYM_REQUIRES_SOURCE_CHECK 119）⇒ **依 WI-A2，Wave 2 禁止开工**（执行计划 §WI-A2）
- 重构项**禁止**使用 `equivalentClass`（执行计划 §WI-1-3 校验④）
- D1 标准文本到手前**禁止任何国标符合性表述**（执行计划 §WI-A3）
