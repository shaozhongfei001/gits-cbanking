# DKWS 客户经理持续经营演示 · 已准备数据集存放位置

场景：华东精工客户经理持续经营闭环（RM-CONTINUOUS-ENGAGEMENT-HDEG-001-V11）。
数据均为合成（synthetic）演示数据。

## 一、原文权威源（SSOT，只读复用）—— `scenario/seed/`

| # | 数据集 | 存放位置（原文） | 格式 |
|---|---|---|---|
| 1 | 客户主数据/基础信息 | `seed/02_master_data/customer_master.json` | JSON |
| 2 | 产品知识/产品准入 | `seed/05_knowledge/product_knowledge_cards.yaml` | YAML |
| 3 | 运营规范/访前中后 SOP | `seed/05_knowledge/visit_sop.yaml` | YAML |
| 4 | KYC 问题库 | `seed/05_knowledge/kyc_question_library.jsonl` | JSONL |
| 5 | 本体/对象与关键区分 | `seed/05_knowledge/ontology_seed.json` | JSON |
| 6 | 企业图谱/法人实体 | `seed/02_master_data/legal_entities.csv` | CSV |
| 7 | 企业图谱/股权关系 | `seed/02_master_data/group_relationships.csv` | CSV |
| 8 | 企业图谱/产业链节点 | `seed/02_master_data/industry_chain_nodes.csv` | CSV |
| 9 | 企业图谱/行业分层 | `seed/02_master_data/industry_taxonomy.csv` | CSV |
| 10 | 企业图谱/关键人物 | `seed/02_master_data/stakeholder_directory.csv` | CSV |
| 11 | 产品规则版本 | `seed/05_knowledge/product_rule_versions.jsonl` | JSONL |
| 12 | Skill-Product 注册 | `seed/05_knowledge/skill_product_registry.json` | JSON |

## 二、DKWS 工作区落点（接入后派生，可查询/可重建）—— `demo_rm_data_access.py` 运行时生成

以下路径为每次运行 `scripts/demo_rm_data_access.py --ws <WS>` 生成的**工作区相对路径**（示例 WS 为 `/tmp/dkws-rm-demo`）。生成物只读，随输入确定性重建。

| 层 | 落点（工作区相对） | 内容 |
|---|---|---|
| `01_raw` | `01_raw/knowledge/batch-*/` + `MANIFEST.md` | 原文接入批次与清单（含 SHA-256） |
| `02_work/U` | `02_work/U/RM-<doc>/NORMALIZED.md` + `segments/*.md` | 规范化文本 + 稳定切片（产品卡/SOP/KYC） |
| `02_work/C` | `02_work/C/{entity,statement,relation,rule}/*.md` | 知识候选（实体/关系/声明） |
| `03_core` | `03_core/knowledge/version=1.0.0/{entities,relations,statements,rules}/*.md` + `RELEASE.md` | **已发布核心知识（PUBLISHED）** |
| `03_core` | `03_core/knowledge/CURRENT.md` | 当前活动版本指针 |
| `04_serve` | `04_serve/<service>/version=1.0.0/{entities,relations,statements}.{csv,parquet}` + `PROJECTION.md` | 服务投影 |
| `90_control` | `90_control/decisions/DC-RM-DEMO.md` | 人工审核决定 |
| `90_control` | `90_control/jobs/<job_id>/{STATUS.md,RUN_REPORT.md}` | 任务状态与运行报告 |
| `90_control` | `90_control/logs/<date>/<job>.log` | 结构化日志（敏感脱敏） |

## 三、清单/交付物

| 说明 | 位置 |
|---|---|
| 演示脚本 | `scenario/dkws-platform/scripts/demo_rm_data_access.py` |
| 知识领域访问清单 | `scenario/dkws-platform/docs/RM_CONTINUOUS_ENGAGEMENT_DATA_ACCESS.md` |
| 数据集位置清单（本文） | `scenario/dkws-platform/docs/DATA_ASSETS_LOCATION.md` |
| 契约/工程源码 | `scenario/dkws-platform/src/dkws/` |
| 测试 | `scenario/dkws-platform/tests/`（51 passed） |

## 四、说明

- 原文权威源在 `scenario/seed/`，DKWS 只读复用、不回写。
- 派生落点随 WS 目录变化；`<version>` 由发布时自动递增（当前 `1.0.0`）。
- 未接入但同场景可访问的数据（报告 R0–R8、CRM 回写、客管队列/绩效、隐性知识、证据策略等）见 `RM_CONTINUOUS_ENGAGEMENT_DATA_ACCESS.md` 第四节。