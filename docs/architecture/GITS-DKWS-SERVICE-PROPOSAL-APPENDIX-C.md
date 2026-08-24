# 附录 C：SP-20 / SP-21 Skill 完整 JSON 定义

> 关联主文档：`GITS-DKWS-SERVICE-PROPOSAL-INTEGRATION-DESIGN.md` §6

---

## C.1 SP-20：对公客户服务建议书生成

```json
{
  "schemaVersion": "1.0.0",
  "skillId": "SP-20",
  "name": "对公客户服务建议书生成",
  "version": "1.0.0-draft",
  "owner": "客户经营Owner",
  "status": "DRAFT",
  "description": "基于客户企业数据、公开行业/产业数据和交互记忆，生成对公客户服务建议书。遵循五闸门、双版本、事实状态标签规范。",
  "implementationType": "RULE_MODEL",

  "inputs": [
    { "name": "ContextPackage", "type": "object", "schemaRef": "context-package.schema.json", "required": true },
    { "name": "proposalType", "type": "string", "enum": ["INITIAL", "UPDATE"], "required": true },
    { "name": "engagementPhase", "type": "string", "enum": ["PROSPECTING", "FIRST_CONTACT", "ACTIVE_ENGAGEMENT", "PROPOSAL_DELIVERED", "IMPLEMENTATION", "RETENTION"], "required": true }
  ],

  "outputs": [
    { "name": "ProposalDraft", "type": "object", "schemaRef": "proposal-service-result.schema.json" },
    { "name": "citationIndex", "type": "array", "description": "引用索引列表" },
    { "name": "unknowns", "type": "array", "description": "未知项列表" },
    { "name": "limitations", "type": "array", "description": "限制说明" },
    { "name": "gateRecommendations", "type": "object", "description": "闸门推进建议" }
  ],

  "assetDependencies": [
    "ASSET-KNOW-INDUSTRY-ANALYSIS",
    "ASSET-KNOW-FINANCIAL-ANALYSIS",
    "ASSET-KNOW-PROPOSAL-TEMPLATE",
    "ASSET-KNOW-VISIT-SOP"
  ],

  "ruleDependencies": [
    {
      "ruleId": "CITATION_REQUIRED",
      "description": "所有断言必须有引用，标注来源和日期",
      "enforcement": "BLOCKING"
    },
    {
      "ruleId": "NO_UNDISCLOSED_DEGRADATION",
      "description": "不得隐瞒风险降级，内部版风险红旗必须保留",
      "enforcement": "BLOCKING"
    },
    {
      "ruleId": "DUAL_VERSION_PRINCIPLE",
      "description": "内部版和对客版分离，对客版仅含F+A标签内容",
      "enforcement": "BLOCKING"
    },
    {
      "ruleId": "GATE_SEQUENCING",
      "description": "闸门顺序不可跳过：G0→G1→G2→G3→G4→G5",
      "enforcement": "BLOCKING"
    },
    {
      "ruleId": "FACT_LABEL_MANDATORY",
      "description": "每个断言必须标注事实状态标签（F/C/B/H/P/A）",
      "enforcement": "BLOCKING"
    },
    {
      "ruleId": "NO_COMMITMENT_WITHOUT_APPROVAL",
      "description": "未经G3审批的内容不得以承诺性表述呈现",
      "enforcement": "BLOCKING"
    }
  ],

  "humanGatePolicy": "REQUIRED",
  "sideEffectPolicy": "PROPOSE_ONLY",
  "activationContract": "AC-SERVICE-PROPOSAL-001",

  "chapters": [
    {
      "id": "CH01",
      "name": "企业概况与经营现状",
      "template": "ch01-enterprise-overview.md",
      "requiredFactLabel": "F",
      "description": "客户基本信息、股权结构、主营业务、经营现状",
      "dataSources": ["enterpriseData.basicInfo", "publicData.newsEvents"]
    },
    {
      "id": "CH02",
      "name": "行业与竞争分析",
      "template": "ch02-industry-analysis.md",
      "requiredFactLabel": "H",
      "description": "行业趋势、竞争格局、客户行业地位",
      "dataSources": ["publicData.industryReports", "ASSET-KNOW-INDUSTRY-ANALYSIS"]
    },
    {
      "id": "CH03",
      "name": "财务状况与经营能力分析",
      "template": "ch03-financial-analysis.md",
      "requiredFactLabel": "F",
      "description": "财务比率、现金流、盈利能力、偿债能力",
      "dataSources": ["enterpriseData.financialSummary", "ASSET-KNOW-FINANCIAL-ANALYSIS"]
    },
    {
      "id": "CH04",
      "name": "风险分析与预警",
      "template": "ch04-risk-analysis.md",
      "requiredFactLabel": "C",
      "description": "信用风险、市场风险、操作风险、合规风险",
      "dataSources": ["enterpriseData.creditFacility", "publicData.regulatoryChanges"]
    },
    {
      "id": "CH05",
      "name": "客户需求识别与优先级排序",
      "template": "ch05-need-identification.md",
      "requiredFactLabel": "C",
      "description": "显性需求、隐性需求、需求优先级矩阵",
      "dataSources": ["interactionMemory", "interactionHistory"]
    },
    {
      "id": "CH06",
      "name": "服务方案设计",
      "template": "ch06-service-design.md",
      "requiredFactLabel": "C",
      "description": "主方案+备选方案、条件、风险、预期效果",
      "dataSources": ["ASSET-KNOW-VISIT-SOP", "interactionMemory"]
    },
    {
      "id": "CH07",
      "name": "产品推荐与适配",
      "template": "ch07-product-recommendation.md",
      "requiredFactLabel": "C",
      "description": "产品适配矩阵、推荐理由、适用条件",
      "dataSources": ["ASSET-KNOW-PROPOSAL-TEMPLATE", "enterpriseData.creditFacility"]
    },
    {
      "id": "CH08",
      "name": "实施路径",
      "template": "ch08-implementation-path.md",
      "requiredFactLabel": "H",
      "description": "30/90/180天实施计划、里程碑、KPI",
      "dataSources": ["ASSET-KNOW-VISIT-SOP"]
    }
  ],

  "appendixTables": [
    { "id": "APX-A", "name": "客户信息采集表", "template": "apx-a-customer-info-table.md" },
    { "id": "APX-B", "name": "行业分析表", "template": "apx-b-industry-analysis-table.md" },
    { "id": "APX-C", "name": "需求—方案—产品映射表", "template": "apx-c-need-solution-product-mapping.md" },
    { "id": "APX-D", "name": "专家协同单", "template": "apx-d-expert-collaboration.md" },
    { "id": "APX-E", "name": "30/90/180天实施计划", "template": "apx-e-implementation-plan.md" }
  ],

  "generationStrategy": {
    "mode": "CHAPTER_BY_CHAPTER",
    "description": "逐章生成，每章独立LLM调用，最后合并",
    "maxTokensPerChapter": 2000,
    "totalMaxTokens": 20000,
    "retryPolicy": {
      "maxRetries": 2,
      "backoffMs": 1000
    }
  },

  "dualVersionRules": {
    "internalVersion": {
      "includes": ["ALL_FACT_LABELS"],
      "additionalSections": ["风险红旗", "内部判断", "待审批事项", "假设前提"]
    },
    "customerVersion": {
      "includes": ["F", "A"],
      "excludes": ["C", "B", "H", "P"],
      "prerequisiteGates": ["G1", "G2", "G3"],
      "filteringRules": [
        "移除所有非F/A标签的断言",
        "移除内部判断章节",
        "移除风险红旗（除非已转为A标签）",
        "移除待审批事项",
        "对移除内容生成过滤报告"
      ]
    }
  }
}
```

