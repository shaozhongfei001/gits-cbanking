#!/usr/bin/env python3
"""生成 GK-KE 能力语义探针样例（U-B 配套）。

依据各 bank-front-* 技能真实的 references/output-schema.md 结构，
以及建议书 §9.4 要求（已知语义样例 + 证据引用要求 + 必须失败负例）。

所有样例均标注 limitations，不声称业务效果。
"""
from __future__ import annotations

import json
import pathlib

PROBES = pathlib.Path("specs/knowledge-architecture/registry/semantic-probes")
PROBES.mkdir(parents=True, exist_ok=True)

COMMON = {
    "probeVersion": "1.0.0",
    "probeMethod": "SEMANTIC_SAMPLE_NOT_HTTP_200",
    "evidenceFromDataset": {
        "datasetRef": "scenario/seed/18_gk_ke_dataset_v2",
        "observationLayerOnly": True,
        "worldTruthMustNotBeRead": True,
        "note": "探针只允许读取 observation/ 层，不得读取 world_truth/ 或 evaluation/。",
    },
    "limitations": [
        "本探针不证明该能力在真实数据上的业务准确性",
        "本探针不证明内容已发布或服务已就绪",
        "本探针只验证输入、结果、证据与失败状态的可观察结构",
        "KERT 侧输出 schema 为 markdown 提示而非机器可读 JSON Schema，结构校验能力受限",
    ],
    "dryRunVerified": True,
    "dryRunNote": (
        "条件齐备性已核验（provider 已解析、输出结构有原文依据、证据要求已声明、负例齐备）。"
        "真实调用结果须在具备 KERT 运行环境时复核；在此之前不得据本文件声称业务效果。"
    ),
}

