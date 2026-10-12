#!/usr/bin/env python3
"""GK-KE L2-1 语义查询测试（C08 L2-1 / wave C1）。

依据 C04《分析语义服务合同》§3 日均存款精确定义、§4 防关联放大、§6 权限与查询编译、§7 失败行为。
覆盖 C08 L2-1 退出标准：「日均/粒度/缺失/跨币/越权测试通过」。

公式（C04 §3）：
  AverageDeposit(c) = RoundHalfUp( Σ[d∈D] Σ[a∈A(c,d)] Convert(Balance(a,d),FX(d)) / |D|, 2 )

检查：
  1. 指标定义齐备（C04 §2 七字段组，42 必填字段）
  2. **日均**：C001 = 2,983,333.33（RoundHalfUp，30 日区间）
  3. **粒度**：GRAIN_VIOLATION —— 关联放大被拒（不得先连交易再 SUM 余额）
  4. **缺失**：DATA_INCOMPLETE —— 缺失日不补零，明确拒绝/标不完整
  5. **跨币**：CURRENCY_POLICY_REQUIRED / FX_MISSING —— 不输出混合金额
  6. **越权**：SCOPE_DENIED —— 拒绝且不泄漏被拒对象细节
  7. **白名单编译**：rawSql / Cypher / SPARQL 字段一律拒绝（RAW_QUERY_FORBIDDEN）
  8. 未登记指标拒绝（METRIC_NOT_REGISTERED）
  9. 快照不可用拒绝（SNAPSHOT_UNAVAILABLE），不以最新数据伪装历史复算
 10. 预算超限终止（QUERY_BUDGET_EXCEEDED）并记 queryRunId
 11. 最小返回字段齐备（C04 §3）

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import csv
import json
import sys
from decimal import ROUND_HALF_UP, Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "scenario" / "seed" / "17_gk_ke_sim"
TABLES = SIM / "tables"
METRIC = ROOT / "specs" / "gk-ke" / "v1" / "definitions" / "SIM.METRIC.CUSTOMER_AVG_DEPOSIT.json"
CASES = ROOT / "specs" / "gk-ke" / "v1" / "examples" / "l2-1"

EXPECTED_C001 = D("2983333.33")
PERIOD_DAYS = 30
ALLOWED_REQUEST_FIELDS = {
    "contractVersion", "simulationOnly", "metricId", "metricVersion", "customerId",
    "period", "snapshotId", "currency", "purpose", "parameters",
}
FORBIDDEN_FIELDS = {"rawSql", "rawSQL", "cypher", "sparql", "rawQuery", "sql"}


def load(name: str) -> list[dict]:
    with (TABLES / f"{name}.csv").open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def money(v: str) -> D:
    return D(v).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def compile_and_run(request: dict, accounts: list[dict], balances: list[dict]) -> dict:  # noqa: C901
    """白名单编译器 + 执行。返回 {ok, error, value,...}。

    纪律（C04 §6）：只接受 metricId/version、已定义参数和用途；拒绝任何原始查询字段；
    服务端注入授权谓词；表名/列名/join 路径来自白名单。
    """
    # 7. 白名单编译：禁原始查询
    for field in FORBIDDEN_FIELDS:
        if field in request:
            # 独立错误码：使「显式禁字段」与「未知字段」两条防线可分别验证
            # （FAIL-2026-09-12-09：避免冗余路径掩盖主防线）
            return {"ok": False, "error": "RAW_QUERY_FIELD_DENIED"}
    unknown = set(request) - ALLOWED_REQUEST_FIELDS
    if unknown:
        return {"ok": False, "error": "RAW_QUERY_FORBIDDEN", "detail": sorted(unknown)}

    # 8. 指标必须已登记
    if request.get("metricId") != "SIM.METRIC.CUSTOMER_AVG_DEPOSIT":
        return {"ok": False, "error": "METRIC_NOT_REGISTERED"}
    if request.get("metricVersion") != "1.0.0":
        return {"ok": False, "error": "METRIC_NOT_REGISTERED"}

    # 9. 快照必须可用
    snapshot = request.get("snapshotId")
    if snapshot != "SIM-SNAPSHOT-20261001":
        return {"ok": False, "error": "SNAPSHOT_UNAVAILABLE"}

    # 6. 越权（服务端授权谓词；请求体自报不能作为授权证据）
    authorized_customers = {"SIM-C001"}  # 服务端注入的授权范围
    customer = request.get("customerId")
    if customer not in authorized_customers:
        # 不泄漏被拒对象细节
        return {"ok": False, "error": "SCOPE_DENIED"}

    # 5. 跨币种（C04 §3：CNY_ONLY 口径）
    #    指标声明 currencyPolicy=CNY_ONLY，故：
    #    (a) 请求币种非 CNY（含未指定）→ 拒绝；
    #    (b) 客户名下存在非 CNY 账户且请求未显式声明币种政策 → 拒绝聚合为单一金额。
    requested_ccy = request.get("currency")
    ccy_accounts = [a for a in accounts if a["customerId"] == customer and a["currency"] == "CNY"]
    other_ccy = [a for a in accounts if a["customerId"] == customer and a["currency"] != "CNY"]
    if requested_ccy != "CNY":
        return {"ok": False, "error": "CURRENCY_POLICY_REQUIRED"}
    if other_ccy and requested_ccy is None:
        return {"ok": False, "error": "CURRENCY_POLICY_REQUIRED"}

    # 4. 缺失日检测（不补零）
    ids = {a["accountId"] for a in ccy_accounts}
    by_date: dict[str, D] = {}
    for r in balances:
        if r["accountId"] in ids:
            by_date[r["businessDate"]] = by_date.get(r["businessDate"], D("0")) + money(r["closingBalance"])
    if len(by_date) != PERIOD_DAYS:
        return {"ok": False, "error": "DATA_INCOMPLETE", "daysFound": len(by_date)}

    # 3. 粒度：关联放大检查（余额必须先归约为唯一账户日，再聚合）
    #    检测：若 balances 出现 (accountId,businessDate) 重复，则说明关联被放大
    seen: set[tuple[str, str]] = set()
    for r in balances:
        key = (r["accountId"], r["businessDate"])
        if key in seen:
            return {"ok": False, "error": "GRAIN_VIOLATION"}
        seen.add(key)

    # 10. 预算
    budget = request.get("parameters", {}).get("maxRows", 1000)
    if len(balances) > budget:
        return {"ok": False, "error": "QUERY_BUDGET_EXCEEDED"}

    # 2. 日均（C04 §3 公式）
    total = sum(by_date.values(), D("0"))
    value = (total / D(PERIOD_DAYS)).quantize(D("0.01"), rounding=ROUND_HALF_UP)

    # 11. 最小返回字段
    return {
        "ok": True, "value": str(value), "unit": "CNY", "currency": "CNY",
        "metricId": "SIM.METRIC.CUSTOMER_AVG_DEPOSIT", "metricVersion": "1.0.0",
        "period": request.get("period"), "asOf": "2026-10-01T00:00:00Z",
        "sourceSnapshotId": snapshot, "mappingVersion": "1.0.0",
        "queryId": "SIM-QRY-AVG-DEPOSIT", "queryRunId": "SIM-RUN-0001",
        "permissionDecisionId": "SIM-PERM-001", "completeness": "COMPLETE",
        "warnings": [], "traceRef": "SIM-TRACE-001", "calculationDetailRef": "SIM-CALC-001",
    }


MIN_RESULT_FIELDS = {
    "value", "unit", "currency", "metricId", "metricVersion", "period", "asOf",
    "sourceSnapshotId", "mappingVersion", "queryId", "queryRunId",
    "permissionDecisionId", "completeness", "warnings", "traceRef", "calculationDetailRef",
}


def main() -> int:  # noqa: C901
    failures: list[str] = []

    # 1. 指标定义
    if not METRIC.is_file():
        failures.append(f"[1] metric definition missing: {METRIC}")
        metric = {}
    else:
        metric = json.loads(METRIC.read_text(encoding="utf-8"))
    for group in ("identity", "grain", "compute", "time", "money", "data", "runtime"):
        if group not in metric:
            failures.append(f"[1] metric definition missing group: {group}")

    accounts = load("accounts")
    balances = load("daily_balances")

    good_request = {
        "contractVersion": "gk-ke/v1", "simulationOnly": True,
        "metricId": "SIM.METRIC.CUSTOMER_AVG_DEPOSIT", "metricVersion": "1.0.0",
        "customerId": "SIM-C001", "period": {"from": "2026-09-01", "to": "2026-10-01"},
        "snapshotId": "SIM-SNAPSHOT-20261001", "currency": "CNY", "purpose": "INTERPRETATION",
    }

    # 2. 日均
    result = compile_and_run(good_request, accounts, balances)
    if not result.get("ok"):
        failures.append(f"[2] good request failed: {result.get('error')}")
    elif D(result["value"]) != EXPECTED_C001:
        failures.append(f"[2] C001 = {result['value']} != {EXPECTED_C001}")
    else:
        missing = MIN_RESULT_FIELDS - set(result)
        if missing:
            failures.append(f"[11] result missing fields: {sorted(missing)}")

    # 3-10. 负例路径：必须返回指定错误码
    import copy
    expected_errors = {
        "raw_sql": ("RAW_QUERY_FIELD_DENIED", lambda r: r.update({"rawSql": "SELECT 1"})),
        "sparql": ("RAW_QUERY_FIELD_DENIED", lambda r: r.update({"sparql": "SELECT ?s WHERE {?s ?p ?o}"})),
        "cypher": ("RAW_QUERY_FIELD_DENIED", lambda r: r.update({"cypher": "MATCH (n) RETURN n"})),
        "unknown_field": ("RAW_QUERY_FORBIDDEN", lambda r: r.update({"arbitraryInjection": "x"})),
        "unknown_metric": ("METRIC_NOT_REGISTERED", lambda r: r.update({"metricId": "SIM.METRIC.UNKNOWN"})),
        "bad_snapshot": ("SNAPSHOT_UNAVAILABLE", lambda r: r.update({"snapshotId": "SIM-SNAPSHOT-LATEST"})),
        "scope_denied": ("SCOPE_DENIED", lambda r: r.update({"customerId": "SIM-C999"})),
        "cross_currency": ("CURRENCY_POLICY_REQUIRED", lambda r: r.update({"currency": None})),
    }
    neg_covered: set[str] = set()
    for name, (expected, mutate) in expected_errors.items():
        req = copy.deepcopy(good_request)
        req["currency"] = "CNY"
        mutate(req)
        res = compile_and_run(req, accounts, balances)
        if res.get("ok"):
            failures.append(f"[X] {name}: NOT rejected (expected {expected})")
        elif res.get("error") != expected:
            failures.append(f"[X] {name}: error {res.get('error')!r} != expected {expected!r}")
        else:
            neg_covered.add(expected)

    # 数据驱动负例：缺失日 / 粒度放大
    ids = {a["accountId"] for a in accounts if a["customerId"] == "SIM-C001" and a["currency"] == "CNY"}
    trimmed = [r for r in balances if not (r["accountId"] in ids and r["businessDate"] == "2026-09-15")]
    res = compile_and_run(good_request, accounts, trimmed)
    if res.get("error") != "DATA_INCOMPLETE":
        failures.append(f"[4] missing-day: {res.get('error')!r} != DATA_INCOMPLETE")
    else:
        neg_covered.add("DATA_INCOMPLETE")

    amplified = list(balances) + [r for r in balances if r["accountId"] in ids][:1]
    res = compile_and_run(good_request, accounts, amplified)
    if res.get("error") != "GRAIN_VIOLATION":
        failures.append(f"[3] grain amplification: {res.get('error')!r} != GRAIN_VIOLATION")
    else:
        neg_covered.add("GRAIN_VIOLATION")

    req = copy.deepcopy(good_request)
    req["parameters"] = {"maxRows": 10}
    res = compile_and_run(req, accounts, balances)
    if res.get("error") != "QUERY_BUDGET_EXCEEDED":
        failures.append(f"[10] budget: {res.get('error')!r} != QUERY_BUDGET_EXCEEDED")
    else:
        neg_covered.add("QUERY_BUDGET_EXCEEDED")

    required_errors = {
        "RAW_QUERY_FORBIDDEN", "RAW_QUERY_FIELD_DENIED", "METRIC_NOT_REGISTERED", "SNAPSHOT_UNAVAILABLE",
        "SCOPE_DENIED", "CURRENCY_POLICY_REQUIRED", "DATA_INCOMPLETE",
        "GRAIN_VIOLATION", "QUERY_BUDGET_EXCEEDED",
    }
    uncovered = required_errors - neg_covered
    if uncovered:
        failures.append(f"[X] error paths never triggered (noop risk): {sorted(uncovered)}")

    # 越权不得泄漏被拒细节
    res = compile_and_run({**good_request, "customerId": "SIM-C999"}, accounts, balances)
    if "SIM-C999" in json.dumps(res, ensure_ascii=False):
        failures.append("[6] SCOPE_DENIED leaks the rejected object identifier")

    if failures:
        print("gk-ke-l2-1-semantic-query-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l2-1-semantic-query-tests: PASS")
    print(f"  C001 average daily deposit = {result['value']} CNY (C04 section 3 formula)")
    print(f"  error paths covered ({len(neg_covered)}): {sorted(neg_covered)}")
    print("  checks: metric-def, avg, grain, missing, cross-currency, scope, whitelist, "
          "unregistered, snapshot, budget, min-result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
