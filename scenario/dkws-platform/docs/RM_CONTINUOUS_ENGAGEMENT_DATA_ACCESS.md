# 客户经理持续经营 · 知识领域数据访问清单（DKWS 平台演示）

场景：`华东精工客户经理持续经营闭环—痛点增强运行场景`
（`RM-CONTINUOUS-ENGAGEMENT-HDEG-001-V11`，主营业日 2026-07-08，弧线 2026-05-18~07-20）

演示地址：`scenario/dkws-platform/scripts/demo_rm_data_access.py`
运行：
```bash
cd scenario/dkws-platform
PYTHONPATH=src python scripts/demo_rm_data_access.py --ws /tmp/dkws-rm-demo
```

---

## 一、逐项清单：访问的知识领域数据 / 存储位置 / 输出格式

> 「存储位置」两列并列：**原文权威源**（`scenario/seed/`，契约 SSOT）与 **DKWS 工作区落点**（`01_raw→02_work→03_core→04_serve/90_control`）。
> 「输出格式」指 DKWS 服务返回给上层（客户经理前端/报告生成）的格式。

| # | 知识领域 | 访问的数据 | 原文权威源（存储） | DKWS 工作区落点 | 输出格式 |
|---|---|---|---|---|---|
| 1 | **客户主数据 / 客户基础信息** | 客户 ID、名称、行业、地区、层级、集团、授信/结算概况 | `scenario/seed/02_master_data/customer_master.json` | `03_core/knowledge/version=*/entities/ENT-CUST-001.md` → 投影 `entities.csv` | JSON：`{entity_id, name, entity_type, domain, status}` |
| 2 | **产品知识 / 产品准入（产品画像）** | 产品 ID、版本、关键条件、不适用项、必备材料、禁止项、场景适配 | `scenario/seed/05_knowledge/product_knowledge_cards.yaml` | `02_work/U/RM-product-cards/NORMALIZED.md` + `segments/*.md` | JSON（规范化文本 + 切片元数据） |
| 3 | **运营规范 / 访前·中·后 SOP** | 访前目标、访中沟通顺序、访后 Call Report 与未决问题继承 | `scenario/seed/05_knowledge/visit_sop.yaml` | `02_work/U/RM-visit-sop/NORMALIZED.md` + `segments/*.md` | JSON（规范化文本 + 切片元数据） |
| 4 | **KYC / 问题库（按角色/主题）** | 问题 ID、角色(CFO 等)、主题、访前问题、敏感度 | `scenario/seed/05_knowledge/kyc_question_library.jsonl` | `02_work/U/RM-kyc-library/NORMALIZED.md` + `segments/*.md` | JSON（规范化文本 + 切片元数据） |
| 5 | **本体 / 对象与关键区分** | `Party/LegalEntity/Need/Concern/Commitment/Task/Opportunity...`、关键区分（Claim≠Fact 等） | `scenario/seed/05_knowledge/ontology_seed.json` | `03_core/knowledge/version=*/entities/ENT-OBJ-*.md` → 投影 `entities.csv` | JSON：`{entity_id, name, entity_type, status}` |
| 6 | **企业知识图谱 / 法人实体** | 法人主体 ID、名称、类型、集团本部/项目主体角色、银行客户归属 | `scenario/seed/02_master_data/legal_entities.csv` | `03_core/knowledge/version=*/entities/ENT-*.md` → 投影 `entities.csv` | JSON（实体） |
| 7 | **企业知识图谱 / 股权关系** | 持股比例 ownership_pct、关系类型(OWNS)、有效起始日、来源登记 | `scenario/seed/02_master_data/group_relationships.csv` | `03_core/knowledge/version=*/relations/REL-*.md` → 投影 `relations.csv` | JSON（关系：source/target/relation_type/direction） |
| 8 | **企业知识图谱 / 产业链节点** | 上下游节点、行业代码、典型金融需求（预付款/设备/订单/项目） | `scenario/seed/02_master_data/industry_chain_nodes.csv` | `03_core/knowledge/version=*/entities/CHAIN-*.md` → 投影 `entities.csv` | JSON（产业链节点实体） |
| 9 | **企业知识图谱 / 行业分层** | 行业代码、名称、父级、层级(level) | `scenario/seed/02_master_data/industry_taxonomy.csv` | `03_core/knowledge/version=*/entities/I-*.md`（INDUSTRY_TAXONOMY_NODE）+ `statements/ST-*-parent|lvl` | JSON（行业实体/层级声明） |
| 10 | **企业知识图谱 / 关键人物与影响** | 角色、影响力、态度、银行关系强度、决策议题、偏好渠道、最近联系 | `scenario/seed/02_master_data/stakeholder_directory.csv` | `03_core/knowledge/version=*/entities/STK-*.md`（STAKEHOLDER）+ `statements/ST-STK-*-role|infl|rel` | JSON（人物实体/声明） |
| 11 | **运行技能注册 / 技能能力** | 运行时技能 ID、实现类型、LLM 依赖、副作用策略 | `scenario/seed/05_knowledge/runtime_skill_registry.json` | （可访问引用；本演示以 `skill_product_registry.json` 演示） | JSON |
| 12 | **跨领域对象模型（产品规则版本 / Skill-Product）** | 产品规则版本(生效/状态/所有者)、Skill-Product 注册(human_gate等) | `scenario/seed/05_knowledge/product_rule_versions.jsonl`、`skill_product_registry.json` | `03_core/knowledge/version=*/entities/PROD-*.md`（PRODUCT_RULE_VERSION）+ `SP-*.md`（SKILL_PRODUCT）+ 状态/生效声明 | JSON（产品/Skill 实体+声明） |

