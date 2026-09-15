#!/usr/bin/env python3
"""生成 GK-KE 首批受控指标定义（A2 / WP03 落地）。

依据：
  - 建议书 §6.4 MetricDefinition 最低 7 组合同
  - GK-KE-D3-DECISION-001（首批 19 项启用清单）
  - 现有 SIM.METRIC.CUSTOMER_AVG_DEPOSIT.json 的结构范式
  - 数据集 v2 的实际字段（scenario/seed/18_gk_ke_dataset_v2/observation/）

纪律：
  - 不覆写既有 SIM.METRIC.CUSTOMER_AVG_DEPOSIT.json（保真值 2983333.33）
  - 未获授权的指标不生成（I01-I12）
  - 无数据的指标不生成（M14/M15/M21/M29/M30 等）→ 记录为 NOT_ENABLED
"""
from __future__ import annotations

import json
import pathlib

DEFS = pathlib.Path("specs/gk-ke/v1/definitions")
DEFS.mkdir(parents=True, exist_ok=True)

COMMON = {
    "contractVersion": "gk-ke/v1",
    "simulationOnly": True,
    "status": "CANDIDATE",
    "authority": {
        "physicalArchive": "gits-cbanking",
        "semanticOwner": "metric_governance",
        "noProductionClaim": "本定义为 SIM 模拟口径，不构成杭银正式口径。",
    },
    "identity": {
        "owner": "SIM-METRIC-OWNER",
        "approvalRef": "GK-KE-D3-DECISION-001",
        "definitionHash": None,
        "hashNote": "hash 由 scripts/gk_ke_metric_definitions_check.py 按真实字节计算，禁止手工填写。",
    },
    "grain": {
        "entityType": "Customer",
        "dimensions": ["customerId"],
    },
    "time": {
        "intervalConvention": "LEFT_CLOSED_RIGHT_OPEN",
        "businessTimezone": "Asia/Shanghai",
        "calendarVersion": "SIM-CAL-1.0.0",
        "asOfPolicy": "SNAPSHOT_PINNED",
        "lateArrivalPolicy": "RESTATE_WITH_NEW_RUN",
    },
    "money": {
        "currencyPolicy": "CNY_ONLY",
        "unit": "CNY",
        "fxPolicy": "NONE",
        "fxDateRule": "NONE",
        "precision": 2,
    },
    "data": {
        "sourceProductRef": "SIM-DSV2",
        "sourceSnapshotPolicy": "SNAPSHOT_ID_REQUIRED",
        "mappingVersion": "2.0.0",
        "qualityChecks": ["SAME_PERIOD", "NO_NEGATIVE_WHERE_INVALID", "PERIOD_ALIGNED"],
        "availabilityDimensions": [
            "availability", "authorization", "coverage", "freshness", "retrievalOutcome",
        ],
        "valueStates": ["KNOWN", "UNKNOWN", "NOT_APPLICABLE"],
        "executionStates": ["SUCCESS", "PARTIAL", "FAILED", "NOT_RUN"],
        "notRunVsNoConflict": "未执行过的『无冲突』与检查成功且未发现冲突必须区分（§6.5）",
    },
    "runtime": {
        "parameterSchemaRef": "gk-ke/v1:SemanticRequest",
        "resultSchemaRef": "gk-ke/v1:SemanticResult",
        "permissionRef": "SIM-PERM-001",
        "maxRows": 1000,
        "timeoutMs": 30000,
        "whitelistCompilation": "服务端把 metricId 映射到批准模板；表名列名与 join 路径来自白名单。",
    },
    "provenance": {
        "registeredAt": "2026-09-12",
        "registeredBy": "tech_lead",
        "loop": "GK14-l4-0-capability-closure",
        "wp": "A2/WP03",
    },
}

