#!/usr/bin/env python3
"""为指标定义补 recomputeKind：区分"求和"与"按公式复算"。

背景（QA 第二轮指出，属实）：
原 gk_ke_metric_definitions_check.py 的 recompute() 对**所有**指标一律求和，
但 RATIO/DAYS 型指标求和无意义（比率之和、天数之和都不表示任何东西）。
我在 A 层收口文档中仍写"14 项实测复算"，属**过度声称**。

本脚本按指标语义分类打标：
  SUM_FLOW        流量型：跨期求和有意义（营收、净利润、经营现金流）
  LATEST_STOCK    存量型：**只取期末值**，跨期求和无意义（资产、负债、应收、存货、应付）
  RATIO_DERIVED   比率型：须**由组分按公式逐期复算**并与夹具值比对（资产负债率）
  DAYS_DERIVED    天数型：须**由组分按公式逐期复算**（现金转换周期）
  DAYS_OBSERVED   天数型：公式所需输入（赊销/赊购）不可得，**只能取观测值**，
                  但须校验**内部一致性**（如 CCC = AR + INV − AP）
  AVG_FROM_DAILY  日均型：须按**去重后逐日平均**复算（日均存款）
"""
from __future__ import annotations

import json
import pathlib

DEFS = pathlib.Path("specs/gk-ke/v1/definitions")

KIND = {
    "SIM.METRIC.REVENUE": ("SUM_FLOW", {}),
    "SIM.METRIC.NET_PROFIT": ("SUM_FLOW", {}),
    "SIM.METRIC.OPERATING_CASH_FLOW": ("SUM_FLOW", {}),
    "SIM.METRIC.TOTAL_ASSETS": ("LATEST_STOCK", {}),
    "SIM.METRIC.TOTAL_LIABILITIES": ("LATEST_STOCK", {}),
    "SIM.METRIC.ACCOUNTS_RECEIVABLE": ("LATEST_STOCK", {}),
    "SIM.METRIC.INVENTORY": ("LATEST_STOCK", {}),
    "SIM.METRIC.ACCOUNTS_PAYABLE": ("LATEST_STOCK", {}),
    "SIM.METRIC.DEBT_ASSET_RATIO": ("RATIO_DERIVED", {
        "numerator": "totalLiabilities", "denominator": "totalAssets"}),
    "SIM.METRIC.CASH_CONVERSION_CYCLE": ("DAYS_DERIVED", {
        "components": {"+": ["arTurnoverDays", "invTurnoverDays"],
                       "-": ["apTurnoverDays"]}}),
    "SIM.METRIC.AR_TURNOVER_DAYS": ("DAYS_OBSERVED", {
        "formulaNeeds": "赊销收入（数据集未提供）→ 只能取观测值，不得冒充按公式复算"}),
    "SIM.METRIC.INV_TURNOVER_DAYS": ("DAYS_OBSERVED", {
        "formulaNeeds": "营业成本可算，但期初期末口径与账龄明细不可得 → 取观测值"}),
    "SIM.METRIC.AP_TURNOVER_DAYS": ("DAYS_OBSERVED", {
        "formulaNeeds": "赊购金额（数据集未提供）→ 只能取观测值"}),
    "SIM.METRIC.CUSTOMER_AVG_DEPOSIT": ("AVG_FROM_DAILY", {
        "note": "按账户日去重后再按客户日汇总，最后除以天数"}),
}


def main() -> int:
    updated = 0
    for metric_id, (kind, extra) in KIND.items():
        path = DEFS / f"{metric_id}.json"
        if not path.is_file():
            print(f"SKIP 缺失: {metric_id}")
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["recomputeKind"] = kind
        if extra:
            doc["recomputeSpec"] = extra
        # 清掉旧的求和证据，强制由新版核验器重算
        doc.pop("recomputeEvidence", None)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        updated += 1
        print(f"  {metric_id.split('.')[-1]:26s} -> {kind}")
    print(f"已更新 {updated} 项")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