---

## C.2 SP-21：交互记忆抽取

```json
{
  "schemaVersion": "1.0.0",
  "skillId": "SP-21",
  "name": "交互记忆抽取",
  "version": "1.0.0-draft",
  "owner": "客户经营Owner",
  "status": "DRAFT",
  "description": "从客户交互纪要中抽取结构化洞察（交互记忆），与已有记忆比对，输出候选记忆供人工确认。",

  "implementationType": "RULE_MODEL",

  "inputs": [
    {
      "name": "interactionId",
      "type": "string",
      "required": true,
      "description": "交互ID"
    },
    {
      "name": "interactionContent",
      "type": "string",
      "required": true,
      "description": "交互纪要全文"
    },
    {
      "name": "existingMemories",
      "type": "array",
      "required": true,
      "description": "该客户已有的交互记忆列表（用于比对）"
    }
  ],

  "outputs": [
    {
      "name": "candidateMemories",
      "type": "array",
      "description": "新抽取的候选记忆列表"
    },
    {
      "name": "memoryUpdates",
      "type": "array",
      "description": "对已有记忆的置信度更新建议"
    },
    {
      "name": "memorySupersessions",
      "type": "array",
      "description": "被新交互否定的已有记忆（建议标记SUPERSEDED）"
    }
  ],

  "ruleDependencies": [
    {
      "ruleId": "CONFIDENCE_CALIBRATION",
      "description": "置信度校准：有明确证据0.8-1.0，有间接证据0.5-0.7，推断0.3-0.4",
      "enforcement": "ADVISORY"
    },
    {
      "ruleId": "DECAY_RULE_APPLICATION",
      "description": "衰减规则选择：事实性NONE，业务信号LINEAR，情感状态STEP",
      "enforcement": "ADVISORY"
    },
    {
      "ruleId": "DUPLICATE_DETECTION",
      "description": "与已有记忆去重：语义相似度>0.85视为重复，合并而非新增",
      "enforcement": "BLOCKING"
    },
    {
      "ruleId": "NO_UNVERIFIED_FACT",
      "description": "抽取的记忆默认为CANDIDATE状态，不得直接设为CONFIRMED",
      "enforcement": "BLOCKING"
    }
  ],

  "humanGatePolicy": "REQUIRED",
  "sideEffectPolicy": "PROPOSE_ONLY",

  "extractionCategories": [
    {
      "category": "PREFERENCE",
      "description": "客户偏好",
      "extractionHints": [
        "沟通方式偏好（面谈/电话/微信/邮件）",
        "决策风格（独断/协商/民主）",
        "关注重点（效率/成本/风险/创新）",
        "信息接收偏好（数据驱动/案例驱动/关系驱动）"
      ]
    },
    {
      "category": "DECISION_PATTERN",
      "description": "决策模式",
      "extractionHints": [
        "决策链条（谁提议→谁评估→谁审批）",
        "决策时间窗口（即时/周级/月级/季度级）",
        "金额阈值（不同金额对应不同审批层级）",
        "决策触发条件（预算周期/项目周期/事件驱动）"
      ]
    },
    {
      "category": "RELATIONSHIP",
      "description": "关系网络",
      "extractionHints": [
        "关键决策人及角色",
        "内部政治关系（派系/联盟/对立）",
        "外部关系（供应商/客户/监管/竞争对手）",
        "关系变化（新任/离职/升迁）"
      ]
    },
    {
      "category": "BUSINESS_SIGNAL",
      "description": "业务信号",
      "extractionHints": [
        "预算周期和规模",
        "采购计划和优先级",
        "战略方向变化",
        "组织架构调整",
        "新项目/新业务线索"
      ]
    },
    {
      "category": "EMOTIONAL_STATE",
      "description": "情感状态",
      "extractionHints": [
        "信任程度（对银行/对客户经理/对产品）",
        "满意度（现有服务/现有产品）",
        "焦虑/担忧（合规/风险/竞争）",
        "态度变化（积极→消极 或 消极→积极）"
      ]
    }
  ],

  "comparisonStrategy": {
    "similarityThreshold": 0.85,
    "description": "与已有记忆比对：相似度>0.85视为重复，0.5-0.85视为相关（可合并），<0.5视为新记忆",
    "actions": {
      "duplicate": "MERGE（合并，取置信度较高者）",
      "related": "LINK（关联，保留两条，交叉引用）",
      "new": "CREATE（创建新候选记忆）",
      "contradicted": "SUPERSEDE（标记旧记忆为SUPERSEDED，创建新候选）"
    }
  }
}
```