# 首批 19 项（GK-KE-D3-DECISION-001）
METRICS = [
    # ---- A 类：可复算 ----
    ("M01", "REVENUE", "营业收入",
     "企业报表期间的收入；按报表确认基础读取",
     "报表期间营业收入合计",
     {"formula": "Σ[期间内各月营业收入]", "additivity": "ADDITIVE",
      "noSubstitution": "不得由账户入账替代（§6.2）"},
     "CNY", "数据集 v2 monthly_business_observation.revenue（24 期）"),
    ("M02", "NET_PROFIT", "净利润",
     "同一报表主体、期间的净利润",
     "报表期间净利润",
     {"formula": "Σ[期间内各月净利润]", "additivity": "ADDITIVE",
      "note": "与现金流联合看（§6.2）"},
     "CNY", "数据集 v2 monthly_business_observation.netProfit"),
    ("M03", "TOTAL_ASSETS", "资产总额",
     "企业报表期末资产",
     "期末资产合计",
     {"formula": "期末 totalAssets", "additivity": "NON_ADDITIVE",
      "note": "比率分母及规模；不是可用现金（§6.2）"},
     "CNY", "数据集 v2 monthly_business_observation.totalAssets"),
    ("M04", "TOTAL_LIABILITIES", "负债总额",
     "同一报表期末负债",
     "期末负债合计",
     {"formula": "期末 totalLiabilities", "additivity": "NON_ADDITIVE",
      "note": "包含经营性负债；不等于融资余额（§6.2）"},
     "CNY", "数据集 v2 monthly_business_observation.totalLiabilities"),
    ("M05", "DEBT_ASSET_RATIO", "资产负债率",
     "M04 / M03；资产≤0 时不返回普通比率",
     "负债总额 / 资产总额",
     {"numerator": "M04", "denominator": "M03", "additivity": "RATIO",
      "zeroDenominator": "返回 NOT_APPLICABLE 并给出原因",
      "note": "只按行业及资本结构解释，不设全行业统一准入线（§6.2）"},
     "RATIO", "由 M03/M04 推导"),
    ("M06", "OPERATING_CASH_FLOW", "经营活动现金流量净额",
     "同期现金流量表中经营活动净现金流",
     "经营活动现金流量净额",
     {"formula": "Σ[期间内各月 operatingCashFlow]", "additivity": "ADDITIVE",
      "noSubstitution": "不得由本行单一账户净流入替代（§6.2）"},
     "CNY", "数据集 v2 monthly_business_observation.operatingCashFlow"),
    ("M07", "ACCOUNTS_RECEIVABLE", "应收账款余额",
     "期初、期末分别读取；区分账面与净额",
     "期末应收账款余额",
     {"formula": "期末 accountsReceivable", "additivity": "NON_ADDITIVE",
      "note": "不得混入无关合同资产（§6.2）"},
     "CNY", "数据集 v2 monthly_business_observation.accountsReceivable"),
    ("M08", "AR_TURNOVER_DAYS", "应收账款周转天数",
     "平均应收 / 同期赊销收入 × 期间天数",
     "平均应收 / 同期赊销收入 × 期间天数",
     {"proxyPolicy": "无赊销收入时可另定义营收代理版，标 PROXY，不得同 ID 静默替换（§6.2）",
      "additivity": "NON_ADDITIVE"},
     "DAYS", "数据集 v2 monthly_business_observation.arTurnoverDays"),
    ("M09", "INVENTORY", "存货余额",
     "同口径期初、期末存货",
     "期末存货余额",
     {"formula": "期末 inventory", "additivity": "NON_ADDITIVE",
      "applicability": "制造、贸易常用；部分服务业不适用"},
     "CNY", "数据集 v2 monthly_business_observation.inventory"),
    ("M10", "INV_TURNOVER_DAYS", "存货周转天数",
     "平均存货 / 同期营业成本 × 期间天数",
     "平均存货 / 同期营业成本 × 期间天数",
     {"additivity": "NON_ADDITIVE",
      "failBehavior": "成本≤0 或期初缺失则不可计算（NOT_APPLICABLE）"},
     "DAYS", "数据集 v2 monthly_business_observation.invTurnoverDays"),
    ("M11", "ACCOUNTS_PAYABLE", "应付账款余额",
     "同口径期初、期末应付",
     "期末应付账款余额",
     {"formula": "期末 accountsPayable", "additivity": "NON_ADDITIVE"},
     "CNY", "数据集 v2 monthly_business_observation.accountsPayable"),
    ("M12", "AP_TURNOVER_DAYS", "应付账款周转天数",
     "平均应付 / 同期赊购金额 × 期间天数",
     "平均应付 / 同期赊购金额 × 期间天数",
     {"additivity": "NON_ADDITIVE",
      "proxyPolicy": "若只能用成本代理，另立定义并暴露限制（§6.2）"},
     "DAYS", "数据集 v2 monthly_business_observation.apTurnoverDays"),
    ("M13", "CASH_CONVERSION_CYCLE", "现金转换周期",
     "M08 + M10 − M12；三者使用兼容口径",
     "M08 + M10 − M12",
     {"numerator": "M08+M10-M12", "additivity": "NON_ADDITIVE",
      "negativeAllowed": "可为负；不能因负值直接判断有错误（§6.2）",
      "failBehavior": "任一组分 UNKNOWN → 整体 UNKNOWN，不得跳项计算"},
     "DAYS", "数据集 v2 monthly_business_observation.cashConversionCycle"),
    ("M16", "CUSTOMER_AVG_DEPOSIT", "客户日均存款",
     "先按账户日取唯一日终余额，再按客户日汇总，除以自然日数",
     "Σ[账户日终余额] / 自然日数",
     {"additivity": "SEMI_ADDITIVE", "distinctKey": "accountId+businessDate",
      "dedupPolicy": "DISTINCT",
      "noSumOfBalances": "不得把日终余额直接累计后称为存款总额",
      "noSumDistinctPatch": "禁止用 SUM(DISTINCT balance) 修补关联放大"},
     "CNY", "数据集 v2 daily_balances（180 行）；沿用既有批准的 30 天/CNY SIM 口径"),
    # ---- B 类：有数据但需声明覆盖 ----
    ("M17", "VISIBLE_BUSINESS_RECEIPTS", "本行可识别经营收款",
     "按批准分类器识别经营收款，排除冲正、自转、借款等",
     "Σ[合格经营收款]",
     {"additivity": "ADDITIVE", "scopeDeclaration": "MUST_DECLARE_OWN_BANK_VISIBILITY",
      "mustReturn": ["分类覆盖率", "未分类金额"],
      "noSubstitution": "不是企业总营收（§6.2）"},
     "CNY", "数据集 v2 daily_balances/transactions（须声明本行可见范围）"),
    ("M19", "PAYROLL_COVERAGE_HEADCOUNT", "本行代发覆盖人数",
     "当期成功代发的去重员工标识数",
     "COUNT(DISTINCT 员工标识)",
     {"additivity": "NON_ADDITIVE",
      "entityCheck": "与社保人数比较时需说明同主体、月和人群覆盖（§6.2）",
      "failBehavior": "集团/单体口径不一致 → 停止计算，转实体范围核对"},
     "PERSON", "数据集 v2 monthly_business_observation.socialInsuranceHeadcount（须核对主体）"),
    ("M20", "PAYROLL_AMOUNT", "本行代发金额",
     "成功代发金额减对应撤销；同一工资所属期",
     "Σ[成功代发] − Σ[撤销]",
     {"additivity": "ADDITIVE",
      "mustDeclare": ["奖金", "补发", "税前税后"]},
     "CNY", "数据集 v2（须注明工资所属期）"),
    # ---- C 类：事件型 ----
    ("M22", "OVERDUE_PRINCIPAL", "逾期本金余额",
     "源系统在截止时点认定的未偿逾期本金",
     "Σ[未偿逾期本金]",
     {"additivity": "NON_ADDITIVE",
      "noInference": "不由 LLM 推测（§6.2）",
      "mustLink": ["合同", "到期日", "事件状态"]},
     "CNY", "数据集 v2 event_records（设计为 E04 低占用逾期反例）"),
    ("M23", "OVERDUE_INTEREST", "欠息余额",
     "源系统在截止时点认定的未偿欠息",
     "Σ[未偿欠息]",
     {"additivity": "NON_ADDITIVE",
      "mustSeparateFrom": "逾期本金；不得合并为模糊风险分数（§6.2）"},
     "CNY", "数据集 v2 event_records"),
]