---

## 二、DKWS 访问链路（接入 → 发布 → 查询）

```
原文(JSON/YAML/JSONL)
   │ ① 接入(ingest/docs)
   ▼
01_raw(原文) → 02_work(U: NORMALIZED+segments / C: 候选)
   │ ② 知识候选 + 人工审核决定
   ▼
03_core/knowledge/version=<v>/entities|statements|relations (APPROVED→PUBLISHED)
   │ ③ 发布 Release + CURRENT 指针 + 冒烟校验
   ▼
CURRENT.md 指向当前活动版本
   │ ④ service.query / search / rule
   ▼
04_serve/<service>/version=<v>/ 投影(entities/relations/statements.csv|parquet)
```

演示实际输出（`service.query`，接入 11 类知识领域后 `entity_count=15`，均为 PUBLISHED）：
```json
{"entity_count": 15, "entities": [
  {"entity_id": "CHAIN-01", "name": "CHAIN-01", "entity_type": "INDUSTRY_CHAIN_NODE",
   "domain": "knowledge", "status": "PUBLISHED"},
  {"entity_id": "CUST-001", "name": "华东精工装备集团有限公司",
   "entity_type": "CUSTOMER", "domain": "knowledge", "status": "PUBLISHED"},
  {"entity_id": "ENT-001", "name": "华东精工装备集团有限公司",
   "entity_type": "LEGAL_ENTITY", "domain": "knowledge", "status": "PUBLISHED"}]}
```

按类型过滤输出（仅列出已人工批准发布的代表实体）：
| 过滤（--entity-type） | entity_count | 示例 |
|---|---|---|
| `LEGAL_ENTITY` | 5 | ENT-001 集团本部、ENT-002 智能制造… |
| `STAKEHOLDER` | 2 | STK-001(CFO)、STK-002(财务总经理) |
| `INDUSTRY_TAXONOMY_NODE` | 2 | I-100 高端装备制造、I-110 工业自动化装备 |
| `PRODUCT_RULE_VERSION` | 2 | PROD-WCL@3.4、PROD-FAL@2.2 |
| （`entity_count` 总数） | 15 | 含产业链节点/客户本体/法人等 |

图谱事实（股权关系发布到 `03_core/knowledge/version=1.0.0/relations/*.md`，投影 `relations.csv`）：
```
事实： ENT-001 —OWNS 100%→ ENT-002   （华东精工 → 智能制造）
       ENT-001 —OWNS 80% →  ENT-003   （华东精工 → 自动化设备）
       ENT-001 —OWNS 100%→ ENT-004   （华东精工 → 进出口）
       ENT-001 —OWNS 100%→ ENT-005   （华东精工 → 产业投资）
人物： STK-001(CFO,HIGH,STRONG) STK-002(财务总经理,POSITIVE,STRONG)
行业： I-100 → I-110 → I-111/112（层级 1→2→3）
产品： PROD-WCL@3.4 ACTIVE(2026-06-15)、PROD-FAL@2.2 ACTIVE(2026-07-01)
技能： SP-01 客户组合与经营触发（human_gate=CONDITIONAL）等 16 项
```

---

## 三、关键约定（DKWS-SPEC-001 + 仓库规则）

- **存储**：权威源在 `scenario/seed/`（SSOT）；DKWS 只读复用，不写回 `seed/`。
- **输出格式**：统一 JSON 通则（`request_id/status/data/errors[]/meta`），字段 snake_case。
- **路径**：服务返回一律工作区相对路径或逻辑 URI，**不承载宿主绝对路径**。
- **人工责任边界**：Chat 产物为候选；正式发布需人工审核决定（系统禁止自动批准 OWNER/QA）。
- **确定性**：同输入同输出（切片/投影可重建）；SHA-256 校验产物。
- 本演示为**模拟**数据（含合成声明：假定企业/交易为合成演示，不代表真实客户）。

---

## 四、扩展（本次演示已接入 11 类；以下为未接入但属同一场景，可从 `scenario/seed/` 访问）

| 知识领域 | 原文权威源 |
|---|---|
| 客户画像/行业映射 | `02_master_data/customer_industry_mapping.csv` |
| 客管队列/绩效/组合 | `02_master_data/rm_day_queue.csv`, `rm_goals_kpi.csv`, `rm_portfolio.csv` |
| 知识资产注册 | `05_knowledge/knowledge_asset_registry.csv` |
| 隐性知识候选 | `05_knowledge/tacit_knowledge_candidates.jsonl` |
| 证据策略 | `05_knowledge/evidence_policy.yaml` |
| 输出报告（访前作战单/报告） | `scenario/seed/11_outputs/R0_DAILY_OPERATING_BRIEF.md` … `R8_NEXT_PRE_VISIT_REPORT.md` |
| CRM 回写 | `scenario/seed/11_outputs/CRM_WRITEBACK_COMMANDS.jsonl` |