---

## C.3 AC-SERVICE-PROPOSAL-001 激活合同

```json
{
  "schemaVersion": "1.0.0",
  "contractId": "AC-SERVICE-PROPOSAL-001",
  "name": "对公客户服务建议书生成（首次）",
  "version": "1.0.0-draft",
  "status": "DRAFT",
  "skillId": "SP-20",
  "engagementPhase": "PROSPECTING",

  "routeMode": "ONTOLOGY_THEN_MAP",
  "description": "首次生成建议书，先读行业本体框架，再读知识地图",

  "assetDependencies": [
    {
      "assetId": "ASSET-KNOW-INDUSTRY-ANALYSIS",
      "selectionRule": "按客户行业匹配对应行业分析框架",
      "required": true
    },
    {
      "assetId": "ASSET-KNOW-FINANCIAL-ANALYSIS",
      "selectionRule": "通用财务分析框架",
      "required": true
    },
    {
      "assetId": "ASSET-KNOW-PROPOSAL-TEMPLATE",
      "selectionRule": "对公客户服务建议书模板",
      "required": true
    },
    {
      "assetId": "ASSET-KNOW-VISIT-SOP",
      "selectionRule": "访问SOP",
      "required": true
    }
  ],

  "gateSequence": ["G0", "G1", "G2", "G3", "G4", "G5"],

  "gateDefinitions": {
    "G0": {
      "name": "证据准备",
      "checklist": [
        "公开信息有来源和日期",
        "事实与假设分列",
        "数据缺口清单完成"
      ],
      "prohibitions": ["不得把假设作为确定事实带入正式建议"]
    },
    "G1": {
      "name": "客户核验",
      "prerequisites": ["G0通过", "首次拜访完成"],
      "checklist": [
        "目标经确认或标记待确认",
        "事件经确认或标记待确认",
        "痛点经确认或标记待确认",
        "决策人经确认或标记待确认",
        "期限经确认或标记待确认"
      ],
      "prohibitions": ["不得直接进入正式方案承诺"]
    },
    "G2": {
      "name": "专家设计",
      "prerequisites": ["G1通过"],
      "checklist": [
        "需求—方案—产品映射完整",
        "主方案和备选方案明确",
        "方案条件明确",
        "方案风险明确"
      ],
      "prohibitions": ["不得以客户经理个人判断替代专业评估"]
    },
    "G3": {
      "name": "内部审批",
      "prerequisites": ["G2通过"],
      "checklist": [
        "产品审批完成",
        "授信审批完成",
        "价格审批完成",
        "合规审批完成",
        "合同审批完成",
        "数据使用审批完成"
      ],
      "prohibitions": ["不得对客承诺额度、价格、收益和时效"]
    },
    "G4": {
      "name": "对客确认",
      "prerequisites": ["G3通过", "对客版已生成"],
      "checklist": [
        "客户理解价值",
        "客户理解条件",
        "客户理解责任",
        "客户理解下一步"
      ],
      "prohibitions": ["不得将'客户已收到'视为'客户已接受并实施'"]
    },
    "G5": {
      "name": "实施复盘",
      "prerequisites": ["G4通过"],
      "checklist": [
        "里程碑达成情况",
        "KPI完成情况",
        "证据收集情况",
        "问题记录情况",
        "复盘闭环"
      ],
      "prohibitions": ["不得把建议书交付视为经营任务完成"]
    }
  }
}
```