NOT_ENABLED = [
    ("M14", "可用现金余额", "NO_DATA", "数据集 v2 无冻结/质押标识"),
    ("M15", "未来 90 日到期债务本息", "NO_DATA", "无付款计划表"),
    ("M18", "本行可识别经营付款", "DEFERRED", "首批 R03 仅需收款侧"),
    ("M21", "授信使用率", "NO_DATA", "数据集 v2 无额度池结构；不影响 R08（逾期独立触发）"),
    ("M24", "前五大收款对手占比", "DEFERRED", "需对手解析，归 WP05/CAP-03；W-2 确认不应删指标"),
    ("M25", "前五大付款对手占比", "DEFERRED", "同上"),
    ("M26", "本行中间业务净收入", "OUT_OF_SCOPE", "内部经营分析，非客户风险事实"),
    ("M27", "票据发生额", "DEFERRED", "首批规则未涉及"),
    ("M28", "票据期末余额", "DEFERRED", "首批规则未涉及"),
    ("M29", "可见融资性负债余额", "NO_AUTHORIZATION", "需跨行授权，未证实"),
    ("M30", "可见对外担保责任余额", "NO_AUTHORIZATION", "需跨行授权，未证实"),
    ("I01-I12", "行业与条件扩展指标", "NO_AUTHORIZATION",
     "无数据可得性授权合同（§6.3）；数据集 v2 虽含外部观察层，但数据存在不等于已获授权（§2.4）"),
]


