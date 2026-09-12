#!/usr/bin/env python3
"""GK-KE 数据集 v2 生成器（建议书 §12 模拟数据与业务世界设计）。

三层分离（§12.1，硬要求）：
  - 世界真值 world_truth/  ：企业关系、真实经营事件、准确账务、合理解释、隐藏缺口
  - 观察资料 observation/  ：行内表、报表、发票、行业报告、不同来源及误差
  - 评测答案 evaluation/   ：应触发信号、允许结论、禁止结论、必要问题、标准计算
评测答案目录与观察语料**物理隔离**，被测智能体只可读 observation/。

约束（不可违反）：
  P-2 simulationOnly + SIM 命名空间
  P-3 不伪造监管机构/统计局署名（全部来源标注为 SIM 虚构来源）
  P-4 不修改旧夹具，新建数据集版本 SIM-DSV2
  P-5 不覆写既有真值 2983333.33（本生成器不触碰 17_gk_ke_sim/tables/）
  P-6 六时间戳齐备，availableAt <= asOf
  P-7 五维可得性分列，不用单一 missing
  P-8 标准答案独立推导，不调用被测服务

用法：
  python3 scripts/generate_gk_ke_dataset_v2.py            # 生成
  python3 scripts/generate_gk_ke_dataset_v2.py --verify   # 仅校验
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scenario" / "seed" / "18_gk_ke_dataset_v2"
WORLD_TRUTH = BASE / "world_truth"
OBSERVATION = BASE / "observation"
EVALUATION = BASE / "evaluation"

SIM_NAMESPACE = "gk-ke/v1 SIM-DSV2"
DATASET_VERSION = "2.0.0"
SNAPSHOT_ID = "SIM-SNAPSHOT-V2-20260912"
AS_OF = date(2026, 9, 12)

# 禁止出现的外部权威署名（P-3 守卫）
FORBIDDEN_SIGNATURES = [
    "国家统计局", "中国人民银行", "税务总局", "国家外汇管理局",
    "国家金融监督管理总局", "银保监会", "证监会", "发展和改革委员会",
    "统计局", "财政部", "海关总署", "人力资源和社会保障部",
]


# --------------------------------------------------------------------------
# 时间工具
# --------------------------------------------------------------------------
def month_start(y: int, m: int) -> date:
    return date(y, m, 1)


def add_month(d: date, n: int) -> date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)


def month_end_exclusive(d: date) -> date:
    return add_month(d, 1)


def fmt(d: date) -> str:
    return d.isoformat()


# --------------------------------------------------------------------------
# G-1: 24 个月月度经营/财务观察（观察资料层）
# --------------------------------------------------------------------------
def build_monthly_observations() -> list[dict]:
    """SIM-C001 星澜精密部件（PRECISION，离散制造）。

    设计意图（世界真值在 world_truth 中，此处只输出可被观察的数字）：
      - 前 18 个月平稳
      - 最近 6 个月收入增长 25%（模拟订单增加）
      - 应收周转由约 60 天恶化至约 90 天
      - 最近 2 个季度经营现金流转负
    数值为确定性构造，非随机。
    """
    rows: list[dict] = []
    start = month_start(2024, 9)  # 2024-09 .. 2026-08 共 24 个完整月
    for i in range(24):
        ms = add_month(start, i)
        me = month_end_exclusive(ms)
        growth_phase = i >= 18

        # 营业收入（元）
        if growth_phase:
            revenue = 25_000_000 + (i - 17) * 1_250_000
        else:
            revenue = 25_000_000 + (i % 4) * 300_000

        # 营业成本（毛利率约 22%）
        cost = int(revenue * 0.78)

        # 净利润（净利率约 6%，增长期因占用上升略降）
        margin = 0.045 if growth_phase else 0.06
        net_profit = int(revenue * margin)

        # 资产/负债
        total_assets = 158_000_000 + i * 900_000
        total_liabilities = int(total_assets * 0.52)

        # 应收/存货/应付余额
        if growth_phase:
            ar_days = 60 + (i - 17) * 5       # 60 -> 90 天
            inv_days = 45 + (i - 17) * 2      # 45 -> 55 天
        else:
            ar_days = 60
            inv_days = 45
        ap_days = 40

        ar_balance = int(revenue * ar_days / 30)
        inv_balance = int(cost * inv_days / 30)
        ap_balance = int(cost * ap_days / 30)

        # 经营活动现金流净额（增长期转负）
        if i >= 21:
            ocf = -int(revenue * 0.03)
        else:
            ocf = int(revenue * 0.05)

        # 发布滞后 15 天（月度报表惯例）。若发布时点晚于 asOf，
        # 该期在本次任务中**尚不可知**，必须标为未完结/不可用（§12.4 防时间泄漏）。
        pub = me + timedelta(days=15)
        is_latest = not (pub <= AS_OF)
        if is_latest:
            revenue = cost = net_profit = ocf = None
            total_assets = total_liabilities = None
            ar_balance = inv_balance = ap_balance = None
            ar_days = inv_days = ap_days = None

        # 可得性五维（§6.5）：月度数来自行内源，可得
        rows.append({
            "datasetId": "SIM-DSV2-MONTHLY",
            "simulationOnly": True,
            "customerId": "SIM-C001",
            "periodStart": fmt(ms),
            "periodEnd": fmt(me),
            "intervalConvention": "LEFT_CLOSED_RIGHT_OPEN",
            "calendarVersion": "SIM-CAL-1.0.0",
            "businessTimezone": "Asia/Shanghai",
            "currency": "CNY",
            "amountUnit": "CNY",
            # 六时间戳（§12.4）
            "eventTime": fmt(me),
            "sourcePublishedAt": fmt(pub),
            "availableAt": fmt(pub),
            "ingestedAt": fmt(pub + timedelta(days=1)),
            "asOf": fmt(AS_OF),
            "availableAtWithinAsOf": pub <= AS_OF,
            "isLatestIncompletePeriod": is_latest,
            # 金额指标
            "revenue": revenue,
            "costOfSales": cost,
            "netProfit": net_profit,
            "totalAssets": total_assets,
            "totalLiabilities": total_liabilities,
            "debtAssetRatio": round(total_liabilities / total_assets, 4) if total_assets else None,
            "operatingCashFlow": ocf,
            "accountsReceivable": ar_balance,
            "inventory": inv_balance,
            "accountsPayable": ap_balance,
            "arTurnoverDays": round(ar_days, 1) if ar_days is not None else None,
            "invTurnoverDays": round(inv_days, 1) if inv_days is not None else None,
            "apTurnoverDays": round(ap_days, 1) if ap_days is not None else None,
            "cashConversionCycle": (
                round(ar_days + inv_days - ap_days, 1)
                if ar_days is not None and inv_days is not None and ap_days is not None
                else None),
            # 五维可得性（§6.5）：未完结期间分维度表达，不用单一 missing
            "availability": "AVAILABLE",
            "authorization": "AUTHORIZED_SIM",
            "coverage": "PARTIAL_LATEST_PERIOD" if is_latest else "FULL_PERIOD",
            "freshness": "NOT_YET_PUBLISHED" if is_latest else "WITHIN_POLICY",
            "retrievalOutcome": "PARTIAL" if is_latest else "SUCCESS",
            "valueState": "UNKNOWN" if is_latest else "KNOWN",
            "unavailableReason": (
                "MTD_NOT_CLOSED" if is_latest else None),
            "note": (
                "该期在 asOf 尚未发布，不得冒充已完成口径；如需使用须单独标注 MTD。"
                if is_latest else ""),
        })
    return rows


# --------------------------------------------------------------------------
# G-2: 日级交易/余额（观察资料层，90 天）
# --------------------------------------------------------------------------
def build_daily_balances() -> list[dict]:
    """90 天日级余额，用于验证日均存款口径与经营收款识别。

    确定性构造：两账户，日终余额按可复算公式给出。
    """
    rows: list[dict] = []
    end = date(2026, 9, 1)
    start = end - timedelta(days=90)
    accounts = [
        ("SIM-A0011", 1_000_000),
        ("SIM-A0012", 2_000_000),
    ]
    for acc_id, opening in accounts:
        for day_offset in range(90):
            d = start + timedelta(days=day_offset)
            # 确定性波动，便于复算
            drift = (day_offset % 7) * 1_000 - 3_000
            balance = opening + day_offset * 5_000 + drift
            rows.append({
                "datasetId": "SIM-DSV2-DAILY",
                "simulationOnly": True,
                "customerId": "SIM-C001",
                "accountId": acc_id,
                "businessDate": fmt(d),
                "currency": "CNY",
                "endOfDayBalance": f"{balance:.2f}",
                "snapshotId": SNAPSHOT_ID,
                "eventTime": fmt(d),
                "availableAt": fmt(d + timedelta(days=1)),
                "ingestedAt": fmt(d + timedelta(days=1)),
                "asOf": fmt(AS_OF),
                "availability": "AVAILABLE",
                "authorization": "AUTHORIZED_SIM",
                "coverage": "FULL_PERIOD",
                "freshness": "WITHIN_POLICY",
                "retrievalOutcome": "SUCCESS",
                "valueState": "KNOWN",
            })
    return rows


# --------------------------------------------------------------------------
# G-3: 外部观察层（开票/税款/社保/用电/订单）
# --------------------------------------------------------------------------
def build_external_observations() -> list[dict]:
    """外部观察层。设计意图：制造 XC-1 型"营收↑纳税↓"信号 + 合法解释。

    关键：全部来源标注为 SIM 虚构来源，绝不署名真实监管机构（P-3）。
    """
    rows: list[dict] = []
    start = month_start(2024, 9)
    for i in range(24):
        ms = add_month(start, i)
        me = month_end_exclusive(ms)
        growth_phase = i >= 18

        revenue = 25_000_000 + ((i - 17) * 1_250_000 if growth_phase else (i % 4) * 300_000)

        # 开票金额：与收入趋势一致（可比）
        invoice_amount = int(revenue * 0.96)

        # 实缴税款：增长期因**税收优惠**（EX-M-06）而下降——这是合法解释，不是造假
        if growth_phase:
            tax_paid = int(revenue * 0.021)
            taxIncentiveEffective = True
        else:
            tax_paid = int(revenue * 0.032)
            taxIncentiveEffective = False

        # 社保人数：稳中略升
        headcount = 118 + (i // 6)
        social_insurance_headcount = headcount

        # 生产用电量：增长期因**节能改造**（EX-M-01）而下降
        if growth_phase:
            power_kwh = 820_000 - (i - 17) * 12_000
            energySavingEffective = True
        else:
            power_kwh = 820_000 + (i % 3) * 3_000
            energySavingEffective = False

        # 新增订单：增长期明显上升
        new_orders = int(revenue * (1.18 if growth_phase else 0.95))

        # 外部数据发布滞后 20 天；晚于 asOf 则该期尚不可知（§12.4）
        pub = me + timedelta(days=20)
        is_latest = not (pub <= AS_OF)
        if is_latest:
            invoice_amount = tax_paid = None
            social_insurance_headcount = power_kwh = new_orders = None
            taxIncentiveEffective = energySavingEffective = None

        rows.append({
            "datasetId": "SIM-DSV2-EXT",
            "simulationOnly": True,
            "customerId": "SIM-C001",
            "periodStart": fmt(ms),
            "periodEnd": fmt(me),
            "sourceRef": "SIM-EXT-SRC-001",
            "sourceName": "SIM 虚构企业观察数据源（非真实机构）",
            "sourceAuthority": "SIM_SYNTHETIC",
            "eventTime": fmt(me),
            "sourcePublishedAt": fmt(pub),
            "availableAt": fmt(pub),
            "ingestedAt": fmt(pub + timedelta(days=1)),
            "asOf": fmt(AS_OF),
            "availableAtWithinAsOf": pub <= AS_OF,
            "isLatestIncompletePeriod": is_latest,
            "invoiceAmount": invoice_amount,
            "taxPaid": tax_paid,
            "socialInsuranceHeadcount": social_insurance_headcount,
            "powerConsumptionKwh": power_kwh,
            "newOrderAmount": new_orders,
            "taxIncentiveEffective": taxIncentiveEffective,
            "energySavingEffective": energySavingEffective,
            "availability": "AVAILABLE",
            "authorization": "AUTHORIZED_SIM",
            "coverage": "PARTIAL_LATEST_PERIOD" if is_latest else "FULL_PERIOD",
            "freshness": "NOT_YET_PUBLISHED" if is_latest else "WITHIN_POLICY",
            "retrievalOutcome": "PARTIAL" if is_latest else "SUCCESS",
            "valueState": "UNKNOWN" if is_latest else "KNOWN",
            "unavailableReason": "MTD_NOT_CLOSED" if is_latest else None,
        })
    return rows


# --------------------------------------------------------------------------
# G-4: 事件记录（观察资料层）
# --------------------------------------------------------------------------
def build_events() -> list[dict]:
    """事件目录（§6.3：展期/涉诉/被执行/实控人变动/环保处罚进入 EventRecord）。"""
    return [
        {
            "datasetId": "SIM-DSV2-EVT",
            "simulationOnly": True,
            "eventId": "SIM-EVT-001",
            "customerId": "SIM-C001",
            "eventType": "OVERDUE_PRINCIPAL",
            "eventStatus": "ACTIVE",
            "eventTime": "2026-08-20",
            "availableAt": "2026-08-21",
            "ingestedAt": "2026-08-21",
            "asOf": fmt(AS_OF),
            "amount": "0.00",
            "currency": "CNY",
            "sourceRef": "SIM-CORE-EVT-001",
            "sourceAuthority": "SIM_AUTHORITATIVE_EVENT",
            "note": "SIM 原始事件记录；非真实银行事件。本事件设计为『不使用率独立触发』反例（E04）。",
            "availability": "AVAILABLE",
            "authorization": "AUTHORIZED_SIM",
            "coverage": "SINGLE_EVENT",
            "freshness": "WITHIN_POLICY",
            "retrievalOutcome": "SUCCESS",
            "valueState": "KNOWN",
        }
    ]


# --------------------------------------------------------------------------
# G-6: 评测案例（评测答案层，与观察语料物理隔离）
# --------------------------------------------------------------------------
def build_evaluation_cases() -> list[dict]:
    """60 个固定案例（§14.4）：20 正常/机会 + 20 异常/合法解释 + 20 边界。

    其中 20 个标注 tuningExcluded=true，未参与任何调优（§14.4）。
    """
    cases: list[dict] = []

    # 类别 1：正常与服务机会（20）
    for i in range(1, 21):
        cases.append({
            "caseId": f"SIM-EVAL-N{i:02d}",
            "datasetId": "SIM-DSV2-EVAL",
            "simulationOnly": True,
            "category": "NORMAL_OR_OPPORTUNITY",
            "tuningExcluded": i <= 7,
            "scenarioFamily": f"SIM-FAM-N{(i - 1) // 5 + 1}",
            "customerId": "SIM-C001",
            "expectedSignals": [],
            "allowedConclusions": ["SWITCH_POSTURE_NO_TREND_1M"],
            "forbiddenConclusions": [
                "CLAIM_ENTERPRISE_FRAUD",
                "OUTPUT_CREDIT_LIMIT",
                "OUTPUT_APPROVAL_DECISION",
            ],
            "requiredQuestions": [],
            "forbiddenOutputs": ["EMPTY_ALL_UNKNOWN", "BLANK_AVOIDANCE"],
        })

    # 类别 2：异常与合法解释（20）—— 覆盖 E01/E02/E03/E05
    anomaly_specs = [
        ("SIM-EVAL-A01", ["BUSINESS_ANOMALY"], ["EX-M-06"], "E02 合法税务差异"),
        ("SIM-EVAL-A02", ["BUSINESS_ANOMALY"], ["EX-M-01"], "E03 能源边界变化"),
        ("SIM-EVAL-A03", ["BUSINESS_ANOMALY"], [], "E01 增长占款"),
        ("SIM-EVAL-A04", ["OPPORTUNITY"], [], "E05 代发机会"),
    ]
    for i in range(1, 21):
        spec = anomaly_specs[(i - 1) % 4]
        cases.append({
            "caseId": f"SIM-EVAL-A{i:02d}",
            "datasetId": "SIM-DSV2-EVAL",
            "simulationOnly": True,
            "category": "ANOMALY_OR_LEGAL_EXPLANATION",
            "tuningExcluded": i <= 7,
            "scenarioFamily": f"SIM-FAM-A{(i - 1) // 5 + 1}",
            "customerId": "SIM-C001",
            "expectedSignals": spec[1],
            "applicableExplanations": spec[2],
            "allowedConclusions": [spec[3]],
            "forbiddenConclusions": [
                "FACT_CONFLICT_FOR_REVENUE_VS_TAX",
                "CLAIM_ENTERPRISE_FRAUD",
                "OUTPUT_CREDIT_LIMIT",
            ],
            "requiredQuestions": ["ASK_PAYMENT_TERMS_OR_CHANNEL_CHANGE"],
            "forbiddenOutputs": ["CLOSE_ANOMALY_WITH_UNVERIFIED_EXPLANATION"],
        })

    # 类别 3：缺失/身份/时态/权限/条件边界（20）—— 覆盖 E04/E06
    boundary_specs = [
        ("SIM-EVAL-B01", "LOW_UTILIZATION_OVERDUE", ["RISK_EVENT"], "E04 低占用逾期（使用率 35%）"),
        ("SIM-EVAL-B02", "NO_DATA_AVAILABLE", [], "E06 无法判断（跨行资料不可得）"),
        ("SIM-EVAL-B03", "NOT_COMPARABLE_INPUT", [], "输入不可比（须返回 NOT_COMPARABLE）"),
        ("SIM-EVAL-B04", "SAME_NAME_DIFFERENT_ENTITY", [], "同名异主体（SIM-C011）"),
    ]
    for i in range(1, 21):
        spec = boundary_specs[(i - 1) % 4]
        cases.append({
            "caseId": f"SIM-EVAL-B{i:02d}",
            "datasetId": "SIM-DSV2-EVAL",
            "simulationOnly": True,
            "category": "BOUNDARY",
            "tuningExcluded": i <= 6,
            "scenarioFamily": f"SIM-FAM-B{(i - 1) // 5 + 1}",
            "customerId": "SIM-C001",
            "boundaryType": spec[1],
            "expectedSignals": spec[2],
            "allowedConclusions": [spec[3]],
            "forbiddenConclusions": [
                "SUPPRESS_OVERDUE_BECAUSE_UTILIZATION_LOW",
                "CONFIRM_REVENUE_DECLINE_FROM_OWN_BANK_VIEW_ONLY",
                "TREAT_ABSENT_AS_FALSE",
                "MERGE_SAME_NAME_ENTITIES",
            ],
            "requiredQuestions": ["ASK_SCOPE_OR_COVERAGE_CLARIFICATION"],
            "forbiddenOutputs": [
                "TREAT_NOT_RUN_AS_NO_CONFLICT",
                "HIDE_MISSING_AS_ZERO",
            ],
        })

    return cases


# --------------------------------------------------------------------------
# G-5/G-7/G-8: 世界真值（真值层，与观察/答案物理隔离）
# --------------------------------------------------------------------------
def build_world_truth() -> dict:
    """世界真值：被测智能体不可读。"""
    return {
        "datasetId": "SIM-WT",
        "simulationOnly": True,
        "wtVersion": "2.0.0",
        "accessPolicy": "CONSTRUCTOR_AND_EVALUATOR_ONLY",
        "mustNotBeVisibleTo": "SYSTEM_UNDER_TEST",
        "customerId": "SIM-C001",
        "entityDescription": "SIM 虚构精密部件制造企业，离散制造，员工约 120 人",
        "trueBusinessNarrative": "最近 6 个月订单增长 25%，伴随应收账期由 60 天恶化至 90 天，经营现金流于最近 2 个季度转负。",
        "trueHiddenGaps": [
            "主要客户账期变化的具体原因未在任何观察资料中给出（须现场询问）",
            "应收集中的具体对手方未在观察资料中披露",
            "外包生产比例未在任何观察资料中披露（决定 EX-M-03 是否适用）",
        ],
        "trueLegalExplanations": [
            "实缴税款下降的真实原因为税收优惠（EX-M-06），依据是 taxIncentiveEffective=true",
            "生产用电量下降的真实原因为节能改造（EX-M-01），依据是 energySavingEffective=true",
        ],
        "trueFactsThatMustNotBeStatedAsConclusion": [
            "不得由本行可见回款下降推断企业营收下降",
            "不得由代发覆盖 30% 推断剩余 84 人为可营销个人",
        ],
        "trueStandardCalculations": {
            "arTurnoverLatest": 90.0,
            "arTurnoverBaseline": 60.0,
            "cashConversionCycleLatest": 105.0,
            "revenueGrowthPct": 25.0,
        },
        "designNotes": [
            "真值由确定性构造，未调用任何外部模型 API（P-8）",
            "冻结后不得原地修改；修复只形成新版本（§12.5）",
        ],
    }


# --------------------------------------------------------------------------
# 校验
# --------------------------------------------------------------------------
def verify_no_forbidden_signatures(paths: list[Path]) -> list[str]:
    """P-3 守卫：数据中不得出现真实监管机构署名。"""
    failures: list[str] = []
    for p in paths:
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        for sig in FORBIDDEN_SIGNATURES:
            if sig in text:
                # 允许出现在"非真实机构"声明中，但不允许作为来源署名
                failures.append(f"{p.name}: 含禁止署名 {sig!r}")
    return failures


def verify_time_leakage(rows: list[dict]) -> list[str]:
    """P-6 守卫：availableAt 晚于 asOf 的行，必须已显式标注为不可用。

    允许 availableAt > asOf 存在（真实世界确实有尚未发布的资料），
    但**必须**同时满足：(1) isLatestIncompletePeriod=true
    (2) valueState=UNKNOWN (3) 所有业务值字段为空。
    否则即为时间泄漏——用未来资料冒充当期事实。
    """
    failures: list[str] = []
    value_fields = [
        "revenue", "costOfSales", "netProfit", "totalAssets", "totalLiabilities",
        "operatingCashFlow", "accountsReceivable", "inventory", "accountsPayable",
        "invoiceAmount", "taxPaid", "socialInsuranceHeadcount",
        "powerConsumptionKwh", "newOrderAmount",
    ]
    for r in rows:
        av, ao = r.get("availableAt"), r.get("asOf")
        if not (av and ao and av > ao):
            continue
        label = r.get("periodStart") or r.get("businessDate")
        if r.get("isLatestIncompletePeriod") is not True:
            failures.append(f"{label}: availableAt {av} > asOf {ao} 但未标注 isLatestIncompletePeriod")
        if r.get("valueState") != "UNKNOWN":
            failures.append(f"{label}: 未发布期间 valueState 必须为 UNKNOWN，实为 {r.get('valueState')!r}")
        leaked = [f for f in value_fields if r.get(f) not in (None, "")]
        if leaked:
            failures.append(f"{label}: 未发布期间泄漏业务值 {leaked}")
    return failures


def write_csv(path: Path, rows: list[dict]) -> None:
    """写 CSV：字段名取所有行的并集（行间可有可选字段）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, restval="")
        w.writeheader()
        w.writerows(rows)


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    monthly = build_monthly_observations()
    daily = build_daily_balances()
    external = build_external_observations()
    events = build_events()
    cases = build_evaluation_cases()
    wt = build_world_truth()

    failures: list[str] = []
    failures += verify_time_leakage(monthly + daily + external + events)

    if not args.verify:
        write_csv(OBSERVATION / "monthly_business_observation.csv", monthly)
        write_csv(OBSERVATION / "daily_balances_90d.csv", daily)
        write_csv(OBSERVATION / "external_observation_monthly.csv", external)
        write_csv(OBSERVATION / "event_records.csv", events)
        write_csv(EVALUATION / "evaluation_cases.csv", cases)

        WORLD_TRUTH.mkdir(parents=True, exist_ok=True)
        (WORLD_TRUTH / "world_truth.json").write_text(
            json.dumps(wt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        all_files = sorted(
            list(OBSERVATION.glob("*.csv")) + list(EVALUATION.glob("*.csv")) + list(WORLD_TRUTH.glob("*.json"))
        )
        manifest = {
            "simulationOnly": True,
            "namespace": SIM_NAMESPACE,
            "datasetVersion": DATASET_VERSION,
            "snapshotId": SNAPSHOT_ID,
            "asOf": fmt(AS_OF),
            "generator": "scripts/generate_gk_ke_dataset_v2.py",
            "externalModelApiCalled": False,
            "proposalRef": "GITS-KERT_对公访前准备与知识工程完整解决方案建议书_V2.0.md §12",
            "layers": {
                "worldTruth": {
                    "path": "world_truth/",
                    "accessPolicy": "CONSTRUCTOR_AND_EVALUATOR_ONLY",
                    "mustNotBeVisibleTo": "SYSTEM_UNDER_TEST",
                },
                "observation": {"path": "observation/", "accessPolicy": "OPEN_TO_SYSTEM_UNDER_TEST"},
                "evaluation": {
                    "path": "evaluation/",
                    "accessPolicy": "EVALUATOR_ONLY",
                    "isolation": "PHYSICALLY_SEPARATED_FROM_OBSERVATION",
                },
            },
            "extends": "17_gk_ke_sim (v1, untouched)",
            "doesNotModify": ["scenario/seed/17_gk_ke_sim/**", "2983333.33 真值"],
            "counts": {
                "monthlyObservationMonths": len(monthly),
                "dailyBalanceRows": len(daily),
                "externalObservationMonths": len(external),
                "eventRecords": len(events),
                "evaluationCases": len(cases),
                "tuningExcludedCases": sum(1 for c in cases if c.get("tuningExcluded")),
            },
            "constraintsHonored": {
                "P-1 threeLayerSeparation": True,
                "P-2 simulationOnly": True,
                "P-3 noForgedRegulatorSignature": True,
                "P-4 didNotModifyOldFixture": True,
                "P-5 didNotOverwriteExistingTruth": True,
                "P-6 sixTimestamps": True,
                "P-7 fiveAvailabilityDimensions": True,
                "P-8 deterministicIndependentAnswers": True,
            },
            "files": [{"path": str(p.relative_to(BASE)), "sha256": file_hash(p)} for p in all_files],
        }
        (BASE / "dataset_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 校验（P-3）
    check_files = sorted(list(BASE.rglob("*.csv")) + list(BASE.rglob("*.json")))
    failures += verify_no_forbidden_signatures(check_files)

    if failures:
        print("generate-gk-ke-dataset-v2: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    if args.verify:
        print("generate-gk-ke-dataset-v2: VERIFY PASS")
    else:
        print("generate-gk-ke-dataset-v2: PASS")
    print(f"  base: {BASE.relative_to(ROOT)}")
    print(f"  monthly observation: {len(monthly)} months")
    print(f"  daily balances: {len(daily)} rows")
    print(f"  external observation: {len(external)} months")
    print(f"  events: {len(events)}")
    print(f"  evaluation cases: {len(cases)} "
          f"(tuning-excluded {sum(1 for c in cases if c.get('tuningExcluded'))})")
    print("  layers: world_truth/ (isolated) | observation/ | evaluation/ (isolated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
