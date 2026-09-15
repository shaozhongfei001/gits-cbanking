#!/usr/bin/env python3
"""修正指标定义的 expectedColumn / sourceRef 指向数据集 v2 的**真实列名**。

根因：_gen_metric_definitions.py 误把指标常量名（如 REVENUE）写入 expectedColumn，
而数据集实际列名是 camelCase（如 revenue）。门禁 gk_ke_metric_definitions_check.py
正确捕获了该错误（无不可复算值）。
"""
from __future__ import annotations

import json
import pathlib

DEFS = pathlib.Path("specs/gk-ke/v1/definitions")

MONTHLY = "scenario/seed/18_gk_ke_dataset_v2/observation/monthly_business_observation.csv"
DAILY = "scenario/seed/18_gk_ke_dataset_v2/observation/daily_balances_90d.csv"
EVENTS = "scenario/seed/18_gk_ke_dataset_v2/observation/event_records.csv"

# metricId -> (expectedColumn, sourceRef, note)
FIX = {
    "SIM.METRIC.REVENUE": ("revenue", MONTHLY),
    "SIM.METRIC.NET_PROFIT": ("netProfit", MONTHLY),
    "SIM.METRIC.TOTAL_ASSETS": ("totalAssets", MONTHLY),
    "SIM.METRIC.TOTAL_LIABILITIES": ("totalLiabilities", MONTHLY),
    "SIM.METRIC.DEBT_ASSET_RATIO": ("debtAssetRatio", MONTHLY),
    "SIM.METRIC.OPERATING_CASH_FLOW": ("operatingCashFlow", MONTHLY),
    "SIM.METRIC.ACCOUNTS_RECEIVABLE": ("accountsReceivable", MONTHLY),
    "SIM.METRIC.AR_TURNOVER_DAYS": ("arTurnoverDays", MONTHLY),
    "SIM.METRIC.INVENTORY": ("inventory", MONTHLY),
    "SIM.METRIC.INV_TURNOVER_DAYS": ("invTurnoverDays", MONTHLY),
    "SIM.METRIC.ACCOUNTS_PAYABLE": ("accountsPayable", MONTHLY),
    "SIM.METRIC.AP_TURNOVER_DAYS": ("apTurnoverDays", MONTHLY),
    "SIM.METRIC.CASH_CONVERSION_CYCLE": ("cashConversionCycle", MONTHLY),
    "SIM.METRIC.CUSTOMER_AVG_DEPOSIT": ("endOfDayBalance", DAILY),
    "SIM.METRIC.VISIBLE_BUSINESS_RECEIPTS": (None, DAILY),
    "SIM.METRIC.PAYROLL_COVERAGE_HEADCOUNT": (None, MONTHLY),
    "SIM.METRIC.PAYROLL_AMOUNT": (None, MONTHLY),
    "SIM.METRIC.OVERDUE_PRINCIPAL": (None, EVENTS),
    "SIM.METRIC.OVERDUE_INTEREST": (None, EVENTS),
}

# 无对应列者：如实说明为什么不可直接复算（不得编造列名）
NO_COLUMN_REASON = {
    "SIM.METRIC.VISIBLE_BUSINESS_RECEIPTS":
        "需按批准分类器识别经营收款，数据集 v2 未含分类器输出列；不得以余额或交易额替代（§6.2）。",
    "SIM.METRIC.PAYROLL_COVERAGE_HEADCOUNT":
        "数据集 v2 仅有 socialInsuranceHeadcount，**无本行代发覆盖人数**；二者为不同概念，不得互相替代（§6.2）。",
    "SIM.METRIC.PAYROLL_AMOUNT":
        "数据集 v2 无代发金额列；不得以社保人数推算。",
    "SIM.METRIC.OVERDUE_PRINCIPAL":
        "事件表目前无逾期本金金额字段（SIM-EVT-001 的 amount=0.00，设计为『低占用逾期』反例）；不可直接复算。",
    "SIM.METRIC.OVERDUE_INTEREST":
        "同上，事件表无欠息金额字段。",
}


def main() -> int:
    changed = 0
    for mid, (col, source) in FIX.items():
        path = DEFS / f"{mid}.json"
        if not path.is_file():
            print(f"SKIP 缺失: {mid}")
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["data"]["sourceRef"] = source
        if col:
            doc["expectedColumn"] = col
            doc.pop("recomputeBlockedReason", None)
        else:
            doc.pop("expectedColumn", None)
            doc["recomputeBlockedReason"] = NO_COLUMN_REASON.get(mid, "无对应列")
            doc["compute"]["recomputeStatus"] = "NOT_DIRECTLY_RECOMPUTABLE"
        doc["data"]["sourceColumnNote"] = (
            f"数据集 v2 实际列名: {col}" if col
            else "数据集 v2 无直接对应列，见 recomputeBlockedReason"
        )
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed += 1
    print(f"修正 {changed} 项")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