def main() -> int:
    written = 0
    for code, name, cn, definition, expr, compute, unit, source in METRICS:
        metric_id = f"SIM.METRIC.{name}"
        doc = json.loads(json.dumps(COMMON))  # deep copy
        doc["$comment"] = (
            f"A2/WP03 落地：{cn}（建议书 §6.2 编号 {code}）。"
            f"依据 GK-KE-D3-DECISION-001 首批启用清单。simulationOnly，非正式银行口径。"
        )
        doc["metricId"] = metric_id
        doc["version"] = "1.0.0"
        doc["proposalCode"] = code
        doc["definition"] = definition
        doc["identity"]["metricId"] = metric_id
        doc["identity"]["version"] = "1.0.0"
        doc["identity"]["definition"] = definition
        doc["grain"]["baseGrain"] = "customerId+periodStart"
        doc["grain"]["aggregationGrain"] = "CustomerPerPeriod"
        doc["compute"] = dict(compute)
        doc["compute"]["expressionText"] = expr
        doc["money"]["unit"] = unit
        doc["data"]["sourceRef"] = source
        doc["data"]["datasetVersion"] = "SIM-DSV2@2.0.0"
        doc["expectedColumn"] = name
        # 角色声明（依 OWNER-006）
        doc["roleInReconciliation"] = {
            "requiredInTask": True if code in {
                "M01", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13", "M22", "M23"} else False,
            "optionalInTask": False if code in {
                "M01", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13", "M22", "M23"} else True,
            "missingBehavior": (
                "COVERAGE_INSUFFICIENT" if code in {
                    "M01", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13", "M22", "M23"}
                else "UNKNOWN_WITH_EXPLANATION"),
            "supersedes": "SIM-RULE-FR-3 的固定 14 项要求（见 GK-KE-OWNER-006）",
        }
        (DEFS / f"{metric_id}.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written += 1

    # NOT_ENABLED 登记
    (DEFS / "_NOT_ENABLED_metrics.json").write_text(json.dumps({
        "$comment": "A2 交付物：明确**不启用**的指标及理由。依据 §14.2『以数据可得性合同为准』与 §2.4『数据存在不等于可用』。不得把未启用指标当作已启用。",
        "simulationOnly": True,
        "authority": "GK-KE-D3-DECISION-001",
        "items": [
            {"proposalCode": c, "name": n, "reason": r, "detail": d}
            for c, n, r, d in NOT_ENABLED
        ],
        "statement": "上述指标首批不启用。若下游需要，须先建立数据可得性授权或补齐数据，不得以推测值填充。"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"A2: 生成 {written} 项受控指标定义 → {DEFS}")
    print(f"    NOT_ENABLED 登记 {len(NOT_ENABLED)} 项")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