SPECS = [
    {
        "capabilityId": "SIM-CAP-FACT-RECON",
        "providerId": "bank-front-fact-reconciliation",
        "skillIdDoc": "SK-FRONT-004",
        "input": {
            "customerId": "SIM-C001",
            "purpose": "FINANCE_VISIT_PREP",
            "asOf": "2026-09-12",
            "metricsRef": "scenario/seed/18_gk_ke_dataset_v2/observation/external_observation_monthly.csv",
        },
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "evidenceRefsMustResolveTo": "KE-FRONT-003-*",
            "mustContainIndicatorsWithStatus": ["verified", "pending", "missing"],
            "mustNotConflate": ["开票额", "实缴税款", "营业收入"],
            "mustNotClaim": ["CLAIM_ENTERPRISE_FRAUD", "OUTPUT_CREDIT_LIMIT", "OUTPUT_APPROVAL_DECISION"],
            "mustClassifySignalType": ["FACT_CONFLICT", "BUSINESS_ANOMALY", "RISK_EVENT", "OPPORTUNITY"],
            "note": "营收↑纳税↓ 必须归 BUSINESS_ANOMALY 并保留合法解释，不得归 FACT_CONFLICT。",
        },
        "mustFail": [
            {"caseId": "PROBE-FR-N1", "scenario": "跨主体比较", "input": {"customerId": "SIM-C011"},
             "expectedError": "ENTITY_MISMATCH", "rationale": "SIM-C011 与 SIM-C001 同名但不同主体，不得合并比较。"},
            {"caseId": "PROBE-FR-N2", "scenario": "不可比输入仍出冲突结论",
             "input": {"conceptPair": ["营业收入", "开票额"], "comparabilityChecked": False},
             "expectedError": "NOT_COMPARABLE", "rationale": "§7.2 步骤3：不能对齐则返回不可比较，而非无异常。"},
            {"caseId": "PROBE-FR-N3", "scenario": "缺层仍判通过", "input": {"coveredLayers": ["layer1"]},
             "expectedError": "COVERAGE_INSUFFICIENT", "rationale": "缺层不得静默通过；须报告覆盖不足。"},
            {"caseId": "PROBE-FR-N4", "scenario": "执行失败当作无冲突", "input": {"ruleRunStatus": "NOT_RUN"},
             "expectedError": "TREAT_NOT_RUN_AS_NO_CONFLICT",
             "rationale": "§6.5：未执行过的『无冲突』与检查成功且未发现冲突必须区分。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-EIGHT-DIM",
        "providerId": "bank-front-eight-dimension",
        "skillIdDoc": "SK-FRONT-003",
        "input": {"customerId": "SIM-C001", "industryCode": "PRECISION", "asOf": "2026-09-12"},
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "mustContainDimensionsWith": ["score", "label", "basis", "evidenceLevel"],
            "evidenceLevelEnum": ["明确依据", "部分依据", "证据不足-待核实"],
            "mustSupportNotAssessed": "维度无充分证据时输出 NOT_ASSESSED 而非填充标签",
            "mustNotClaim": ["INDUSTRY_INDEX_AS_FIRM_JUDGEMENT", "SINGLE_FIRM_DEFAULT_PROBABILITY"],
        },
        "mustFail": [
            {"caseId": "PROBE-8D-N1", "scenario": "强制八维都有评级", "input": {"evidenceAvailable": ["policy"]},
             "expectedError": "FORCED_FULL_RATING", "rationale": "§5.2：不能强制八维都有正负评级。"},
            {"caseId": "PROBE-8D-N2", "scenario": "以行业景气直接判定单一企业",
             "input": {"usesMacroIndexOnly": True}, "expectedError": "NO_FIRM_BRIDGE",
             "rationale": "§2.5：行业标签相同不代表企业承受相同影响。"},
            {"caseId": "PROBE-8D-N3", "scenario": "T-MARKET-001 输出无来源时间",
             "input": {"sourceIsAgent": True, "hasTimestamp": False}, "expectedError": "SOURCE_UNVERIFIABLE",
             "rationale": "§5.1：不能因来源是另一个 Agent 就视为权威研究结果。"},
            {"caseId": "PROBE-8D-N4", "scenario": "用电量套用于服务业", "input": {"industryCode": "SERVICE"},
             "expectedError": "NOT_APPLICABLE_REQUIRED",
             "rationale": "§5.3：用电量不能成为服务业、贸易类企业的必填经营活力指标。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-KYC-GAP",
        "providerId": "bank-front-kyc-gap-check",
        "skillIdDoc": "SK-FRONT-006",
        "input": {"customerId": "SIM-C001", "asOf": "2026-09-12", "purpose": "FINANCE_VISIT_PREP"},
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "mustContainGapsWith": ["gapId", "description", "trigger", "priority", "verifyScript"],
            "verifyScriptMustContain": ["factBasis", "question"],
            "questionQuality": ["可回答", "一次一事", "不预设结论", "不要求确认未证明数字", "说明所需资料"],
            "mustNotConflate": "业务访谈缺口检查 != 法定反洗钱 KYC 完成",
            "mustNotClaim": ["AML_KYC_COMPLETED", "OUTPUT_APPROVAL_DECISION"],
        },
        "mustFail": [
            {"caseId": "PROBE-KYC-N1", "scenario": "诱导性提问",
             "input": {"question": "贵司营收下降是因为客户流失吧？"}, "expectedError": "INDUCING_QUESTION",
             "rationale": "§8.4 不合格示例：预设结论。"},
            {"caseId": "PROBE-KYC-N2", "scenario": "要求确认未经证明的数字",
             "input": {"question": "确认一下你们9月营收是3125万对吧？"}, "expectedError": "UNVERIFIED_NUMBER_REQUEST",
             "rationale": "§8.4 T-4。"},
            {"caseId": "PROBE-KYC-N3", "scenario": "声称已完成反洗钱 KYC", "input": {"scope": "AML"},
             "expectedError": "OUT_OF_SCOPE_AML", "rationale": "§9.2：不得冒充法定反洗钱 KYC 完成。"},
            {"caseId": "PROBE-KYC-N4", "scenario": "失败当无缺口", "input": {"executionStatus": "FAILED"},
             "expectedError": "FAILED_AS_NO_GAP", "rationale": "§9.1 CAP-05：失败不当『无缺口』。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-COMMITMENT",
        "providerId": "bank-front-commitment-script",
        "skillIdDoc": "SK-FRONT-005",
        "input": {"customerId": "SIM-C001", "asOf": "2026-09-12"},
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "mustContainCommitmentsWith": ["commitmentId", "description", "promisor", "status",
                                           "promiseDate", "dueDate", "factReference"],
            "promisorEnum": ["client", "bank"],
            "statusEnum": ["completed", "pending", "overdue"],
            "mustSeparate": ["历史承诺", "沟通问题", "新行动建议"],
            "mustNotClaim": ["CONFIRM_BREACH_WITHOUT_EVIDENCE"],
        },
        "mustFail": [
            {"caseId": "PROBE-CM-N1", "scenario": "把客户未回复当作确认违约", "input": {"clientReplied": False},
             "expectedError": "UNREPLIED_AS_BREACH", "rationale": "§7.3 R09：把客户未回复与确认违约分开。"},
            {"caseId": "PROBE-CM-N2", "scenario": "承诺无事实引用", "input": {"factReference": None},
             "expectedError": "MISSING_FACT_REFERENCE",
             "rationale": "输出承诺须含事实引用，引用缺失处应标注待核实。"},
            {"caseId": "PROBE-CM-N3", "scenario": "混合历史承诺与新行动建议",
             "input": {"mergedWithoutLabel": True}, "expectedError": "UNCLASSIFIED_MIX",
             "rationale": "§9.2：须分开历史承诺、沟通问题和新行动建议。"},
            {"caseId": "PROBE-CM-N4", "scenario": "编造承诺", "input": {"sourceExists": False},
             "expectedError": "INVENTED_COMMITMENT", "rationale": "不得编造客户承诺。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-SUPPLY-CHAIN",
        "providerId": "bank-front-supply-chain-graph",
        "skillIdDoc": "SK-FRONT-002",
        "input": {"customerId": "SIM-C001", "asOf": "2026-09-12"},
        "expected": {
            "buildStatus": "complete",
            "evidenceRefsRequired": True,
            "mustContainNodesWith": ["id", "name", "layer", "type"],
            "layerEnum": ["supplier", "enterprise", "customer"],
            "mustNotClaimPaymentAsTrade": "付款关系不得冒充贸易关系",
            "mustNotMergeSameName": "同名主体不得合并",
            "concentrationRecomputable": True,
        },
        "mustFail": [
            {"caseId": "PROBE-SC-N1", "scenario": "同名主体合并",
             "input": {"entities": ["SIM-C001", "SIM-C011"]}, "expectedError": "SAME_NAME_MERGED",
             "rationale": "SIM-C011 与 SIM-C001 同名异主体。"},
            {"caseId": "PROBE-SC-N2", "scenario": "付款关系当贸易关系", "input": {"evidenceType": "PAYMENT_ONLY"},
             "expectedError": "PAYMENT_AS_TRADE", "rationale": "§9.1 CAP-03：支付关系不冒充贸易关系。"},
            {"caseId": "PROBE-SC-N3", "scenario": "LLM 抽取候选关系写成源事实",
             "input": {"relationSource": "LLM_EXTRACTION"}, "expectedError": "CANDIDATE_AS_FACT",
             "rationale": "§11.4：禁止把 LLM 抽取的候选关系自动写成源系统事实。"},
            {"caseId": "PROBE-SC-N4", "scenario": "声称多跳图能力", "input": {"hopDepth": 3},
             "expectedError": "MULTI_HOP_NOT_IMPLEMENTED",
             "rationale": "§9.1：普通融资访前可用一跳，不得声称已实现多跳图能力。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-PRODUCT-DOCTOR",
        "providerId": "bank-front-product-recommendation",
        "skillIdDoc": "SK-FRONT-007",
        "sharedProviderNote": "与 SIM-CAP-PRODUCT-CONDITION 共用 KERT 侧单一提供者；KERT 未拆分。",
        "input": {"customerId": "SIM-C001", "productId": "SIM-P001", "productVersion": "1.0.0"},
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "mustContainProductCard13": ["productId", "productVersion", "serviceType", "problemsSolved",
                                         "applicableCustomers", "businessPurpose", "requiredDocuments",
                                         "conditions", "exceptions", "mutex", "validity",
                                         "sourceLocator", "explanation", "publicationStatus"],
            "healthChecks": ["H-1", "H-2", "H-3", "H-4", "H-5", "H-6"],
            "mustNotClaim": ["CUSTOMER_ADMISSION_CONCLUSION", "OUTPUT_APPROVAL_DECISION"],
        },
        "mustFail": [
            {"caseId": "PROBE-PD-N1", "scenario": "跨版本拼接条件", "input": {"versions": ["1.0.0", "2.0.0"]},
             "expectedError": "VERSION_CONCATENATION", "rationale": "§8.1：产品名称相同但版本不同的条件不可拼接。"},
            {"caseId": "PROBE-PD-N2", "scenario": "模型补齐条款", "input": {"clauseMissing": True},
             "expectedError": "MODEL_FABRICATED_CLAUSE", "rationale": "不得由模型任意补齐产品条款。"},
            {"caseId": "PROBE-PD-N3", "scenario": "体检未通过仍进候选", "input": {"healthResult": "INCOMPLETE"},
             "expectedError": "UNHEALTHY_INTO_CANDIDATE",
             "rationale": "§8.1：体检未通过的产品不能进入可执行候选判断。"},
            {"caseId": "PROBE-PD-N4", "scenario": "对客解释超出原文", "input": {"explanationBeyondSource": True},
             "expectedError": "OVER_CLAIM", "rationale": "§8.1 H-6。"},
            {"caseId": "PROBE-PD-N5", "scenario": "以抽象规则ID代替条件内容",
             "input": {"conditions": "KI-RULE-002"}, "expectedError": "RULE_ID_AS_CONDITION",
             "rationale": "§15.4 WP04 完成定义：不以抽象规则 ID 代替条件内容。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-PRODUCT-CONDITION",
        "providerId": "bank-front-product-recommendation",
        "skillIdDoc": "SK-FRONT-007",
        "sharedProviderNote": "同上，提供者侧未拆分；体检门禁只能在 GK-KE 编排侧强制。",
        "input": {"customerId": "SIM-C001", "purpose": "WORKING_CAPITAL",
                  "admittedProducts": ["SIM-P001@1.0.0"]},
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "conditionResultEnum": ["TRUE", "FALSE", "UNKNOWN", "ERROR"],
            "mustNotTreatErrorAsFalse": True,
            "mustNotTreatAbsenceAsExistence": True,
            "rankingOrder": ["客户已确认目标", "业务适配", "证据充分性", "服务成本与实施难度", "本行经营价值"],
            "mustNotClaim": ["OUTPUT_CREDIT_LIMIT", "OUTPUT_APPROVAL_DECISION",
                             "OUTPUT_PRICING", "FORMAL_ADMISSION"],
        },
        "mustFail": [
            {"caseId": "PROBE-PC-N1", "scenario": "全未知判条件已满足", "input": {"allConditions": "UNKNOWN"},
             "expectedError": "ALL_UNKNOWN_AS_SATISFIED", "rationale": "§9.1 CAP-07：全未知不进入『条件已满足』。"},
            {"caseId": "PROBE-PC-N2", "scenario": "未见重复融资判 TRUE",
             "input": {"registryAccessible": False}, "expectedError": "ABSENCE_AS_PROOF",
             "rationale": "§8.3：没有登记/证据就不能把『未见重复融资』判 TRUE。"},
            {"caseId": "PROBE-PC-N3", "scenario": "执行错误当条件不满足",
             "input": {"ruleVersionMissing": True}, "expectedError": "ERROR_AS_FALSE",
             "rationale": "§8.2：ERROR 须停止该候选判断，不得当作 FALSE。"},
            {"caseId": "PROBE-PC-N4", "scenario": "事件过度阻断", "input": {"event": "OVERDUE"},
             "expectedError": "BLOCK_ALL_SERVICES",
             "rationale": "§8.3：不能因融资候选受限自动禁止所有结算或服务沟通。"},
            {"caseId": "PROBE-PC-N5", "scenario": "笼统互斥", "input": {"mutex": "A与B永远互斥"},
             "expectedError": "VAGUE_MUTEX", "rationale": "§8.3：互斥必须描述对象与条件。"},
            {"caseId": "PROBE-PC-N6", "scenario": "按本行中收排序",
             "input": {"primaryRankBasis": "BANK_INCOME"}, "expectedError": "RANK_BY_BANK_INCOME",
             "rationale": "§8.2：本行经营价值置于最后。"},
            {"caseId": "PROBE-PC-N7", "scenario": "凑数展示不适用产品", "input": {"candidateCount": 1},
             "expectedError": "PADDING_TO_THREE", "rationale": "§8.2：不要为凑齐三个候选展示不适用产品。"},
        ],
    },
    {
        "capabilityId": "SIM-CAP-REPORT-ASSEMBLE",
        "providerId": "bank-front-report-assembler",
        "skillIdDoc": "SK-FRONT-001",
        "input": {"customerId": "SIM-C001", "goal": "核实增长带来的资金占用", "asOf": "2026-09-12"},
        "expected": {
            "status": "complete",
            "evidenceRefsRequired": True,
            "mustContainBattleOrderFields": ["meta", "summary"],
            "mustBindEvidence": True,
            "internalVsCustomerViewSeparated": True,
            "mustExposeLimitations": True,
            "mustNotClaim": ["OUTPUT_CREDIT_LIMIT", "OUTPUT_APPROVAL_DECISION"],
        },
        "mustFail": [
            {"caseId": "PROBE-RA-N1", "scenario": "内部信息进入对客话术",
             "input": {"includeInternalIncome": True}, "expectedError": "INTERNAL_LEAK",
             "rationale": "§16.3-9：内部经营排序与受限风险资料不得进入客户可见材料。"},
            {"caseId": "PROBE-RA-N2", "scenario": "报告与锁定证据不对应",
             "input": {"evidenceBundleRef": None}, "expectedError": "UNBOUND_REPORT",
             "rationale": "§9.1 CAP-09：报告与锁定证据须一一对应。"},
            {"caseId": "PROBE-RA-N3", "scenario": "重大事件被 Top-K 截掉",
             "input": {"majorEvents": 1, "topK": 3}, "expectedError": "MAJOR_EVENT_TRUNCATED",
             "rationale": "§3.4：重大事件不能因 Top-K 限制被截掉。"},
            {"caseId": "PROBE-RA-N4", "scenario": "不说明建议何时不成立",
             "input": {"missingFalsification": True}, "expectedError": "NO_FALSIFICATION",
             "rationale": "§3.4：报告必须说明『什么情况下它不成立』。"},
        ],
    },
]

for spec in SPECS:
    doc = dict(COMMON)
    doc.update(spec)
    (PROBES / f"{spec['capabilityId']}.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written {spec['capabilityId']} mustFail={len(spec['mustFail'])}")
