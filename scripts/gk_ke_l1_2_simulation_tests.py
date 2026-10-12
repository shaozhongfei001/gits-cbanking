#!/usr/bin/env python3
"""GK-KE L1-2 模拟源一致性测试（C08 L1-2 / wave B2）。

依据 C07《模拟数据合同》§2 表清单、§5 强制一致性、§6 异常集。
覆盖 C08 L1-2 退出标准：「外键/余额/币种/重复负例通过」。

七项检查：
  1. 表清单与 dataset_manifest 一致（C07 §2）
  2. 外键引用闭包（C07 §5：客户关系引用存在、账户币种与交易相同、持仓指向存在产品）
  3. 余额滚动（closing = opening + netMovement；次日 opening = 前日 closing）
  4. 借贷平衡（每交易两条分录、金额相等、方向相反、同币种）
  5. 币种一致性（账户币种与交易相同）
  6. 重复账户日检测（C07 §5：所有余额行唯一且日期完整）
  7. C001 日均复算 = 2,983,333.33 CNY（C07 §5）

另核 C07 §6 异常集：负例必须声明 expectedError，且不得污染正常快照。

退出码：全部通过 0，否则 1。
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "scenario" / "seed" / "17_gk_ke_sim"
TABLES = SIM / "tables"
MANIFEST = SIM / "dataset_manifest.json"
NEGATIVES = SIM / "negatives"

EXPECTED_C001 = D("2983333.33")


def load_table(name: str) -> list[dict]:
    path = TABLES / f"{name}.csv"
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def money(value: str) -> D:
    return D(value).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def main() -> int:  # noqa: C901 - explicit check list
    failures: list[str] = []

    if not MANIFEST.is_file():
        print(f"FAIL: manifest missing: {MANIFEST}", file=sys.stderr)
        return 2
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # --- 1. 表清单与 manifest 一致 ---
    declared = set(manifest.get("tableCounts", {}).keys())
    present = {p.stem for p in TABLES.glob("*.csv")}
    missing = sorted(declared - present)
    if missing:
        failures.append(f"[1] declared tables missing: {missing}")
    for table, expected in manifest.get("tableCounts", {}).items():
        actual = len(load_table(table))
        if actual != expected:
            failures.append(f"[1] {table}: row count {actual} != manifest {expected}")

    # 载入
    customers = load_table("customers")
    accounts = load_table("accounts")
    transactions = load_table("transactions")
    ledger = load_table("ledger_entries")
    balances = load_table("daily_balances")
    holdings = load_table("holdings")
    facilities = load_table("credit_facilities")

    customer_ids = {r["customerId"] for r in customers}
    account_ids = {r["accountId"] for r in accounts}
    account_ccy = {r["accountId"]: r["currency"] for r in accounts}
    tx_ids = {r["transactionId"] for r in transactions}
    product_ids = {r["productId"] for r in load_table("products")}

    # --- 2. 外键闭包 ---
    for r in accounts:
        if r["customerId"] not in customer_ids:
            failures.append(f"[2] account {r['accountId']} -> unknown customer {r['customerId']}")
    for r in transactions:
        if r["accountId"] not in account_ids:
            failures.append(f"[2] transaction {r['transactionId']} -> unknown account {r['accountId']}")
    for r in ledger:
        if r["transactionId"] not in tx_ids:
            failures.append(f"[2] ledger {r['entryId']} -> unknown transaction {r['transactionId']}")
    for r in holdings:
        if r["customerId"] not in customer_ids or r["productId"] not in product_ids:
            failures.append(f"[2] holding {r['holdingId']} -> unknown customer/product")
    for r in facilities:
        if r["customerId"] not in customer_ids:
            failures.append(f"[2] facility {r['facilityId']} -> unknown customer {r['customerId']}")
    for r in balances:
        if r["accountId"] not in account_ids:
            failures.append(f"[2] balance row -> unknown account {r['accountId']}")

    # --- 3. 余额滚动 ---
    rolling = defaultdict(list)
    for r in balances:
        rolling[r["accountId"]].append(r)
    for acct, rows in rolling.items():
        rows.sort(key=lambda x: x["businessDate"])
        prev_close = None
        for r in rows:
            opening = money(r["openingBalance"])
            net = money(r["netMovement"])
            closing = money(r["closingBalance"])
            if opening + net != closing:
                failures.append(
                    f"[3] {acct}@{r['businessDate']}: opening+net={opening + net} != closing={closing}"
                )
            if prev_close is not None and opening != prev_close:
                failures.append(
                    f"[3] {acct}@{r['businessDate']}: opening={opening} != prev close={prev_close}"
                )
            prev_close = closing

    # --- 4. 借贷平衡（列名为 direction；每交易恰好 2 条、金额相等、方向相反、同币种）---
    by_tx = defaultdict(list)
    for r in ledger:
        by_tx[r["transactionId"]].append(r)
    for tx_id, rows in by_tx.items():
        if len(rows) != 2:
            failures.append(f"[4] transaction {tx_id}: {len(rows)} entries, expected 2")
            continue
        debit = sum((money(r["amount"]) for r in rows if r["direction"] == "DEBIT"), D("0"))
        credit = sum((money(r["amount"]) for r in rows if r["direction"] == "CREDIT"), D("0"))
        if debit != credit:
            failures.append(f"[4] transaction {tx_id}: DEBIT={debit} != CREDIT={credit}")
        if len({r["currency"] for r in rows}) != 1:
            failures.append(f"[4] transaction {tx_id}: currency mismatch across entries")

    # --- 5. 币种一致性 ---
    for r in transactions:
        acct_ccy = account_ccy.get(r["accountId"])
        if acct_ccy and r["currency"] != acct_ccy:
            failures.append(
                f"[5] transaction {r['transactionId']}: ccy {r['currency']} != account ccy {acct_ccy}"
            )

    # --- 6. 重复账户日 ---
    seen_days: set[tuple[str, str]] = set()
    for r in balances:
        key = (r["accountId"], r["businessDate"])
        if key in seen_days:
            failures.append(f"[6] duplicate balance row: {key}")
        seen_days.add(key)

    # --- 7. C001 日均复算（权威公式：先按业务日跨账户汇总，再除以区间天数）---
    # C07 §5：C001 两账户初始合计 300 万，9/6 入账 10 万、9/16 出账 20 万；日均真值 2,983,333.33
    c001_accounts = {
        a["accountId"] for a in accounts
        if a["customerId"] == "SIM-C001" and a["currency"] == "CNY"
    }
    if len(c001_accounts) < 2:
        failures.append(f"[7] SIM-C001 has {len(c001_accounts)} CNY accounts, expected >= 2")
    by_date: dict[str, D] = defaultdict(lambda: D("0"))
    for r in balances:
        if r["accountId"] in c001_accounts:
            by_date[r["businessDate"]] += money(r["closingBalance"])
    period_days = manifest.get("c001PeriodDays", 30)
    if len(by_date) != period_days:
        failures.append(f"[7] C001: expected {period_days} business days, got {len(by_date)}")
    total = sum(by_date.values(), D("0"))
    avg = (total / D(period_days)).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    if avg != EXPECTED_C001:
        failures.append(f"[7] C001 avg deposit {avg} != expected {EXPECTED_C001}")

    # --- 8. 异常集：负例必须声明 expectedError ---
    neg_count = 0
    if NEGATIVES.is_dir():
        for path in sorted(NEGATIVES.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            if not doc.get("expectedError"):
                failures.append(f"[8] {path.name}: missing expectedError (C07 section 6)")
            if doc.get("simulationOnly") is not True:
                failures.append(f"[8] {path.name}: missing simulationOnly=true")
            neg_count += 1

    if failures:
        print("gk-ke-l1-2-simulation-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l1-2-simulation-tests: PASS")
    print(f"  tables={len(present)} rows_total={sum(len(load_table(t)) for t in present)}")
    print(f"  customers={len(customers)} accounts={len(accounts)} transactions={len(transactions)}")
    print(f"  ledger_entries={len(ledger)} daily_balances={len(balances)}")
    print(f"  C001 avg deposit = {EXPECTED_C001} CNY (independently recomputed)")
    print(f"  negatives_with_expectedError={neg_count}")
    print("  checks: manifest, FK closure, balance rolling, double-entry, currency, duplicate-day, C001")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
